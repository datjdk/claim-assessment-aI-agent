"""lookupPolicy(policyId): coverage checks against the context, with version and exact clauses."""

import dataclasses
import unittest
from datetime import date
from decimal import Decimal

from claim_agent.tools import lookup_policy
from helpers import STORE, store_without_balances, verified_context

CHECKS = ("policy_active", "member_covered", "benefit_covered", "waiting_period", "submission_deadline", "exclusions", "limit")


def clause_text(policy_id, clause_id):
    clauses = STORE.policy(policy_id)["clauses"]
    return next(c["exact_text"] for c in clauses if c["clause_id"] == clause_id)


class LookupPolicyTest(unittest.TestCase):
    def test_approval_policy_passes_every_check(self):
        result = lookup_policy("POL-APP-001", verified_context("CLM-APP-001"))
        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.policy_id, "POL-APP-001")
        self.assertEqual(result.version, "2026-A")
        self.assertEqual(result.policy_document, "Fictional Essential Health Plan, Policy Wording 2026-A")
        for name in CHECKS:
            with self.subTest(check=name):
                self.assertEqual(result.checks[name].result, "PASS")

    def test_each_check_cites_its_clause(self):
        result = lookup_policy("POL-APP-001", verified_context("CLM-APP-001"))
        expected = {
            "policy_active": ["APP-2.1"],
            "member_covered": ["APP-2.2"],
            "benefit_covered": ["APP-3.1"],
            "waiting_period": ["APP-4.1"],
            "limit": ["APP-5.1"],
        }
        for name, clause_ids in expected.items():
            with self.subTest(check=name):
                self.assertEqual(result.checks[name].clause_ids, clause_ids)
        self.assertEqual(result.checks["submission_deadline"].rule_ids, ["CSR-2.1"])
        for check in result.checks.values():
            for clause_id in check.clause_ids:
                self.assertIn(clause_id, result.clauses)
            for rule_id in check.rule_ids:
                self.assertIn(rule_id, result.rules)

    def test_returns_exact_clause_text_and_location(self):
        result = lookup_policy("POL-APP-001", verified_context("CLM-APP-001"))
        copay = result.clauses["APP-5.3"]
        self.assertEqual(copay["exact_text"], clause_text("POL-APP-001", "APP-5.3"))
        self.assertEqual(copay["location"], "Page 6, Section 5.3")

    def test_returns_policyholder(self):
        holder = lookup_policy("POL-APP-001", verified_context("CLM-APP-001")).policyholder
        self.assertEqual((holder["policyholder_id"], holder["type"], holder["member_id"]), ("PH-APP-001", "INDIVIDUAL", "MEM-APP-001"))
        group = lookup_policy("POL-RFI-001", verified_context("CLM-RFI-001")).policyholder
        self.assertEqual((group["type"], group["member_id"]), ("ORGANIZATION", None))

    def test_reports_remaining_limit(self):
        result = lookup_policy("POL-APP-001", verified_context("CLM-APP-001"))
        self.assertEqual(result.remaining_limit, Decimal("800.00"))

    def test_documented_cosmetic_procedure_fails_exclusion_check(self):
        result = lookup_policy("POL-REJ-001", verified_context("CLM-REJ-001"))
        self.assertEqual(result.checks["exclusions"].result, "FAIL")
        self.assertEqual(result.checks["exclusions"].clause_ids, ["REJ-6.4"])
        self.assertEqual(result.clauses["REJ-6.4"]["exact_text"], clause_text("POL-REJ-001", "REJ-6.4"))
        for name in ("policy_active", "member_covered", "benefit_covered", "waiting_period", "submission_deadline", "limit"):
            self.assertEqual(result.checks[name].result, "PASS")

    def test_exclusion_is_uncertain_without_verified_clinical_facts(self):
        result = lookup_policy("POL-RFI-001", verified_context("CLM-RFI-001"))
        self.assertEqual(result.checks["exclusions"].result, "UNCERTAIN")
        self.assertEqual(result.checks["policy_active"].result, "PASS")
        self.assertEqual(result.checks["benefit_covered"].result, "PASS")

    def test_policy_not_active_on_treatment_date(self):
        ctx = dataclasses.replace(
            verified_context("CLM-APP-001"), treatment_start=date(2027, 1, 5), treatment_end=date(2027, 1, 5)
        )
        result = lookup_policy("POL-APP-001", ctx)
        self.assertEqual(result.checks["policy_active"].result, "FAIL")

    def test_member_not_on_policy(self):
        ctx = dataclasses.replace(verified_context("CLM-APP-001"), member_id="MEM-OTHER")
        result = lookup_policy("POL-APP-001", ctx)
        self.assertEqual(result.checks["member_covered"].result, "FAIL")

    def test_waiting_period_not_satisfied(self):
        ctx = dataclasses.replace(
            verified_context("CLM-APP-001"), treatment_start=date(2026, 1, 20), treatment_end=date(2026, 1, 20)
        )
        result = lookup_policy("POL-APP-001", ctx)
        self.assertEqual(result.checks["waiting_period"].result, "FAIL")

    def test_benefit_missing_from_policy_is_uncertain_not_fail(self):
        ctx = dataclasses.replace(verified_context("CLM-APP-001"), claim_type="DENTAL")
        result = lookup_policy("POL-APP-001", ctx)
        self.assertEqual(result.checks["benefit_covered"].result, "UNCERTAIN")

    def test_missing_balance_makes_limit_uncertain(self):
        result = lookup_policy("POL-APP-001", verified_context("CLM-APP-001", store_without_balances()))
        self.assertEqual(result.checks["limit"].result, "UNCERTAIN")
        self.assertIsNone(result.remaining_limit)

    def test_submission_on_deadline_day_passes(self):
        ctx = dataclasses.replace(verified_context("CLM-APP-001"), submission_date=date(2026, 11, 14))
        check = lookup_policy("POL-APP-001", ctx).checks["submission_deadline"]
        self.assertEqual(check.result, "PASS")
        self.assertIn("60 days", check.fact)

    def test_submission_after_60_days_fails(self):
        ctx = dataclasses.replace(verified_context("CLM-APP-001"), submission_date=date(2026, 11, 15))
        check = lookup_policy("POL-APP-001", ctx).checks["submission_deadline"]
        self.assertEqual(check.result, "FAIL")
        self.assertEqual(check.rule_ids, ["CSR-2.1"])
        self.assertEqual(check.clause_ids, [])
        self.assertIn("claim_submission:CLM-APP-001", check.evidence)

    def test_deadline_rule_comes_from_submission_rules_source(self):
        result = lookup_policy("POL-APP-001", verified_context("CLM-APP-001"))
        rule = result.rules["CSR-2.1"]
        source = STORE.submission_rule_set("POL-APP-001")
        self.assertEqual(rule["exact_text"], source["deadlines"][0]["exact_text"])
        self.assertEqual((rule["version"], rule["source_document"]), ("2026.1", "Fictional Claim Submission Rules CSR-2026"))

    def test_policy_without_submission_rules_is_uncertain(self):
        store = dataclasses.replace(STORE, submission_rule_sets=[])
        check = lookup_policy("POL-APP-001", verified_context("CLM-APP-001", store)).checks["submission_deadline"]
        self.assertEqual(check.result, "UNCERTAIN")

    def test_deadline_counts_from_last_treatment_or_discharge_date(self):
        ctx = dataclasses.replace(
            verified_context("CLM-APP-001"),
            treatment_start=date(2026, 9, 10), treatment_end=date(2026, 9, 20), submission_date=date(2026, 11, 19),
        )
        self.assertEqual(lookup_policy("POL-APP-001", ctx).checks["submission_deadline"].result, "PASS")

    def test_maternity_allows_180_days(self):
        base = verified_context("CLM-APP-001")
        on_time = dataclasses.replace(base, claim_type="MATERNITY", submission_date=date(2027, 3, 14))
        late = dataclasses.replace(base, claim_type="MATERNITY", submission_date=date(2027, 3, 15))
        self.assertEqual(lookup_policy("POL-APP-001", on_time).checks["submission_deadline"].result, "PASS")
        self.assertEqual(lookup_policy("POL-APP-001", on_time).checks["submission_deadline"].rule_ids, ["CSR-2.2"])
        self.assertEqual(lookup_policy("POL-APP-001", late).checks["submission_deadline"].result, "FAIL")

    def test_deadline_does_not_apply_to_direct_billing(self):
        ctx = dataclasses.replace(verified_context("CLM-APP-001"), claim_mode="DIRECT_BILLING", submission_date=date(2027, 6, 1))
        self.assertEqual(lookup_policy("POL-APP-001", ctx).checks["submission_deadline"].result, "PASS")

    def test_unknown_claim_mode_is_uncertain(self):
        ctx = dataclasses.replace(verified_context("CLM-APP-001"), claim_mode=None)
        self.assertEqual(lookup_policy("POL-APP-001", ctx).checks["submission_deadline"].result, "UNCERTAIN")

    def test_claim_type_without_deadline_is_uncertain(self):
        ctx = dataclasses.replace(verified_context("CLM-APP-001"), claim_type="DENTAL")
        self.assertEqual(lookup_policy("POL-APP-001", ctx).checks["submission_deadline"].result, "UNCERTAIN")

    def test_unknown_policy_is_unresolved(self):
        result = lookup_policy("POL-UNKNOWN", verified_context("CLM-APP-001"))
        self.assertEqual(result.status, "UNRESOLVED")
        self.assertTrue(result.reason)
        self.assertIsNone(result.version)
        self.assertIsNone(result.policyholder)
        self.assertEqual(result.checks, {})
        self.assertEqual(result.clauses, {})


if __name__ == "__main__":
    unittest.main()
