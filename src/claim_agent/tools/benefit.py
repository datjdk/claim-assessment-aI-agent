"""calculateBenefit(policyId, claimType, amount): Decimal-only benefit calculation, or PENDING with null amounts when inputs are unresolved."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from claim_agent.context import AssessmentContext
from claim_agent.tools.policy import evaluate_exclusions

TOOL_VERSION = "calculateBenefit/1.0"
SUPPORTED_ORDER = ["EXCLUSIONS", "DEDUCTIBLE", "COPAY", "COINSURANCE", "ANNUAL_LIMIT"]
ZERO = Decimal("0.00")


@dataclass
class BenefitResult:
    status: str  # COMPLETE | PENDING
    policy_id: str
    claim_type: str
    currency: Optional[str]
    submitted: Optional[Decimal]
    excluded: Optional[Decimal] = None
    eligible: Optional[Decimal] = None
    deductible: Optional[Decimal] = None
    copay: Optional[Decimal] = None
    coinsurance: Optional[Decimal] = None
    limit_adjustment: Optional[Decimal] = None
    insurer_payable: Optional[Decimal] = None
    member_responsibility: Optional[Decimal] = None
    remaining_limit_before: Optional[Decimal] = None
    remaining_limit_after: Optional[Decimal] = None
    steps: List[Dict[str, Any]] = field(default_factory=list)
    clause_ids: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    pending_reasons: List[str] = field(default_factory=list)


def _unique(items):
    return list(dict.fromkeys(i for i in items if i))


def calculate_benefit(policy_id: str, claim_type: str, amount: str, context: AssessmentContext) -> BenefitResult:
    """Return status COMPLETE with every amount, or PENDING with unresolved amounts as None."""
    if not isinstance(amount, (str, Decimal)):
        raise TypeError("amount must be a decimal string or Decimal, never a float.")
    try:
        submitted = Decimal(amount)
    except InvalidOperation as e:
        raise ValueError(f"amount '{amount}' is not a decimal number.") from e

    store = context.store
    policy = store.policy(policy_id)
    benefit = policy["benefits"].get(claim_type) if policy else None
    balance = store.balance(policy_id, context.member_id, claim_type)
    invoice_total = context.fact("invoice_total")
    visits = context.fact("visit_count")

    pending = []
    if policy is None:
        pending.append(f"Policy {policy_id} was not found.")
    elif benefit is None:
        pending.append(f"Policy has no {claim_type} benefit terms.")
    elif policy["calculation_order"] != SUPPORTED_ORDER:
        pending.append(f"Unsupported calculation order {policy['calculation_order']}.")
    if balance is None:
        pending.append("No benefit balance record found.")
    if invoice_total is None:
        pending.append("Invoice total is not verified.")
    elif Decimal(invoice_total.value) != submitted:
        pending.append(f"Amount {submitted} does not match verified invoice total {invoice_total.value}.")
    if visits is None:
        pending.append("Visit count is not verified.")
    if submitted != context.submitted_amount:
        pending.append(f"Amount {submitted} does not match the claimed amount {context.submitted_amount}.")
    exclusion = evaluate_exclusions(policy, context) if policy else None
    if exclusion is not None and exclusion.result == "UNCERTAIN":
        pending.append(f"Exclusions unresolved: {exclusion.fact}")

    if pending:
        return BenefitResult("PENDING", policy_id, claim_type, context.currency, submitted, pending_reasons=pending)

    places = Decimal(1).scaleb(-policy["rounding"]["decimal_places"])

    def money(value: Decimal) -> Decimal:
        return value.quantize(places, rounding=ROUND_HALF_UP)

    excluded = money(submitted) if exclusion.result == "FAIL" else ZERO
    eligible = money(submitted - excluded)
    deductible = money(min(Decimal(benefit["deductible"]), eligible))
    copay = money(min(Decimal(benefit["copay_per_visit"]) * int(visits.value), eligible - deductible))
    coinsurance = money((eligible - deductible - copay) * Decimal(benefit["coinsurance_rate"]))
    covered = eligible - deductible - copay - coinsurance
    remaining = Decimal(balance["remaining"])
    payable = money(min(covered, remaining))
    limit_adjustment = money(covered - payable)

    steps = [
        {"step": "EXCLUSIONS", "amount": excluded, "detail": exclusion.fact},
        {"step": "DEDUCTIBLE", "amount": deductible, "detail": f"Deductible {benefit['deductible']}."},
        {"step": "COPAY", "amount": copay, "detail": f"Copay {benefit['copay_per_visit']} x {visits.value} visit(s), capped at the amount left."},
        {"step": "COINSURANCE", "amount": coinsurance, "detail": f"Coinsurance rate {benefit['coinsurance_rate']}."},
        {"step": "ANNUAL_LIMIT", "amount": limit_adjustment, "detail": f"Payable capped at remaining limit {balance['remaining']}."},
    ]
    clause_ids = _unique(
        (exclusion.clause_ids if exclusion.result == "FAIL" else [])
        + [benefit["deductible_clause_id"], benefit["copay_clause_id"], benefit["coinsurance_clause_id"], benefit["limit_clause_id"]]
    )
    return BenefitResult(
        status="COMPLETE",
        policy_id=policy_id,
        claim_type=claim_type,
        currency=context.currency,
        submitted=money(submitted),
        excluded=excluded,
        eligible=eligible,
        deductible=deductible,
        copay=copay,
        coinsurance=coinsurance,
        limit_adjustment=limit_adjustment,
        insurer_payable=payable,
        member_responsibility=money(submitted - payable),
        remaining_limit_before=money(remaining),
        remaining_limit_after=money(remaining - payable),
        steps=steps,
        clause_ids=clause_ids,
        evidence=_unique([invoice_total.document_id, visits.document_id, f"ledger:{balance['ledger_ref']}"] + exclusion.evidence),
    )
