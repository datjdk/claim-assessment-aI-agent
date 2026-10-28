"""Plain-text labels for result codes in human-facing output.

Report data, JSON output and the validator keep the codes (e.g. REQUEST_MORE_INFO); only rendered
text uses these labels.
"""

from __future__ import annotations

from typing import Any

LABELS = {
    # Recommendation and assessment status
    "APPROVE": "Approve",
    "REJECT": "Reject",
    "REQUEST_MORE_INFO": "Request more information",
    "PENDING_REVIEW": "Pending review (no recommendation)",
    "READY_FOR_AUTHORIZATION": "Ready for authorization",
    "PENDING_INFORMATION": "Waiting for information",
    "ESCALATED": "Escalated for review",
    # Final authorization
    "PENDING": "Pending",
    "APPROVED": "Approved",
    "REJECTED": "Rejected",
    "INFORMATION_REQUESTED": "Information requested",
    "AUTHORIZED": "Authorized",
    "OVERRIDDEN": "Overridden",
    # Documents
    "COMPLETE": "Complete",
    "INCOMPLETE": "Incomplete",
    "MISSING": "Missing",
    "NOT_APPLICABLE": "Not applicable",
    "UNRESOLVED_ITEMS": "Unresolved items",
    "VERIFIED": "Verified",
    "NOT_VERIFIED": "Not verified",
    # Policy
    "PASS": "Pass",
    "FAIL": "Fail",
    "UNCERTAIN": "Uncertain",
    "ELIGIBLE": "Eligible",
    "INELIGIBLE": "Not eligible",
    "UNDETERMINED": "Not yet determined",
    "FOUND": "Found",
    "UNRESOLVED": "Unresolved",
    # Medical necessity
    "SUPPORTED": "Supported",
    "NOT_SUPPORTED": "Not supported",
    "INSUFFICIENT_EVIDENCE": "Insufficient evidence",
    "REFER_TO_MEDICAL_REVIEW": "Referred to medical review",
    # Validation and explanations
    "NEEDS_REVIEW": "Needs review",
    "NOT_REQUESTED": "Not requested",
    "DRAFTED": "Drafted",
    "FAILED": "Failed",
}


def label(code: Any) -> str:
    """Plain-text label for a result code; unknown codes fall back to sentence case, None to a dash."""
    if code is None:
        return "—"
    text = str(code)
    return LABELS.get(text, text.replace("_", " ").capitalize() if text.isupper() else text)
