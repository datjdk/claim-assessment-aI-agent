"""Report builder: the six report sections plus metadata, assembled only from verified results and citations.

Amounts are decimal strings; unresolved amounts are null, never zero.
"""

from __future__ import annotations

from typing import Any, Dict, List

from claim_agent.context import AssessmentContext
from claim_agent.decision import CHECK_LABELS, Decision
from claim_agent.document_review import DocumentReview
from claim_agent.serialize import to_jsonable
from claim_agent.tools.benefit import BenefitResult
from claim_agent.tools.medical import MedicalResult
from claim_agent.tools.policy import PolicyResult

NOTICE = "Prototype assessment of FICTIONAL claim data. Recommendation only; final authorization belongs to a human."
EXPLANATION_SECTIONS = ["document_review", "policy_verification", "medical_necessity", "benefit_calculation", "recommendation"]
AMOUNT_FIELDS = (
    "submitted", "excluded", "eligible", "deductible", "copay", "coinsurance", "limit_adjustment",
    "insurer_payable", "member_responsibility", "remaining_limit_before", "remaining_limit_after",
)


class CitationRegistry:
    """Assigns PC-nn IDs to each policy clause or checklist requirement the report relies on."""

    def __init__(self, policy: PolicyResult, review: DocumentReview, context: AssessmentContext):
        self.policy = policy
        self.review = review
        self.requirements = {r["requirement_id"]: r for r in (context.checklist or {}).get("requirements", [])}
        self.entries: Dict[str, Dict[str, Any]] = {}

    def _add(self, key: str, entry: Dict[str, Any], finding: str, evidence: List[str]) -> str:
        if key not in self.entries:
            entry["citation_id"] = f"PC-{len(self.entries) + 1:02d}"
            entry["supported_findings"] = []
            entry["evidence_ids"] = []
            self.entries[key] = entry
        cited = self.entries[key]
        if finding not in cited["supported_findings"]:
            cited["supported_findings"].append(finding)
        for e in evidence:
            if e not in cited["evidence_ids"]:
                cited["evidence_ids"].append(e)
        return cited["citation_id"]

    def clause(self, clause_id: str, finding: str, evidence: List[str]) -> str:
        clause = self.policy.clauses.get(clause_id)
        return self._add(f"POLICY:{clause_id}", {
            "kind": "POLICY",
            "source_document": self.policy.policy_document,
            "version": self.policy.version,
            "effective_date": self.policy.effective_from,
            "clause_id": clause_id,
            "title": clause["title"] if clause else None,
            "location": clause["location"] if clause else None,
            "text": clause["exact_text"] if clause else None,
        }, finding, evidence)

    def requirement(self, requirement_id: str, finding: str, evidence: List[str]) -> str:
        req = self.requirements.get(requirement_id)
        source = self.review.checklist_source or {}
        return self._add(f"CHECKLIST:{requirement_id}", {
            "kind": "PROCEDURAL",
            "source_document": source.get("document"),
            "version": source.get("version"),
            "effective_date": None,
            "clause_id": requirement_id,
            "title": f"{self.review.checklist_id} {req['document_type']}" if req else None,
            "location": source.get("location"),
            "text": f"{req['document_type']} is {req['requirement']}: {req['purpose']}" if req else None,
        }, finding, evidence)

    def rule(self, rule_id: str, finding: str, evidence: List[str]) -> str:
        rule = self.policy.rules.get(rule_id)
        return self._add(f"RULE:{rule_id}", {
            "kind": "RULE",
            "source_document": rule["source_document"] if rule else None,
            "version": rule["version"] if rule else None,
            "effective_date": rule["effective_from"] if rule else None,
            "clause_id": rule_id,
            "title": rule["rule_set_id"] if rule else None,
            "location": rule["location"] if rule else None,
            "text": rule["exact_text"] if rule else None,
        }, finding, evidence)

    def cite_all(
        self, clause_ids: List[str], requirement_ids: List[str], finding: str, evidence: List[str], rule_ids: List[str] = ()
    ) -> List[str]:
        return (
            [self.clause(c, finding, evidence) for c in clause_ids]
            + [self.requirement(r, finding, evidence) for r in requirement_ids]
            + [self.rule(r, finding, evidence) for r in rule_ids]
        )


def _policy_conclusion(policy: PolicyResult) -> str:
    if policy.status != "FOUND":
        return "UNDETERMINED"
    results = [c.result for c in policy.checks.values()]
    if "FAIL" in results:
        return "INELIGIBLE"
    return "UNDETERMINED" if "UNCERTAIN" in results else "ELIGIBLE"


def _fact_summary(context: AssessmentContext, name: str) -> Dict[str, Any]:
    fact = context.fact(name)
    if fact is None:
        return {"value": None, "verified": False, "source": None}
    return {"value": fact.value, "verified": True, "source": f"{fact.document_id} {fact.location}"}


def build_report(
    context: AssessmentContext,
    review: DocumentReview,
    policy: PolicyResult,
    medical: MedicalResult,
    benefit: BenefitResult,
    decision: Decision,
    *,
    assessment_id: str,
    assessed_at: str,
    audit_reference: str,
    tool_versions: Dict[str, str],
) -> Dict[str, Any]:
    cites = CitationRegistry(policy, review, context)

    rows = []
    for row in review.rows:
        data = to_jsonable(row)
        data["citation_ids"] = (
            [cites.requirement(row.requirement_id, f"Document requirement {row.document_type}", row.evidence)]
            if row.requirement_id else []
        )
        rows.append(data)

    checks = []
    for name, check in policy.checks.items():
        checks.append({
            "check": name,
            "label": CHECK_LABELS[name],
            "result": check.result,
            "verified_fact": check.fact,
            "clause_ids": check.clause_ids,
            "rule_ids": check.rule_ids,
            "citation_ids": cites.cite_all(check.clause_ids, [], CHECK_LABELS[name], check.evidence, check.rule_ids),
            "evidence": check.evidence,
        })

    medical_clauses = [policy.benefit["medical_necessity_clause_id"]] if policy.benefit else []
    medical_evidence = list(dict.fromkeys(f.document_id for f in medical.evidence))
    benefit_data = {name: to_jsonable(getattr(benefit, name)) for name in AMOUNT_FIELDS}
    reasons = [
        {
            "finding": r.finding,
            "evidence": r.evidence,
            "citation_ids": cites.cite_all(r.policy_clause_ids, r.checklist_requirement_ids, r.finding, r.evidence, r.rule_ids),
        }
        for r in decision.reasons
    ]

    report = {
        "notice": NOTICE,
        "metadata": {
            "claim_id": context.claim_id,
            "assessment_id": assessment_id,
            "assessor": "claim-agent (automated initial assessment)",
            "assessment_date": assessed_at,
            "policy_id": context.policy_id,
            "policy_version": policy.version,
            "policyholder": policy.policyholder,
            "claim_type": context.claim_type,
            "member_id": context.member_id,
            "treatment_dates": {"start": context.treatment_start.isoformat(), "end": context.treatment_end.isoformat()},
            "verified_diagnosis": _fact_summary(context, "diagnosis"),
            "verified_procedures": _fact_summary(context, "procedures"),
            "reported_diagnosis": context.claim.get("reported_diagnosis"),
            "reported_procedures": context.claim.get("reported_procedures"),
            "submitted_amount": str(context.submitted_amount),
            "currency": context.currency,
            "context_version": context.context_version,
            "tool_versions": tool_versions,
        },
        "document_review": {
            "checklist": {"id": review.checklist_id, "version": review.checklist_version, "source": review.checklist_source},
            "rows": rows,
            "conclusion": review.conclusion,
            "outstanding_requests": to_jsonable(review.requests),
            "consistency_issues": review.consistency_issues,
        },
        "policy_verification": {
            "status": policy.status,
            "policy_document": policy.policy_document,
            "version": policy.version,
            "checks": checks,
            "remaining_limit": to_jsonable(policy.remaining_limit),
            "conclusion": _policy_conclusion(policy),
            "reason": policy.reason,
        },
        "medical_necessity": {
            "diagnosis": medical.diagnosis,
            "procedures": medical.procedures,
            "result": medical.result,
            "rule_id": medical.rule_id,
            "rationale": medical.rationale,
            "clinical_source": f"{medical.source} {medical.source_location}" if medical.source_location else medical.source,
            "rule_set_version": medical.rule_set_version,
            "policy_clause_ids": medical_clauses,
            "citation_ids": [cites.clause(c, "Medical necessity", medical_evidence) for c in medical_clauses],
            "evidence": [to_jsonable(f) for f in medical.evidence],
            "outstanding_concerns": [medical.reason] if medical.reason else [],
        },
        "benefit_calculation": {
            "status": benefit.status,
            "currency": benefit.currency,
            **benefit_data,
            "steps": to_jsonable(benefit.steps),
            "clause_ids": benefit.clause_ids,
            "citation_ids": [cites.clause(c, "Benefit calculation", benefit.evidence) for c in benefit.clause_ids],
            "evidence": benefit.evidence,
            "pending_reasons": benefit.pending_reasons,
        },
        "recommendation": {
            "outcome": decision.outcome,
            "recommended_payable": to_jsonable(decision.recommended_payable),
            "reasons": reasons,
            "information_requests": to_jsonable(decision.information_requests),
            "escalations": decision.escalations,
            "next_action": decision.next_action,
            "authorization_owner": decision.authorization_owner,
        },
        "policy_citations": {"citations": list(cites.entries.values())},
        "assessment_status": decision.assessment_status,
        "audit_reference": audit_reference,
        "explanations": {"status": "NOT_REQUESTED", "sections": {}},
        "human_review": {
            "authorization_status": "PENDING",
            "reviewer": None,
            "decision": None,
            "final_outcome": None,
            "reason": None,
            "reviewed_at": None,
        },
    }
    return report


def explanation_facts(report: Dict[str, Any]) -> Dict[str, Any]:
    """The verified report content the LLM may draw on. No names or free-text claimant input."""
    facts = {"claim_id": report["metadata"]["claim_id"], "currency": report["metadata"]["currency"]}
    for key in EXPLANATION_SECTIONS + ["policy_citations"]:
        facts[key] = report[key]
    return facts
