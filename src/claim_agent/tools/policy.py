"""lookupPolicy(policyId): period, member, benefit, waiting-period, exclusion, cost-sharing and limit checks, with policy version and exact clauses."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from claim_agent.context import AssessmentContext
from claim_agent.fixtures import Record

TOOL_VERSION = "lookupPolicy/1.0"


@dataclass
class Check:
    result: str  # PASS | FAIL | UNCERTAIN
    fact: str
    clause_ids: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    rule_ids: List[str] = field(default_factory=list)  # entries from a separate rule source, e.g. submission deadlines


@dataclass
class PolicyResult:
    policy_id: str
    status: str  # FOUND | UNRESOLVED
    version: Optional[str] = None
    policy_document: Optional[str] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    currency: Optional[str] = None
    policyholder: Optional[Record] = None  # who signed the contract; may or may not be an insured member
    checks: Dict[str, Check] = field(default_factory=dict)
    clauses: Dict[str, Record] = field(default_factory=dict)
    benefit: Optional[Record] = None
    remaining_limit: Optional[Decimal] = None
    ledger_ref: Optional[str] = None
    document_requirement_clause_ids: Dict[str, str] = field(default_factory=dict)
    rules: Dict[str, Record] = field(default_factory=dict)  # rule_id -> rule text, version and source, for citations
    reason: Optional[str] = None


def evaluate_exclusions(policy: Record, context: AssessmentContext) -> Check:
    """Apply exclusions only when verified facts establish them; otherwise PASS or UNCERTAIN."""
    exclusions = policy.get("exclusions", [])
    classification = context.fact("procedure_classification")
    if classification is None:
        return Check("UNCERTAIN", "No verified procedure classification; exclusions cannot be assessed.")
    matching = [e for e in exclusions if e["category"] == classification.value]
    if not matching:
        return Check(
            "PASS",
            f"Verified procedure classification {classification.value} matches no exclusion.",
            [e["clause_id"] for e in exclusions],
            [classification.document_id],
        )
    clause_ids = [e["clause_id"] for e in matching]
    indication = context.fact("medical_indication_present")
    if indication is not None and indication.value is False:
        return Check(
            "FAIL",
            f"Verified procedure classification {classification.value} with no documented medical indication.",
            clause_ids,
            sorted({classification.document_id, indication.document_id}),
        )
    return Check(
        "UNCERTAIN",
        f"Procedure classified {classification.value}, but absence of medical indication is not documented.",
        clause_ids,
        [classification.document_id],
    )


SUPPORTED_ANCHORS = {"LAST_TREATMENT_OR_DISCHARGE_DATE", "CHILDBIRTH_OR_TREATMENT_COMPLETION_DATE"}


def rule_citation(rule_set: Record, deadline: Record) -> Record:
    return {
        "rule_id": deadline["deadline_id"],
        "rule_set_id": rule_set["rule_set_id"],
        "version": rule_set["version"],
        "effective_from": rule_set["effective_from"],
        "source_document": rule_set["source"]["document"],
        "location": deadline["location"],
        "exact_text": deadline["exact_text"],
    }


def evaluate_submission_deadline(context: AssessmentContext) -> Tuple[Check, Optional[Record]]:
    """Look up the reimbursement deadline in submission_deadlines.json; returns the check and the cited rule."""
    rule_set = context.store.submission_rule_set(context.policy_id)
    if rule_set is None:
        return Check("UNCERTAIN", f"No claim submission rules found for policy {context.policy_id}."), None
    source = f"rule_set:{rule_set['rule_set_id']}"
    if context.claim_mode is None:
        return Check("UNCERTAIN", "Claim mode not stated; cannot tell whether the reimbursement deadline applies.", evidence=[source]), None
    if context.claim_mode != rule_set["applies_to_claim_mode"]:
        return Check(
            "PASS", f"{context.claim_mode} claim; the {rule_set['applies_to_claim_mode']} submission deadline does not apply.",
            evidence=[source],
        ), None
    deadline = next((d for d in rule_set["deadlines"] if context.claim_type in d["claim_types"]), None)
    if deadline is None:
        return Check("UNCERTAIN", f"No submission deadline defined for {context.claim_type} claims.", evidence=[source]), None
    if deadline["anchor"] not in SUPPORTED_ANCHORS:
        return Check("UNCERTAIN", f"Unsupported deadline anchor {deadline['anchor']}.", evidence=[source]), None
    # Both anchors resolve to treatment_end: the last treatment / discharge date, or completion of maternity treatment.
    due = context.treatment_end + timedelta(days=deadline["days"])
    elapsed = (context.submission_date - context.treatment_end).days
    check = Check(
        "PASS" if context.submission_date <= due else "FAIL",
        f"Submitted {context.submission_date}, {elapsed} days after last treatment {context.treatment_end}; "
        f"{context.claim_type} deadline {deadline['days']} days ({due}).",
        evidence=[source, f"claim_submission:{context.claim_id}"],
        rule_ids=[deadline["deadline_id"]],
    )
    return check, rule_citation(rule_set, deadline)


def _within(start: date, end: date, period_from: str, period_to: str) -> bool:
    return date.fromisoformat(period_from) <= start and end <= date.fromisoformat(period_to)


def lookup_policy(policy_id: str, context: AssessmentContext) -> PolicyResult:
    """Return status FOUND with PASS/FAIL/UNCERTAIN checks and exact clauses, or UNRESOLVED."""
    policy = context.store.policy(policy_id)
    if policy is None:
        return PolicyResult(policy_id, "UNRESOLVED", reason=f"Policy {policy_id} was not found.")

    start, end = context.treatment_start, context.treatment_end
    record = f"policy_record:{policy_id}"
    checks: Dict[str, Check] = {}

    active = policy["status"] == "ACTIVE" and _within(start, end, policy["effective_from"], policy["effective_to"])
    checks["policy_active"] = Check(
        "PASS" if active else "FAIL",
        f"Policy {policy['status']} {policy['effective_from']} to {policy['effective_to']}; treatment {start} to {end}.",
        [policy["period_clause_id"]],
        [record],
    )

    member = next((m for m in policy["members"] if m["member_id"] == context.member_id), None)
    member_ok = member is not None and _within(start, end, member["coverage_start"], member["coverage_end"])
    checks["member_covered"] = Check(
        "PASS" if member_ok else "FAIL",
        f"Member {context.member_id} " + (
            f"covered {member['coverage_start']} to {member['coverage_end']}." if member else "is not named on the policy."
        ),
        [policy["member_clause_id"]],
        [record],
    )

    benefit = policy["benefits"].get(context.claim_type)
    if benefit is None:
        checks["benefit_covered"] = Check(
            "UNCERTAIN", f"Policy has no {context.claim_type} benefit entry; coverage cannot be established.", [], [record]
        )
    else:
        checks["benefit_covered"] = Check(
            "PASS" if benefit["covered"] else "FAIL",
            f"{context.claim_type} benefit {'included' if benefit['covered'] else 'not included'}.",
            [benefit["benefit_clause_id"]],
            [record],
        )

    if benefit is None or member is None:
        checks["waiting_period"] = Check("UNCERTAIN", "Benefit or member record unavailable.", [], [record])
    else:
        days = benefit["waiting_period_days"]
        satisfied_from = date.fromisoformat(member["coverage_start"]) + timedelta(days=days)
        checks["waiting_period"] = Check(
            "PASS" if start >= satisfied_from else "FAIL",
            f"{days}-day waiting period from {member['coverage_start']} satisfied from {satisfied_from}; treatment {start}.",
            [benefit["waiting_period_clause_id"]],
            [record],
        )

    checks["submission_deadline"], deadline_rule = evaluate_submission_deadline(context)
    checks["exclusions"] = evaluate_exclusions(policy, context)

    balance = context.store.balance(policy_id, context.member_id, context.claim_type)
    limit_clauses = [benefit["limit_clause_id"]] if benefit else []
    remaining = None
    if balance is None:
        checks["limit"] = Check("UNCERTAIN", "No benefit balance record found.", limit_clauses, [])
    else:
        remaining = Decimal(balance["remaining"])
        checks["limit"] = Check(
            "PASS" if remaining > 0 else "FAIL",
            f"Remaining {context.claim_type} limit {balance['currency']} {balance['remaining']} of {balance['annual_limit']} as of {balance['as_of']}.",
            limit_clauses,
            [f"ledger:{balance['ledger_ref']}"],
        )

    return PolicyResult(
        policy_id=policy_id,
        status="FOUND",
        version=policy["version"],
        policy_document=policy["policy_document"],
        effective_from=policy["effective_from"],
        effective_to=policy["effective_to"],
        currency=policy["currency"],
        policyholder=dict(policy["policyholder"]) if policy.get("policyholder") else None,
        checks=checks,
        clauses={c["clause_id"]: dict(c) for c in policy["clauses"]},
        benefit=dict(benefit) if benefit else None,
        remaining_limit=remaining,
        ledger_ref=balance["ledger_ref"] if balance else None,
        document_requirement_clause_ids=dict(policy.get("document_requirement_clause_ids", {})),
        rules={deadline_rule["rule_id"]: deadline_rule} if deadline_rule else {},
    )
