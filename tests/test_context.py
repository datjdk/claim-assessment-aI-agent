"""create_assessment_context: claim loading, intake validation and verified-fact tracking."""

import unittest
from datetime import date
from decimal import Decimal

from claim_agent.context import ClaimValidationError, Fact, create_assessment_context
from helpers import STORE, context_for, store_with_claim_changes


class CreateAssessmentContextTest(unittest.TestCase):
    def test_builds_context_from_valid_claim(self):
        ctx = context_for("CLM-APP-001")
        self.assertEqual(ctx.claim_id, "CLM-APP-001")
        self.assertEqual(ctx.policy_id, "POL-APP-001")
        self.assertEqual(ctx.member_id, "MEM-APP-001")
        self.assertEqual(ctx.claim_type, "OUTPATIENT")
        self.assertEqual(ctx.treatment_start, date(2026, 9, 15))
        self.assertEqual(ctx.treatment_end, date(2026, 9, 15))
        self.assertEqual(ctx.submission_date, date(2026, 9, 18))
        self.assertEqual(ctx.claim_mode, "REIMBURSEMENT")
        self.assertIsInstance(ctx.submitted_amount, Decimal)
        self.assertEqual(ctx.submitted_amount, Decimal("200.00"))
        self.assertEqual(ctx.currency, "USD")
        self.assertEqual(ctx.checklist["checklist_id"], "CHK-OUTPATIENT")
        self.assertTrue(ctx.context_version)

    def test_claimant_reported_facts_are_not_verified(self):
        ctx = context_for("CLM-APP-001")
        self.assertEqual(ctx.verified_facts, {})
        self.assertIsNone(ctx.fact("diagnosis"))

    def test_unknown_claim_raises(self):
        with self.assertRaises(ClaimValidationError):
            create_assessment_context("CLM-UNKNOWN", STORE)

    def test_rejects_invalid_amounts(self):
        for bad in ["-5.00", "abc", "", 200.0, None]:
            with self.subTest(amount=bad):
                store = store_with_claim_changes(
                    "CLM-APP-001", submitted_amount={"amount": bad, "currency": "USD"}
                )
                with self.assertRaises(ClaimValidationError):
                    create_assessment_context("CLM-APP-001", store)

    def test_rejects_missing_currency(self):
        store = store_with_claim_changes("CLM-APP-001", submitted_amount={"amount": "200.00", "currency": ""})
        with self.assertRaises(ClaimValidationError):
            create_assessment_context("CLM-APP-001", store)

    def test_rejects_treatment_end_before_start(self):
        store = store_with_claim_changes(
            "CLM-APP-001", treatment_dates={"start": "2026-09-15", "end": "2026-09-10"}
        )
        with self.assertRaises(ClaimValidationError):
            create_assessment_context("CLM-APP-001", store)

    def test_rejects_malformed_date(self):
        store = store_with_claim_changes(
            "CLM-APP-001", treatment_dates={"start": "15/09/2026", "end": "2026-09-15"}
        )
        with self.assertRaises(ClaimValidationError):
            create_assessment_context("CLM-APP-001", store)

    def test_rejects_missing_or_malformed_submission_date(self):
        for bad in [None, "18/09/2026"]:
            with self.subTest(submission_date=bad):
                store = store_with_claim_changes("CLM-APP-001", submission_date=bad)
                with self.assertRaises(ClaimValidationError):
                    create_assessment_context("CLM-APP-001", store)

    def test_rejects_submission_before_treatment(self):
        store = store_with_claim_changes("CLM-APP-001", submission_date="2026-09-01")
        with self.assertRaises(ClaimValidationError):
            create_assessment_context("CLM-APP-001", store)

    def test_rejects_claim_without_documents(self):
        store = store_with_claim_changes("CLM-APP-001", documents=[])
        with self.assertRaises(ClaimValidationError):
            create_assessment_context("CLM-APP-001", store)


class VerifiedFactsTest(unittest.TestCase):
    def test_record_and_read_fact_with_evidence(self):
        ctx = context_for("CLM-APP-001")
        ctx.record_fact("diagnosis", "Acute bacterial sinusitis", "A-D4", "p.1, Assessment")
        self.assertEqual(ctx.fact("diagnosis"), Fact("Acute bacterial sinusitis", "A-D4", "p.1, Assessment"))

    def test_explicit_null_fact_differs_from_absent_fact(self):
        ctx = context_for("CLM-REJ-001")
        ctx.record_fact("diagnosis", None, "R-D4", "p.1, Assessment")
        self.assertIsNotNone(ctx.fact("diagnosis"))
        self.assertIsNone(ctx.fact("diagnosis").value)
        self.assertIsNone(ctx.fact("procedures"))


if __name__ == "__main__":
    unittest.main()
