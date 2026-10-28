"""End-to-end assessments: the three acceptance cases and failure modes that must stay unresolved."""

import json
import unittest
from datetime import datetime, timezone
from unittest import mock

from claim_agent.llm import LLMConfig, OpenRouterClient
from claim_agent.orchestrator import assess_claim
from claim_agent.report import explanation_facts
from claim_agent.render import render_report
from helpers import (
    STORE,
    store_with_claim_changes,
    store_with_document_fact,
    store_with_member_changes,
    store_without_balances,
    store_without_policy,
)

CLOCK = lambda: datetime(2026, 10, 28, 9, 0, tzinfo=timezone.utc)  # noqa: E731


def assess(claim_id, store=STORE, client=None):
    return assess_claim(claim_id, store, client, clock=CLOCK)


def events(assessment):
    return [(e.event, e.name, e.status) for e in assessment.audit.events]


def row(report, document_type):
    return next(r for r in report["document_review"]["rows"] if r["document_type"] == document_type and r["required"] != "N")


class AcceptanceCasesTest(unittest.TestCase):
    def test_case_1_straightforward_approval(self):
        a = assess("CLM-APP-001")
        r = a.report
        self.assertEqual(r["recommendation"]["outcome"], "APPROVE")
        self.assertEqual(r["assessment_status"], "READY_FOR_AUTHORIZATION")
        self.assertEqual(r["recommendation"]["recommended_payable"], "180.00")
        calc = r["benefit_calculation"]
        self.assertEqual(
            (calc["submitted"], calc["copay"], calc["insurer_payable"], calc["member_responsibility"], calc["remaining_limit_after"]),
            ("200.00", "20.00", "180.00", "20.00", "620.00"),
        )
        self.assertEqual(r["medical_necessity"]["result"], "SUPPORTED")
        self.assertEqual(r["document_review"]["conclusion"], "COMPLETE")
        self.assertEqual(r["policy_verification"]["conclusion"], "ELIGIBLE")
        self.assertEqual(r["validation"]["status"], "PASS")
        self.assertEqual(r["human_review"]["authorization_status"], "PENDING")

    def test_case_2_rejection_under_exclusion(self):
        r = assess("CLM-REJ-001").report
        self.assertEqual(r["recommendation"]["outcome"], "REJECT")
        self.assertEqual(r["medical_necessity"]["result"], "NOT_SUPPORTED")
        calc = r["benefit_calculation"]
        self.assertEqual((calc["excluded"], calc["insurer_payable"], calc["member_responsibility"]), ("2000.00", "0.00", "2000.00"))
        exclusion = next(c for c in r["policy_verification"]["checks"] if c["check"] == "exclusions")
        self.assertEqual((exclusion["result"], exclusion["clause_ids"]), ("FAIL", ["REJ-6.4"]))
        cited = {c["clause_id"] for c in r["policy_citations"]["citations"]}
        self.assertIn("REJ-6.4", cited)
        self.assertIn("denial review", r["recommendation"]["next_action"])
        self.assertEqual(r["validation"]["status"], "PASS")

    def test_case_3_request_more_information(self):
        a = assess("CLM-RFI-001")
        r = a.report
        self.assertEqual(r["recommendation"]["outcome"], "REQUEST_MORE_INFO")
        self.assertEqual(r["assessment_status"], "PENDING_INFORMATION")
        self.assertEqual(row(r, "MEDICAL_REPORT")["status"], "MISSING")
        mismatch = next(x for x in r["document_review"]["rows"] if x["document_id"] == "I-D4")
        self.assertEqual((mismatch["submitted_type"], mismatch["detected_type"]), ("MEDICAL_REPORT", "APPOINTMENT_CONFIRMATION"))
        request = r["recommendation"]["information_requests"][0]
        self.assertEqual(
            (request["required_item"], request["requirement_id"], request["policy_clause_id"], request["status"]),
            ("MEDICAL_REPORT", "OP-REQ-4", "RFI-7.2", "OPEN"),
        )
        self.assertTrue(request["reassessment_trigger"])
        self.assertEqual(r["medical_necessity"]["result"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(r["benefit_calculation"]["status"], "PENDING")
        self.assertIsNone(r["benefit_calculation"]["insurer_payable"])
        self.assertIsNone(r["recommendation"]["recommended_payable"])
        self.assertIn(("SKIPPED_STEP", "checkMedicalNecessity", "SKIPPED"), events(a))
        self.assertIn(("SKIPPED_STEP", "calculateBenefit", "SKIPPED"), events(a))
        self.assertEqual(r["validation"]["status"], "PASS")

    def test_tool_calls_run_in_plan_order_with_versions(self):
        a = assess("CLM-APP-001")
        names = [e.name for e in a.audit.events]
        self.assertEqual(names, ["verifyDocument"] * 4 + [
            "documentReview", "lookupPolicy", "checkMedicalNecessity", "calculateBenefit", "decide", "validateReport",
        ])
        for e in a.audit.events:
            self.assertEqual(e.status, "OK")
            self.assertTrue(e.tool_version)
            self.assertEqual(e.context_version, a.context.context_version)
            self.assertIsNotNone(e.output)

    def test_log_records_review_decision_and_validation(self):
        a = assess("CLM-RFI-001")
        steps = {e.name: e for e in a.audit.events if e.event == "STEP"}
        self.assertEqual(steps["documentReview"].output["conclusion"], "UNRESOLVED_ITEMS")
        self.assertEqual(steps["decide"].output["outcome"], "REQUEST_MORE_INFO")
        self.assertEqual(steps["decide"].output["information_requests"], ["REQ-CLM-RFI-001-1"])
        self.assertEqual((steps["validateReport"].status, steps["validateReport"].output["status"]), ("OK", "PASS"))

    def test_skip_reasons_name_the_missing_inputs(self):
        a = assess("CLM-RFI-001")
        skipped = {e.name: e.reason for e in a.audit.events if e.event == "SKIPPED_STEP"}
        self.assertEqual(
            skipped["checkMedicalNecessity"],
            "No verified MEDICAL_REPORT: OP-REQ-4 MISSING (I-D4 is APPOINTMENT_CONFIRMATION).",
        )
        self.assertEqual(skipped["calculateBenefit"], "Blocked by: OP-REQ-4 MEDICAL_REPORT MISSING; medical necessity INSUFFICIENT_EVIDENCE.")
        self.assertEqual(a.report["medical_necessity"]["outstanding_concerns"], [skipped["checkMedicalNecessity"]])
        self.assertEqual(a.report["benefit_calculation"]["pending_reasons"], [skipped["calculateBenefit"]])

    def test_every_reason_traces_to_evidence_and_citation(self):
        for claim_id in ("CLM-APP-001", "CLM-REJ-001", "CLM-RFI-001"):
            r = assess(claim_id).report
            citations = {c["citation_id"] for c in r["policy_citations"]["citations"]}
            for reason in r["recommendation"]["reasons"]:
                with self.subTest(claim=claim_id, reason=reason["finding"][:40]):
                    self.assertTrue(reason["evidence"])
                    self.assertTrue(reason["citation_ids"])
                    self.assertTrue(set(reason["citation_ids"]) <= citations)

    def test_report_records_policyholder(self):
        r = assess("CLM-REJ-001").report
        self.assertEqual(r["metadata"]["policyholder"]["policyholder_id"], "PH-REJ-001")
        self.assertIn("Policyholder: Morgan Sample (INDIVIDUAL, PH-REJ-001, not an insured member)", render_report(r))

    def test_policyholder_name_is_not_sent_to_llm(self):
        for claim_id in ("CLM-APP-001", "CLM-REJ-001", "CLM-RFI-001"):
            r = assess(claim_id).report
            self.assertNotIn(r["metadata"]["policyholder"]["name"], json.dumps(explanation_facts(r)))

    def test_policyholder_does_not_affect_the_decision(self):
        policies = {k: {**v, "policyholder": None} for k, v in STORE.policies.items()}
        store = __import__("dataclasses").replace(STORE, policies=policies)
        for claim_id in ("CLM-APP-001", "CLM-REJ-001", "CLM-RFI-001"):
            with self.subTest(claim=claim_id):
                self.assertEqual(
                    assess(claim_id, store).report["recommendation"]["outcome"],
                    assess(claim_id).report["recommendation"]["outcome"],
                )

    def test_report_is_json_serializable(self):
        a = assess("CLM-APP-001")
        json.dumps({"report": a.report, "audit": a.audit.to_dict()})


class FailureModesTest(unittest.TestCase):
    def assert_pending_review(self, report):
        self.assertIsNone(report["recommendation"]["outcome"])
        self.assertEqual(report["assessment_status"], "ESCALATED")
        self.assertTrue(report["recommendation"]["escalations"])
        self.assertIsNone(report["recommendation"]["recommended_payable"])

    def test_unknown_policy_is_escalated_not_decided(self):
        a = assess("CLM-APP-001", store_without_policy("POL-APP-001"))
        self.assertEqual(a.report["policy_verification"]["status"], "UNRESOLVED")
        self.assertEqual(a.report["benefit_calculation"]["status"], "PENDING")
        self.assert_pending_review(a.report)

    def test_missing_balance_is_escalated(self):
        r = assess("CLM-APP-001", store_without_balances()).report
        self.assertEqual(r["benefit_calculation"]["status"], "PENDING")
        self.assertIsNone(r["benefit_calculation"]["insurer_payable"])
        self.assert_pending_review(r)

    def test_unmatched_clinical_rule_is_referred(self):
        store = store_with_document_fact("A-D4", "procedures", ["Outpatient consultation", "MRI scan"])
        r = assess("CLM-APP-001", store).report
        self.assertEqual(r["medical_necessity"]["result"], "REFER_TO_MEDICAL_REVIEW")
        self.assert_pending_review(r)

    def test_tool_error_becomes_unresolved_result(self):
        with mock.patch("claim_agent.tools.medical.check_medical_necessity", side_effect=RuntimeError("rules unavailable")):
            a = assess("CLM-APP-001")
        error = next(e for e in a.audit.events if e.name == "checkMedicalNecessity")
        self.assertEqual(error.status, "ERROR")
        self.assertIn("rules unavailable", error.reason)
        self.assertEqual(a.report["medical_necessity"]["result"], "REFER_TO_MEDICAL_REVIEW")
        self.assert_pending_review(a.report)

    def test_document_tool_error_leaves_requirement_missing(self):
        real = __import__("claim_agent.tools.documents", fromlist=["verify_document"]).verify_document

        def flaky(document_id, context):
            if document_id == "A-D4":
                raise TimeoutError("extraction service timeout")
            return real(document_id, context)

        with mock.patch("claim_agent.tools.documents.verify_document", side_effect=flaky):
            r = assess("CLM-APP-001").report
        self.assertEqual(row(r, "MEDICAL_REPORT")["status"], "MISSING")
        self.assertEqual(r["recommendation"]["outcome"], "REQUEST_MORE_INFO")

    def test_identity_mismatch_is_not_accepted(self):
        r = assess("CLM-APP-001", store_with_document_fact("A-D1", "member_id", "MEM-SOMEONE-ELSE")).report
        self.assertEqual(row(r, "CLAIM_FORM")["status"], "MISSING")
        self.assertTrue(r["document_review"]["consistency_issues"])
        self.assertNotEqual(r["recommendation"]["outcome"], "APPROVE")

    def test_waiting_period_failure_rejects_with_clause(self):
        r = assess("CLM-APP-001", store_with_member_changes("POL-APP-001", coverage_start="2026-09-01")).report
        self.assertEqual(r["recommendation"]["outcome"], "REJECT")
        cited = {c["clause_id"] for c in r["policy_citations"]["citations"]}
        self.assertIn("APP-4.1", cited)

    def test_late_reimbursement_claim_rejects_with_deadline_clause(self):
        r = assess("CLM-APP-001", store_with_claim_changes("CLM-APP-001", submission_date="2026-11-20")).report
        self.assertEqual(r["recommendation"]["outcome"], "REJECT")
        deadline = next(c for c in r["policy_verification"]["checks"] if c["check"] == "submission_deadline")
        self.assertEqual((deadline["result"], deadline["rule_ids"]), ("FAIL", ["CSR-2.1"]))
        rule = next(c for c in r["policy_citations"]["citations"] if c["clause_id"] == "CSR-2.1")
        self.assertEqual((rule["kind"], rule["source_document"]), ("RULE", "Fictional Claim Submission Rules CSR-2026"))
        self.assertTrue(any("deadline" in reason["finding"] for reason in r["recommendation"]["reasons"]))
        self.assertEqual(r["validation"]["status"], "PASS")

    def test_missing_claim_mode_is_escalated(self):
        r = assess("CLM-APP-001", store_with_claim_changes("CLM-APP-001", claim_mode=None)).report
        self.assertIsNone(r["recommendation"]["outcome"])
        self.assertEqual(r["assessment_status"], "ESCALATED")

    def test_null_diagnosis_without_explicit_finding_never_rejects(self):
        store = store_with_document_fact("R-D4", "medical_indication_present", None)
        r = assess("CLM-REJ-001", store).report
        self.assertNotEqual(r["recommendation"]["outcome"], "REJECT")


class ExplanationsTest(unittest.TestCase):
    def client(self, *contents):
        responses = [{"id": "gen-x", "model": "test/model", "choices": [{"message": {"content": c}}]} for c in contents]
        return OpenRouterClient(LLMConfig(api_key="test-secret-key", retry_delay_s=0), lambda *a: responses.pop(0))

    def test_malformed_model_response_never_changes_decision(self):
        a = assess("CLM-APP-001", client=self.client("not json", "{still not"))
        r = a.report
        self.assertEqual(r["explanations"]["status"], "FAILED")
        self.assertEqual(r["recommendation"]["outcome"], "APPROVE")
        self.assertEqual(r["validation"]["status"], "PASS")
        self.assertIn(("LLM_CALL", "draftExplanations", "ERROR"), events(a))

    def test_valid_explanations_are_attached_with_model_metadata(self):
        sections = ["document_review", "policy_verification", "medical_necessity", "benefit_calculation", "recommendation"]
        a = assess("CLM-APP-001", client=self.client(json.dumps({s: "Consistent with the verified facts." for s in sections})))
        r = a.report
        self.assertEqual(r["explanations"]["status"], "DRAFTED")
        self.assertEqual(r["explanations"]["llm"]["served_model"], "test/model")
        self.assertEqual(r["metadata"]["llm"]["model"], "openai/gpt-4o")
        self.assertNotIn("test-secret-key", json.dumps({"report": r, "audit": a.audit.to_dict()}))


if __name__ == "__main__":
    unittest.main()
