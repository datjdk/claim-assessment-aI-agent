"""Decision engine: explicit guardrail rules mapping verified results to APPROVE, REJECT or REQUEST_MORE_INFO (or pending review).

Order of rules:
1. REJECT when a specific denial basis is established by evidence and an applicable policy clause.
2. REQUEST_MORE_INFO when checklist evidence is missing or incomplete.
3. Pending review (outcome None, ESCALATED) when anything else is unresolved.
4. APPROVE only when every check passes, medical necessity is SUPPORTED and the calculation is complete.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from claim_agent.document_review import DocumentReview, InformationRequest
from claim_agent.tools.benefit import BenefitResult
from claim_agent.tools.medical import MedicalResult
from claim_agent.tools.policy import PolicyResult

CHECK_LABELS = {
    "policy_active": "Policy active on treatment date",
    "member_covered": "Member covered",
    "benefit_covered": "Claim type / benefit covered",
    "waiting_period": "Waiting period",
    "submission_deadline": "Claim submitted within deadline",
    "exclusions": "Exclusions",
    "limit": "Remaining benefit limit",
}
DENIAL_CHECKS = ("policy_active", "member_covered", "benefit_covered", "waiting_period", "submission_deadline", "exclusions", "limit")


@dataclass
class Reason:
    finding: str
    evidence: List[str]
    policy_clause_ids: List[str] = field(default_factory=list)
    checklist_requirement_ids: List[str] = field(default_factory=list)
    rule_ids: List[str] = field(default_factory=list)


@dataclass
class Decision:
    outcome: Optional[str]  # APPROVE | REJECT | REQUEST_MORE_INFO | None (pending review)
    assessment_status: str  # READY_FOR_AUTHORIZATION | PENDING_INFORMATION | ESCALATED
    reasons: List[Reason]
    information_requests: List[InformationRequest]
    escalations: List[str]
    next_action: str
    authorization_owner: str
    recommended_payable: Optional[Decimal]


def _medical_clause(policy: PolicyResult) -> List[str]:
    return [policy.benefit["medical_necessity_clause_id"]] if policy.benefit else []


def _medical_evidence(medical: MedicalResult) -> List[str]:
    refs = list(dict.fromkeys(f.document_id for f in medical.evidence))
    if medical.rule_id:
        refs.append(f"clinical_rule:{medical.rule_id}")
    return refs


def _benefit_reason(benefit: BenefitResult) -> Reason:
    return Reason(
        f"Calculation: {benefit.currency} {benefit.submitted} submitted, {benefit.excluded} excluded, "
        f"{benefit.insurer_payable} insurer payable, {benefit.member_responsibility} member responsibility; "
        f"remaining limit {benefit.remaining_limit_before} -> {benefit.remaining_limit_after}.",
        benefit.evidence,
        benefit.clause_ids,
    )


def _escalations(review: DocumentReview, policy: PolicyResult, medical: MedicalResult, benefit: BenefitResult) -> List[str]:
    items = [f"Document consistency: {i}" for i in review.consistency_issues]
    if policy.status != "FOUND":
        items.append(f"Policy record unavailable: {policy.reason}")
    else:
        items += [f"{CHECK_LABELS[n]} uncertain: {c.fact}" for n, c in policy.checks.items() if c.result == "UNCERTAIN"]
    if medical.result in ("INSUFFICIENT_EVIDENCE", "REFER_TO_MEDICAL_REVIEW"):
        items.append(f"Medical necessity {medical.result}: {medical.reason or medical.rationale}")
    if benefit.status != "COMPLETE":
        items.append("Benefit calculation PENDING: " + "; ".join(benefit.pending_reasons))
    return items


def decide(review: DocumentReview, policy: PolicyResult, medical: MedicalResult, benefit: BenefitResult) -> Decision:
    escalations = _escalations(review, policy, medical, benefit)

    denials: List[Reason] = []
    if policy.status == "FOUND":
        for name in DENIAL_CHECKS:
            check = policy.checks[name]
            if check.result == "FAIL" and (check.clause_ids or check.rule_ids) and check.evidence:
                denials.append(Reason(
                    f"{CHECK_LABELS[name]} failed: {check.fact}", check.evidence, check.clause_ids, rule_ids=check.rule_ids
                ))
        if medical.result == "NOT_SUPPORTED" and _medical_clause(policy) and medical.evidence:
            denials.append(Reason(
                f"Medical necessity NOT_SUPPORTED ({medical.rule_id}): {medical.rationale}",
                _medical_evidence(medical),
                _medical_clause(policy),
            ))
    if denials:
        if benefit.status == "COMPLETE":
            denials.append(_benefit_reason(benefit))
        return Decision(
            "REJECT", "READY_FOR_AUTHORIZATION", denials, [], escalations,
            "Route to human denial review; the denial notice must cite the clauses above.",
            "Senior claims assessor (denial review)",
            benefit.insurer_payable if benefit.status == "COMPLETE" else None,
        )

    if review.requests:
        reasons = []
        for req in review.requests:
            row = review.row_for(req.required_item)
            evidence = (row.evidence if row and row.evidence else []) or [f"claim_submission:{review.claim_id}"]
            reasons.append(Reason(
                f"{req.required_item} needed: {req.why_needed}",
                evidence,
                [req.policy_clause_id] if req.policy_clause_id else [],
                [req.requirement_id],
            ))
        return Decision(
            "REQUEST_MORE_INFO", "PENDING_INFORMATION", reasons, review.requests, escalations,
            "Send the information requests; hold the claim as PENDING_INFORMATION and reassess on receipt.",
            "Claims assessor",
            None,
        )

    approvable = (
        policy.status == "FOUND"
        and all(c.result == "PASS" for c in policy.checks.values())
        and medical.result == "SUPPORTED"
        and benefit.status == "COMPLETE"
        and review.conclusion == "COMPLETE"
        and benefit.insurer_payable <= benefit.remaining_limit_before
    )
    if not approvable or escalations:
        return Decision(
            None, "ESCALATED", [], [], escalations or ["Approval conditions not met."],
            "Hold for specialist review; do not approve or reject until the escalations are resolved.",
            "Claims supervisor / medical reviewer",
            None,
        )

    checks = policy.checks
    reasons = [
        Reason(
            f"Coverage established: {checks['policy_active'].fact} {checks['member_covered'].fact}",
            sorted(set(checks["policy_active"].evidence + checks["member_covered"].evidence)),
            checks["policy_active"].clause_ids + checks["member_covered"].clause_ids,
        ),
        Reason(
            f"Submitted on time: {checks['submission_deadline'].fact}",
            checks["submission_deadline"].evidence,
            checks["submission_deadline"].clause_ids,
            rule_ids=checks["submission_deadline"].rule_ids,
        ),
        Reason(
            f"Benefit applies: {checks['benefit_covered'].fact} {checks['waiting_period'].fact} {checks['exclusions'].fact}",
            sorted(set(checks["benefit_covered"].evidence + checks["waiting_period"].evidence + checks["exclusions"].evidence)),
            checks["benefit_covered"].clause_ids + checks["waiting_period"].clause_ids + checks["exclusions"].clause_ids,
        ),
        Reason(
            f"Medical necessity SUPPORTED ({medical.rule_id}): {medical.rationale}",
            _medical_evidence(medical),
            _medical_clause(policy),
        ),
        _benefit_reason(benefit),
    ]
    return Decision(
        "APPROVE", "READY_FOR_AUTHORIZATION", reasons, [], [],
        f"Send to an authorized approver to authorize payment of {benefit.currency} {benefit.insurer_payable}.",
        "Claims approver",
        benefit.insurer_payable,
    )
