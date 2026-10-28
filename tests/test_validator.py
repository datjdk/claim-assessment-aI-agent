"""validate_report: tampered or inconsistent reports must fail validation."""

import copy
import unittest

from claim_agent.orchestrator import assess_claim
from claim_agent.validator import validate_report
from helpers import STORE


def assessed(claim_id):
    a = assess_claim(claim_id, STORE)
    return a, {d["document_id"] for d in a.context.claim["documents"]}


class ValidateReportTest(unittest.TestCase):
    def validate(self, claim_id, tamper):
        a, doc_ids = assessed(claim_id)
        report = copy.deepcopy(a.report)
        tamper(report)
        return validate_report(report, a.policy, doc_ids)

    def test_untampered_reports_pass(self):
        for claim_id in ("CLM-APP-001", "CLM-REJ-001", "CLM-RFI-001"):
            result = self.validate(claim_id, lambda r: None)
            self.assertEqual(result["status"], "PASS", result["errors"])

    def test_altered_clause_text_fails(self):
        def tamper(r):
            r["policy_citations"]["citations"][-1]["text"] = "We will pay for everything."
        result = self.validate("CLM-APP-001", tamper)
        self.assertEqual(result["citation_check"], "FAIL")

    def test_invented_clause_fails(self):
        def tamper(r):
            c = next(c for c in r["policy_citations"]["citations"] if c["kind"] == "POLICY")
            c["clause_id"] = "APP-99.9"
        self.assertEqual(self.validate("CLM-APP-001", tamper)["status"], "FAIL")

    def test_wrong_policy_version_fails(self):
        def tamper(r):
            next(c for c in r["policy_citations"]["citations"] if c["kind"] == "POLICY")["version"] = "2025-Z"
        self.assertEqual(self.validate("CLM-APP-001", tamper)["status"], "FAIL")

    def test_altered_rule_citation_fails(self):
        def tamper(r):
            next(c for c in r["policy_citations"]["citations"] if c["kind"] == "RULE")["text"] = "Claims may be submitted any time."
        self.assertEqual(self.validate("CLM-APP-001", tamper)["citation_check"], "FAIL")

    def test_dangling_citation_id_fails(self):
        def tamper(r):
            r["recommendation"]["reasons"][0]["citation_ids"].append("PC-99")
        self.assertEqual(self.validate("CLM-APP-001", tamper)["status"], "FAIL")

    def test_reason_without_evidence_fails(self):
        def tamper(r):
            r["recommendation"]["reasons"][0]["evidence"] = []
        self.assertEqual(self.validate("CLM-APP-001", tamper)["status"], "FAIL")

    def test_calculation_that_does_not_reconcile_fails(self):
        def tamper(r):
            r["benefit_calculation"]["insurer_payable"] = "190.00"
        result = self.validate("CLM-APP-001", tamper)
        self.assertEqual(result["reconciliation"], "NEEDS_REVIEW")

    def test_pending_calculation_with_zero_instead_of_null_fails(self):
        def tamper(r):
            r["benefit_calculation"]["insurer_payable"] = "0.00"
        self.assertEqual(self.validate("CLM-RFI-001", tamper)["status"], "FAIL")

    def test_request_more_info_without_open_request_fails(self):
        def tamper(r):
            r["recommendation"]["information_requests"] = []
        self.assertEqual(self.validate("CLM-RFI-001", tamper)["status"], "FAIL")

    def test_finding_about_unsubmitted_document_fails(self):
        def tamper(r):
            r["document_review"]["rows"][0]["document_id"] = "Z-D1"
        self.assertEqual(self.validate("CLM-APP-001", tamper)["status"], "FAIL")

    def test_pre_authorized_report_fails(self):
        def tamper(r):
            r["human_review"]["authorization_status"] = "APPROVED"
        self.assertEqual(self.validate("CLM-APP-001", tamper)["status"], "FAIL")

    def test_approve_with_unsupported_medical_necessity_fails(self):
        def tamper(r):
            r["medical_necessity"]["result"] = "REFER_TO_MEDICAL_REVIEW"
        self.assertEqual(self.validate("CLM-APP-001", tamper)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
