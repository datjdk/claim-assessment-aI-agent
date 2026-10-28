"""calculateBenefit(policyId, claimType, amount): Decimal calculation, or PENDING with null amounts."""

import unittest
from decimal import Decimal

from claim_agent.tools import calculate_benefit
from helpers import store_with_balance, store_without_balances, verified_context

D = Decimal
CALCULATED = (
    "excluded", "eligible", "deductible", "copay", "coinsurance",
    "insurer_payable", "member_responsibility", "remaining_limit_before", "remaining_limit_after",
)


class CalculateBenefitTest(unittest.TestCase):
    def assert_amounts(self, result, **expected):
        for name, value in expected.items():
            with self.subTest(field=name):
                self.assertIsInstance(getattr(result, name), Decimal)
                self.assertEqual(getattr(result, name), D(value))

    def assert_pending(self, result):
        self.assertEqual(result.status, "PENDING")
        self.assertTrue(result.pending_reasons)
        for name in CALCULATED:
            with self.subTest(field=name):
                self.assertIsNone(getattr(result, name))

    def test_approval_case(self):
        result = calculate_benefit("POL-APP-001", "OUTPATIENT", "200.00", verified_context("CLM-APP-001"))
        self.assertEqual(result.status, "COMPLETE")
        self.assertEqual(result.currency, "USD")
        self.assert_amounts(
            result,
            submitted="200.00", excluded="0.00", eligible="200.00", deductible="0.00",
            copay="20.00", coinsurance="0.00", insurer_payable="180.00",
            member_responsibility="20.00", remaining_limit_before="800.00", remaining_limit_after="620.00",
        )

    def test_cites_limit_and_cost_sharing_clauses(self):
        result = calculate_benefit("POL-APP-001", "OUTPATIENT", "200.00", verified_context("CLM-APP-001"))
        self.assertTrue({"APP-5.1", "APP-5.2", "APP-5.3"} <= set(result.clause_ids))

    def test_steps_follow_policy_calculation_order(self):
        result = calculate_benefit("POL-APP-001", "OUTPATIENT", "200.00", verified_context("CLM-APP-001"))
        self.assertEqual(
            [step["step"] for step in result.steps],
            ["EXCLUSIONS", "DEDUCTIBLE", "COPAY", "COINSURANCE", "ANNUAL_LIMIT"],
        )

    def test_excluded_cosmetic_claim_pays_nothing(self):
        result = calculate_benefit("POL-REJ-001", "OUTPATIENT", "2000.00", verified_context("CLM-REJ-001"))
        self.assertEqual(result.status, "COMPLETE")
        self.assert_amounts(
            result,
            submitted="2000.00", excluded="2000.00", eligible="0.00", copay="0.00",
            insurer_payable="0.00", member_responsibility="2000.00", remaining_limit_after="1500.00",
        )
        self.assertIn("REJ-6.4", result.clause_ids)

    def test_payable_is_capped_at_remaining_limit(self):
        store = store_with_balance("POL-APP-001", used_to_date="900.00", remaining="100.00")
        result = calculate_benefit("POL-APP-001", "OUTPATIENT", "200.00", verified_context("CLM-APP-001", store))
        self.assert_amounts(
            result, insurer_payable="100.00", member_responsibility="100.00", remaining_limit_after="0.00"
        )

    def test_payable_and_member_responsibility_reconcile_to_submitted(self):
        cases = [("CLM-APP-001", "POL-APP-001", "200.00"), ("CLM-REJ-001", "POL-REJ-001", "2000.00")]
        for claim_id, policy_id, amount in cases:
            with self.subTest(claim=claim_id):
                r = calculate_benefit(policy_id, "OUTPATIENT", amount, verified_context(claim_id))
                self.assertEqual(r.excluded + r.eligible, r.submitted)
                self.assertEqual(r.insurer_payable + r.member_responsibility, r.submitted)

    def test_rejects_float_amount(self):
        with self.assertRaises(TypeError):
            calculate_benefit("POL-APP-001", "OUTPATIENT", 200.0, verified_context("CLM-APP-001"))

    def test_unknown_policy_is_pending_with_null_amounts(self):
        result = calculate_benefit("POL-UNKNOWN", "OUTPATIENT", "200.00", verified_context("CLM-APP-001"))
        self.assert_pending(result)
        self.assertEqual(result.submitted, D("200.00"))

    def test_missing_balance_is_pending(self):
        ctx = verified_context("CLM-APP-001", store_without_balances())
        self.assert_pending(calculate_benefit("POL-APP-001", "OUTPATIENT", "200.00", ctx))

    def test_unresolved_exclusion_is_pending(self):
        result = calculate_benefit("POL-RFI-001", "OUTPATIENT", "300.00", verified_context("CLM-RFI-001"))
        self.assert_pending(result)

    def test_missing_visit_count_is_pending(self):
        ctx = verified_context("CLM-APP-001")
        del ctx.verified_facts["visit_count"]
        self.assert_pending(calculate_benefit("POL-APP-001", "OUTPATIENT", "200.00", ctx))

    def test_amount_not_matching_verified_invoice_is_pending(self):
        result = calculate_benefit("POL-APP-001", "OUTPATIENT", "250.00", verified_context("CLM-APP-001"))
        self.assert_pending(result)


if __name__ == "__main__":
    unittest.main()
