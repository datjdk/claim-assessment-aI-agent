"""Server-controlled assessment context: claim, member, treatment dates, checklist and verified policy/benefit data.

Supplies inputs the public tool signatures do not carry. Claimant-reported diagnosis and
procedures stay on `claim` only; `verified_facts` holds facts the orchestrator has accepted
from document review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

from claim_agent.fixtures import FixtureStore, Record

CONTEXT_SCHEMA_VERSION = "1"


class ClaimValidationError(ValueError):
    """The claim cannot be loaded or fails intake validation."""


@dataclass(frozen=True)
class Fact:
    value: Any
    document_id: str
    location: str


@dataclass
class AssessmentContext:
    claim: Record
    claim_id: str
    policy_id: str
    member_id: str
    claim_type: str
    treatment_start: date
    treatment_end: date
    submission_date: date
    claim_mode: Optional[str]  # REIMBURSEMENT | DIRECT_BILLING | None when not stated
    submitted_amount: Decimal
    currency: str
    checklist: Optional[Record]
    store: FixtureStore
    context_version: str
    verified_facts: Dict[str, Fact] = field(default_factory=dict)

    def record_fact(self, name: str, value: Any, document_id: str, location: str) -> None:
        self.verified_facts[name] = Fact(value, document_id, location)

    def fact(self, name: str) -> Optional[Fact]:
        return self.verified_facts.get(name)


def _required_text(claim: Record, key: str) -> str:
    value = claim.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ClaimValidationError(f"Claim field '{key}' is missing or empty.")
    return value


def _parse_date(value: Any, label: str) -> date:
    if not isinstance(value, str):
        raise ClaimValidationError(f"{label} must be an ISO date string.")
    try:
        return date.fromisoformat(value)
    except ValueError as e:
        raise ClaimValidationError(f"{label} '{value}' is not an ISO date (YYYY-MM-DD).") from e


def _parse_amount(value: Any) -> Decimal:
    # Amounts must be strings so they never pass through binary floating point.
    if not isinstance(value, str) or not value.strip():
        raise ClaimValidationError("Submitted amount must be a non-empty decimal string.")
    try:
        amount = Decimal(value)
    except InvalidOperation as e:
        raise ClaimValidationError(f"Submitted amount '{value}' is not a decimal number.") from e
    if not amount.is_finite() or amount <= 0:
        raise ClaimValidationError(f"Submitted amount '{value}' must be greater than zero.")
    return amount


def create_assessment_context(claim_id: str, store: FixtureStore) -> AssessmentContext:
    """Load and validate the claim, then build its context. Raises ClaimValidationError."""
    claim = store.claim(claim_id)
    if claim is None:
        raise ClaimValidationError(f"Claim '{claim_id}' was not found.")

    dates = claim.get("treatment_dates") or {}
    start = _parse_date(dates.get("start"), "Treatment start date")
    end = _parse_date(dates.get("end"), "Treatment end date")
    if end < start:
        raise ClaimValidationError("Treatment end date is before the start date.")
    submitted_on = _parse_date(claim.get("submission_date"), "Submission date")
    if submitted_on < start:
        raise ClaimValidationError("Submission date is before treatment started.")

    submitted = claim.get("submitted_amount") or {}
    amount = _parse_amount(submitted.get("amount"))
    currency = submitted.get("currency")
    if not isinstance(currency, str) or not currency.strip():
        raise ClaimValidationError("Submitted amount has no currency.")

    documents = claim.get("documents")
    if not documents or not all(isinstance(d, dict) and d.get("document_id") for d in documents):
        raise ClaimValidationError("Claim has no valid document references.")

    claim_type = _required_text(claim, "claim_type")
    versions = ",".join(sorted(set(store.fixture_versions.values())))
    return AssessmentContext(
        claim=claim,
        claim_id=claim_id,
        policy_id=_required_text(claim, "policy_id"),
        member_id=_required_text(claim, "member_id"),
        claim_type=claim_type,
        treatment_start=start,
        treatment_end=end,
        submission_date=submitted_on,
        claim_mode=claim.get("claim_mode"),
        submitted_amount=amount,
        currency=currency,
        checklist=store.checklist(claim_type),
        store=store,
        context_version=f"ctx-{CONTEXT_SCHEMA_VERSION}/fixtures-{versions}",
    )
