"""Integrity checks for the fictional fixtures: references resolve and amounts reconcile."""

import unittest
from decimal import Decimal

from claim_agent.fixtures import FixtureStore


def fact(document, name):
    return next(f["value"] for f in document["extracted_facts"] if f["fact"] == name)


class FixtureIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = FixtureStore.load()

    def test_three_acceptance_claims_exist(self):
        self.assertEqual(set(self.store.claims), {"CLM-APP-001", "CLM-REJ-001", "CLM-RFI-001"})

    def test_claim_references_resolve(self):
        for claim in self.store.claims.values():
            policy = self.store.policy(claim["policy_id"])
            self.assertIsNotNone(policy, claim["claim_id"])
            self.assertIn(claim["member_id"], {m["member_id"] for m in policy["members"]})
            self.assertIsNotNone(self.store.checklist(claim["claim_type"]))
            self.assertIsNotNone(
                self.store.balance(claim["policy_id"], claim["member_id"], claim["claim_type"])
            )
            for ref in claim["documents"]:
                doc = self.store.document(ref["document_id"])
                self.assertIsNotNone(doc, ref["document_id"])
                self.assertEqual(doc["claim_id"], claim["claim_id"])

    def test_every_policy_has_a_policyholder(self):
        for policy in self.store.policies.values():
            holder = policy["policyholder"]
            self.assertTrue(holder["policyholder_id"] and holder["name"], policy["policy_id"])
            self.assertIn(holder["type"], {"INDIVIDUAL", "ORGANIZATION"})
            if holder["member_id"] is not None:
                self.assertIn(holder["member_id"], {m["member_id"] for m in policy["members"]})
            if holder["type"] == "ORGANIZATION":
                self.assertIsNone(holder["member_id"])

    def test_policy_clause_ids_exist(self):
        for policy in self.store.policies.values():
            clause_ids = {c["clause_id"] for c in policy["clauses"]}
            self.assertIn(policy["period_clause_id"], clause_ids)
            self.assertIn(policy["member_clause_id"], clause_ids)
            for clause_id in policy["document_requirement_clause_ids"].values():
                self.assertIn(clause_id, clause_ids)
            for benefit in policy["benefits"].values():
                for key, value in benefit.items():
                    if key.endswith("clause_id"):
                        self.assertIn(value, clause_ids, f"{policy['policy_id']} {key}")
            for exclusion in policy["exclusions"]:
                self.assertIn(exclusion["clause_id"], clause_ids)

    def test_submission_rules_cover_every_claim_policy_once(self):
        for claim in self.store.claims.values():
            matching = [r for r in self.store.submission_rule_sets if claim["policy_id"] in r["applies_to_policy_ids"]]
            self.assertEqual(len(matching), 1, claim["policy_id"])
        for rule_set in self.store.submission_rule_sets:
            for policy_id in rule_set["applies_to_policy_ids"]:
                self.assertIsNotNone(self.store.policy(policy_id), policy_id)
            claim_types = [t for d in rule_set["deadlines"] for t in d["claim_types"]]
            self.assertEqual(len(claim_types), len(set(claim_types)), "a claim type has two deadlines")
            for d in rule_set["deadlines"]:
                self.assertTrue(d["exact_text"])

    def test_amounts_reconcile(self):
        for claim in self.store.claims.values():
            submitted = Decimal(claim["submitted_amount"]["amount"])
            invoice = self.store.document(claim["documents"][1]["document_id"])
            lines = sum(Decimal(line["amount"]) for line in fact(invoice, "line_items"))
            self.assertEqual(lines, submitted, claim["claim_id"])
            self.assertEqual(Decimal(fact(invoice, "invoice_total")), submitted)
        for b in self.store.balances:
            self.assertEqual(
                Decimal(b["annual_limit"]) - Decimal(b["used_to_date"]), Decimal(b["remaining"])
            )

    def test_approval_case_traits(self):
        report = self.store.document("A-D4")
        self.assertEqual(fact(report, "diagnosis"), "Acute bacterial sinusitis")
        benefit = self.store.policy("POL-APP-001")["benefits"]["OUTPATIENT"]
        self.assertEqual(Decimal(benefit["copay_per_visit"]), Decimal("20.00"))
        balance = self.store.balance("POL-APP-001", "MEM-APP-001", "OUTPATIENT")
        self.assertEqual(Decimal(balance["remaining"]), Decimal("800.00"))

    def test_rejection_case_explicitly_records_no_medical_indication(self):
        report = self.store.document("R-D4")
        self.assertIsNone(fact(report, "diagnosis"))
        self.assertIs(fact(report, "medical_indication_present"), False)
        self.assertEqual(fact(report, "procedure_classification"), "COSMETIC_ELECTIVE")

    def test_rfi_case_medical_report_is_appointment_confirmation(self):
        doc = self.store.document("I-D4")
        self.assertEqual(doc["detected_type"], "APPOINTMENT_CONFIRMATION")
        declared = next(d for d in self.store.claim("CLM-RFI-001")["documents"] if d["document_id"] == "I-D4")
        self.assertEqual(declared["declared_type"], "MEDICAL_REPORT")
        self.assertNotIn("diagnosis", {f["fact"] for f in doc["extracted_facts"]})

    def test_unknown_lookups_return_none(self):
        self.assertIsNone(self.store.policy("POL-UNKNOWN"))
        self.assertIsNone(self.store.document("X-D9"))
        self.assertIsNone(self.store.balance("POL-APP-001", "MEM-APP-001", "INPATIENT"))


if __name__ == "__main__":
    unittest.main()
