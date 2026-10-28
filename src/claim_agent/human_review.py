"""Human review: records authorization or override with reviewer, decision, reason and time. Final authorization stays PENDING until then."""

from __future__ import annotations

from typing import Any, Dict, Optional

from claim_agent.audit import AuditTrail

FINAL_STATUS = {"APPROVE": "APPROVED", "REJECT": "REJECTED", "REQUEST_MORE_INFO": "INFORMATION_REQUESTED"}


class ReviewError(ValueError):
    """The review action is not allowed for this report."""


def _record(report: Dict[str, Any], audit: AuditTrail, reviewer: str, decision: str, outcome: str, reason: Optional[str]) -> Dict[str, Any]:
    if not reviewer or not reviewer.strip():
        raise ReviewError("A named reviewer is required.")
    if report["human_review"]["authorization_status"] != "PENDING":
        raise ReviewError("This assessment has already been reviewed.")
    event = audit.record(
        "HUMAN_REVIEW", decision, "RECORDED",
        input={"reviewer": reviewer, "recommendation": report["recommendation"]["outcome"], "final_outcome": outcome},
        reason=reason,
    )
    report["human_review"] = {
        "authorization_status": FINAL_STATUS[outcome],
        "reviewer": reviewer,
        "decision": decision,
        "final_outcome": outcome,
        "reason": reason,
        "reviewed_at": event.timestamp,
    }
    return report["human_review"]


def authorize(report: Dict[str, Any], audit: AuditTrail, reviewer: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """Accept the agent's recommendation as the final decision."""
    outcome = report["recommendation"]["outcome"]
    if outcome is None:
        raise ReviewError("No recommendation to authorize; the assessment is escalated. Use override with a reason.")
    if report.get("validation", {}).get("status") != "PASS":
        raise ReviewError("The report failed validation; only an override with a reason is allowed.")
    return _record(report, audit, reviewer, "AUTHORIZED", outcome, reason)


def override(report: Dict[str, Any], audit: AuditTrail, reviewer: str, final_outcome: str, reason: str) -> Dict[str, Any]:
    """Replace the recommendation with the reviewer's own decision. A reason is mandatory."""
    if final_outcome not in FINAL_STATUS:
        raise ReviewError(f"Final outcome must be one of {sorted(FINAL_STATUS)}.")
    if not reason or not reason.strip():
        raise ReviewError("An override requires a reason.")
    return _record(report, audit, reviewer, "OVERRIDDEN", final_outcome, reason)
