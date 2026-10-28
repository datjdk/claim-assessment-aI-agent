"""verifyDocument(documentId): findings for one submitted document; unknowns stay unresolved."""

import unittest

from claim_agent.tools import verify_document
from helpers import context_for


class VerifyDocumentTest(unittest.TestCase):
    def test_returns_complete_medical_report_with_located_facts(self):
        result = verify_document("A-D4", context_for("CLM-APP-001"))
        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.document_id, "A-D4")
        self.assertEqual(result.declared_type, "MEDICAL_REPORT")
        self.assertEqual(result.detected_type, "MEDICAL_REPORT")
        self.assertEqual(result.completeness_status, "COMPLETE")
        self.assertEqual(result.verification_status, "VERIFIED")
        self.assertEqual(result.issues, [])
        diagnosis = result.extracted_facts["diagnosis"]
        self.assertEqual(diagnosis.value, "Acute bacterial sinusitis")
        self.assertEqual(diagnosis.document_id, "A-D4")
        self.assertEqual(diagnosis.location, "p.1, Assessment")

    def test_reports_declared_versus_detected_type_mismatch(self):
        result = verify_document("I-D4", context_for("CLM-RFI-001"))
        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.declared_type, "MEDICAL_REPORT")
        self.assertEqual(result.detected_type, "APPOINTMENT_CONFIRMATION")
        self.assertIn("TYPE_MISMATCH", [issue["code"] for issue in result.issues])
        self.assertNotIn("diagnosis", result.extracted_facts)

    def test_keeps_explicit_null_diagnosis(self):
        result = verify_document("R-D4", context_for("CLM-REJ-001"))
        self.assertIn("diagnosis", result.extracted_facts)
        self.assertIsNone(result.extracted_facts["diagnosis"].value)
        self.assertIs(result.extracted_facts["medical_indication_present"].value, False)

    def test_returns_invoice_line_items(self):
        result = verify_document("A-D2", context_for("CLM-APP-001"))
        lines = result.extracted_facts["line_items"].value
        self.assertEqual([line["line_id"] for line in lines], ["A-D2-L1", "A-D2-L2"])

    def test_unknown_document_is_unresolved(self):
        result = verify_document("X-D9", context_for("CLM-APP-001"))
        self.assertEqual(result.status, "UNRESOLVED")
        self.assertTrue(result.reason)
        self.assertIsNone(result.detected_type)
        self.assertEqual(result.extracted_facts, {})

    def test_document_not_submitted_with_this_claim_is_unresolved(self):
        result = verify_document("R-D4", context_for("CLM-APP-001"))
        self.assertEqual(result.status, "UNRESOLVED")
        self.assertTrue(result.reason)
        self.assertEqual(result.extracted_facts, {})

    def test_does_not_record_facts_into_context(self):
        ctx = context_for("CLM-APP-001")
        verify_document("A-D4", ctx)
        self.assertEqual(ctx.verified_facts, {})


if __name__ == "__main__":
    unittest.main()
