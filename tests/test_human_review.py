"""Human review: authorization and override are recorded with reviewer, reason and time."""

import unittest

from claim_agent.human_review import ReviewError, authorize, override
from claim_agent.orchestrator import assess_claim
from helpers import STORE, store_without_balances


class HumanReviewTest(unittest.TestCase):
    def test_authorize_approval(self):
        a = assess_claim("CLM-APP-001", STORE)
        record = authorize(a.report, a.audit, "assessor.jane")
        self.assertEqual(record["authorization_status"], "APPROVED")
        self.assertEqual(record["decision"], "AUTHORIZED")
        self.assertEqual(record["reviewer"], "assessor.jane")
        self.assertTrue(record["reviewed_at"])
        last = a.audit.events[-1]
        self.assertEqual((last.event, last.name), ("HUMAN_REVIEW", "AUTHORIZED"))

    def test_authorize_rejection_records_rejected(self):
        a = assess_claim("CLM-REJ-001", STORE)
        self.assertEqual(authorize(a.report, a.audit, "senior.lee")["authorization_status"], "REJECTED")

    def test_override_requires_reason(self):
        a = assess_claim("CLM-REJ-001", STORE)
        with self.assertRaises(ReviewError):
            override(a.report, a.audit, "senior.lee", "APPROVE", " ")

    def test_override_is_recorded_with_reason(self):
        a = assess_claim("CLM-REJ-001", STORE)
        record = override(a.report, a.audit, "senior.lee", "APPROVE", "Functional impairment confirmed by ENT letter received by phone.")
        self.assertEqual((record["authorization_status"], record["decision"]), ("APPROVED", "OVERRIDDEN"))
        self.assertEqual(a.audit.events[-1].reason, record["reason"])

    def test_escalated_assessment_cannot_be_authorized(self):
        a = assess_claim("CLM-APP-001", store_without_balances())
        with self.assertRaises(ReviewError):
            authorize(a.report, a.audit, "assessor.jane")

    def test_reviewer_is_required(self):
        a = assess_claim("CLM-APP-001", STORE)
        with self.assertRaises(ReviewError):
            authorize(a.report, a.audit, "")

    def test_cannot_review_twice(self):
        a = assess_claim("CLM-APP-001", STORE)
        authorize(a.report, a.audit, "assessor.jane")
        with self.assertRaises(ReviewError):
            override(a.report, a.audit, "assessor.kim", "REJECT", "Second opinion.")


if __name__ == "__main__":
    unittest.main()
