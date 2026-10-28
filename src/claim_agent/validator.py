"""Report validator: schema and enums, calculation reconciliation, evidence links, citation IDs and versions, decision guardrails."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional, Set

from claim_agent.tools.policy import PolicyResult

OUTCOMES = {"APPROVE", "REJECT", "REQUEST_MORE_INFO"}
DOC_STATUSES = {"COMPLETE", "INCOMPLETE", "MISSING", "NOT_APPLICABLE"}
CHECK_RESULTS = {"PASS", "FAIL", "UNCERTAIN"}
MEDICAL_RESULTS = {"SUPPORTED", "NOT_SUPPORTED", "INSUFFICIENT_EVIDENCE", "REFER_TO_MEDICAL_REVIEW"}
ASSESSMENT_STATUSES = {"READY_FOR_AUTHORIZATION", "PENDING_INFORMATION", "ESCALATED"}
SECTIONS = ("metadata", "document_review", "policy_verification", "medical_necessity", "benefit_calculation", "recommendation", "policy_citations", "human_review")
CALCULATED = ("excluded", "eligible", "deductible", "copay", "coinsurance", "limit_adjustment", "insurer_payable", "member_responsibility", "remaining_limit_before", "remaining_limit_after")


def _d(value: Optional[str]) -> Optional[Decimal]:
    return Decimal(value) if value is not None else None


def _check_calculation(calc: Dict[str, Any], errors: List[str]) -> str:
    if calc["status"] == "PENDING":
        for name in CALCULATED:
            if calc[name] is not None:
                errors.append(f"PENDING calculation has a value for {name}; unresolved amounts must be null.")
        return "NOT_APPLICABLE"
    a = {k: _d(calc[k]) for k in ("submitted",) + CALCULATED}
    if any(v is None for v in a.values()):
        errors.append("COMPLETE calculation has null amounts.")
        return "NEEDS_REVIEW"
    problems = []
    if a["excluded"] + a["eligible"] != a["submitted"]:
        problems.append("excluded + eligible != submitted")
    if a["deductible"] + a["copay"] + a["coinsurance"] + a["limit_adjustment"] + a["insurer_payable"] != a["eligible"]:
        problems.append("cost-sharing + limit adjustment + payable != eligible")
    if a["insurer_payable"] + a["member_responsibility"] != a["submitted"]:
        problems.append("payable + member responsibility != submitted")
    if a["insurer_payable"] > a["remaining_limit_before"]:
        problems.append("payable exceeds remaining limit")
    if a["remaining_limit_before"] - a["insurer_payable"] != a["remaining_limit_after"]:
        problems.append("remaining limit does not reconcile")
    if any(v < 0 for v in a.values()):
        problems.append("negative amount")
    errors.extend(f"Calculation: {p}." for p in problems)
    return "NEEDS_REVIEW" if problems else "PASS"


def _check_citations(report: Dict[str, Any], policy: PolicyResult, errors: List[str]) -> str:
    before = len(errors)
    citations = {c["citation_id"]: c for c in report["policy_citations"]["citations"]}
    for c in citations.values():
        if not c.get("text"):
            errors.append(f"Citation {c['citation_id']} ({c['clause_id']}) has no source text; clause not established.")
        if c["kind"] == "POLICY":
            source = policy.clauses.get(c["clause_id"]) if policy.status == "FOUND" else None
            if source is None:
                errors.append(f"Citation {c['citation_id']} references unknown clause {c['clause_id']}.")
            elif c["text"] != source["exact_text"]:
                errors.append(f"Citation {c['citation_id']} text differs from clause {c['clause_id']}.")
            if c["version"] != policy.version:
                errors.append(f"Citation {c['citation_id']} version {c['version']} != policy version {policy.version}.")
        elif c["kind"] == "RULE":
            source = policy.rules.get(c["clause_id"])
            if source is None:
                errors.append(f"Citation {c['citation_id']} references unknown rule {c['clause_id']}.")
            elif c["text"] != source["exact_text"] or c["version"] != source["version"]:
                errors.append(f"Citation {c['citation_id']} differs from rule {c['clause_id']} version {source['version']}.")

    referenced = []
    for reason in report["recommendation"]["reasons"]:
        if not reason["evidence"]:
            errors.append(f"Reason has no evidence: {reason['finding']}")
        if not reason["citation_ids"]:
            errors.append(f"Reason has no citation: {reason['finding']}")
        referenced += reason["citation_ids"]
    for section in ("policy_verification", "medical_necessity", "benefit_calculation"):
        data = report[section]
        for item in data.get("checks", [data]):
            referenced += item.get("citation_ids", [])
    referenced += [cid for row in report["document_review"]["rows"] for cid in row["citation_ids"]]
    for cid in referenced:
        if cid not in citations:
            errors.append(f"Citation ID {cid} does not exist in Policy Citations.")
    return "PASS" if len(errors) == before else "FAIL"


def validate_report(report: Dict[str, Any], policy: PolicyResult, submitted_document_ids: Set[str]) -> Dict[str, Any]:
    errors: List[str] = []
    for section in SECTIONS:
        if section not in report:
            errors.append(f"Missing section {section}.")
    if errors:
        return {"status": "FAIL", "errors": errors, "citation_check": "FAIL", "reconciliation": "NEEDS_REVIEW"}

    rec = report["recommendation"]
    outcome = rec["outcome"]
    if outcome is not None and outcome not in OUTCOMES:
        errors.append(f"Invalid recommendation {outcome}.")
    if outcome is None and report["assessment_status"] != "ESCALATED":
        errors.append("An assessment without a recommendation must be ESCALATED.")
    if report["assessment_status"] not in ASSESSMENT_STATUSES:
        errors.append(f"Invalid assessment status {report['assessment_status']}.")

    for row in report["document_review"]["rows"]:
        if row["status"] not in DOC_STATUSES:
            errors.append(f"Invalid document status {row['status']}.")
        if row["document_id"] is not None and row["document_id"] not in submitted_document_ids:
            errors.append(f"Document finding refers to unsubmitted document {row['document_id']}.")
        if row["document_id"] is None and row["status"] not in ("MISSING", "NOT_APPLICABLE"):
            errors.append(f"Requirement {row['requirement_id']} has no document but status {row['status']}.")
    for check in report["policy_verification"]["checks"]:
        if check["result"] not in CHECK_RESULTS:
            errors.append(f"Invalid policy check result {check['result']}.")
    medical = report["medical_necessity"]["result"]
    if medical not in MEDICAL_RESULTS:
        errors.append(f"Invalid medical necessity result {medical}.")

    reconciliation = _check_calculation(report["benefit_calculation"], errors)
    citation_check = _check_citations(report, policy, errors)

    calc = report["benefit_calculation"]
    if outcome == "APPROVE":
        if calc["status"] != "COMPLETE" or medical != "SUPPORTED":
            errors.append("APPROVE requires a complete calculation and SUPPORTED medical necessity.")
        if any(c["result"] != "PASS" for c in report["policy_verification"]["checks"]):
            errors.append("APPROVE requires every policy check to PASS.")
        if rec["recommended_payable"] != calc["insurer_payable"]:
            errors.append("Recommended payable differs from the calculated insurer payable.")
    # Contractual denial bases: a policy clause, or a rule from a contract-referenced rule source (e.g. submission deadlines).
    if outcome == "REJECT" and not any(
        c["kind"] in ("POLICY", "RULE") for c in report["policy_citations"]["citations"]
        if any(c["citation_id"] in r["citation_ids"] for r in rec["reasons"])
    ):
        errors.append("REJECT requires at least one applicable policy clause or contractual rule.")
    if outcome == "REQUEST_MORE_INFO" and not any(r["status"] == "OPEN" for r in rec["information_requests"]):
        errors.append("REQUEST_MORE_INFO requires at least one open information request.")
    if outcome != "APPROVE" and outcome != "REJECT" and rec["recommended_payable"] is not None:
        errors.append("A payable amount is only recommended for APPROVE or REJECT.")
    if report["human_review"]["authorization_status"] != "PENDING":
        errors.append("Final authorization must be PENDING until a human acts.")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "citation_check": citation_check,
        "reconciliation": reconciliation,
    }
