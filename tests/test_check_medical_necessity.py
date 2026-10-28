"""checkMedicalNecessity(diagnosis, procedures): rule matching on verified clinical facts only."""

import unittest

from claim_agent.tools import check_medical_necessity
from helpers import context_for, verified_context

SINUSITIS = "Acute bacterial sinusitis"
SINUSITIS_PROCEDURES = ["Outpatient consultation", "Prescribed treatment"]
RHINOPLASTY = ["Elective cosmetic rhinoplasty"]


class CheckMedicalNecessityTest(unittest.TestCase):
    def test_supported_for_documented_sinusitis(self):
        result = check_medical_necessity(SINUSITIS, SINUSITIS_PROCEDURES, verified_context("CLM-APP-001"))
        self.assertEqual(result.result, "SUPPORTED")
        self.assertEqual(result.rule_id, "CR-001")
        self.assertTrue(result.rationale)
        self.assertEqual(result.rule_set_version, "1.0")
        self.assertEqual(result.source_location, "CNR-2026 Section 2.3")

    def test_cites_supporting_documents(self):
        result = check_medical_necessity(SINUSITIS, SINUSITIS_PROCEDURES, verified_context("CLM-APP-001"))
        self.assertIn("A-D4", {fact.document_id for fact in result.evidence})

    def test_procedure_order_does_not_matter(self):
        result = check_medical_necessity(
            SINUSITIS, list(reversed(SINUSITIS_PROCEDURES)), verified_context("CLM-APP-001")
        )
        self.assertEqual(result.result, "SUPPORTED")

    def test_not_supported_when_report_documents_no_medical_indication(self):
        result = check_medical_necessity(None, RHINOPLASTY, verified_context("CLM-REJ-001"))
        self.assertEqual(result.result, "NOT_SUPPORTED")
        self.assertEqual(result.rule_id, "CR-002")
        self.assertIn("R-D4", {fact.document_id for fact in result.evidence})

    def test_null_diagnosis_alone_is_insufficient_evidence(self):
        result = check_medical_necessity(None, RHINOPLASTY, context_for("CLM-REJ-001"))
        self.assertEqual(result.result, "INSUFFICIENT_EVIDENCE")
        self.assertIsNone(result.rule_id)

    def test_claimant_reported_facts_alone_are_insufficient(self):
        result = check_medical_necessity(SINUSITIS, SINUSITIS_PROCEDURES, context_for("CLM-APP-001"))
        self.assertEqual(result.result, "INSUFFICIENT_EVIDENCE")

    def test_no_procedures_is_insufficient_evidence(self):
        result = check_medical_necessity(SINUSITIS, [], verified_context("CLM-APP-001"))
        self.assertEqual(result.result, "INSUFFICIENT_EVIDENCE")

    def test_contradicting_fact_refers_to_medical_review(self):
        ctx = verified_context("CLM-REJ-001")
        ctx.record_fact("medical_indication_present", True, "R-D9", "p.1, Assessment")
        result = check_medical_necessity(None, RHINOPLASTY, ctx)
        self.assertEqual(result.result, "REFER_TO_MEDICAL_REVIEW")

    def test_combined_functional_and_cosmetic_surgery_is_referred(self):
        ctx = context_for("CLM-REJ-001")
        ctx.record_fact("medical_indication_present", True, "R-D4", "p.1, Assessment")
        result = check_medical_necessity(
            "Nasal septal deviation with airway obstruction", ["Septorhinoplasty"], ctx
        )
        self.assertEqual(result.result, "REFER_TO_MEDICAL_REVIEW")
        self.assertEqual(result.rule_id, "CR-003")

    def test_unmatched_combination_is_referred_not_assumed(self):
        result = check_medical_necessity(SINUSITIS, ["MRI scan"], verified_context("CLM-APP-001"))
        self.assertEqual(result.result, "REFER_TO_MEDICAL_REVIEW")
        self.assertIsNone(result.rule_id)
        self.assertTrue(result.reason)


if __name__ == "__main__":
    unittest.main()
