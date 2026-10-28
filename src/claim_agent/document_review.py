"""Compare verifyDocument results with the claim-type checklist and promote verified facts into the context.

Facts are promoted only from documents that were found, verified, and detected as the type they
were submitted as. A mismatched document stays visible, but the requirement it was meant to meet
stays MISSING.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from claim_agent.context import AssessmentContext
from claim_agent.tools.documents import DocumentResult


@dataclass
class DocumentRow:
    document_type: str
    required: str  # Y | CONDITIONAL | N
    status: str  # COMPLETE | INCOMPLETE | MISSING | NOT_APPLICABLE
    requirement_id: Optional[str] = None
    document_id: Optional[str] = None
    submitted_type: Optional[str] = None
    detected_type: Optional[str] = None
    verification: Optional[str] = None
    issues: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)


@dataclass
class InformationRequest:
    request_id: str
    required_item: str
    why_needed: str
    request_to: str
    requirement_id: str
    checklist_source: str
    policy_clause_id: Optional[str]
    reassessment_trigger: str
    status: str = "OPEN"


@dataclass
class DocumentReview:
    claim_id: str
    rows: List[DocumentRow]
    conclusion: str  # COMPLETE | UNRESOLVED_ITEMS
    requests: List[InformationRequest]
    checklist_id: Optional[str]
    checklist_version: Optional[str]
    checklist_source: Optional[Dict[str, Any]]
    consistency_issues: List[str] = field(default_factory=list)

    def row_for(self, document_type: str) -> Optional[DocumentRow]:
        return next((r for r in self.rows if r.document_type == document_type and r.required != "N"), None)


IDENTITY_FACTS = {"member_id": "member_id", "patient_member_id": "member_id", "policy_id": "policy_id"}
AMOUNT_FACTS = ("claimed_amount", "invoice_total", "amount_paid")
DATE_FACTS = ("treatment_date", "service_date", "examination_date", "payment_date", "appointment_date")


def _cross_check(result: DocumentResult, context: AssessmentContext) -> List[str]:
    issues = []
    for name, fact in result.extracted_facts.items():
        if name in IDENTITY_FACTS:
            expected = getattr(context, IDENTITY_FACTS[name])
            if fact.value != expected:
                issues.append(f"{name} {fact.value} does not match claim {expected} ({fact.location}).")
        elif name in AMOUNT_FACTS and Decimal(fact.value) != context.submitted_amount:
            issues.append(f"{name} {fact.value} does not match submitted {context.submitted_amount} ({fact.location}).")
        elif name in DATE_FACTS and not (context.treatment_start <= date.fromisoformat(fact.value) <= context.treatment_end):
            issues.append(f"{name} {fact.value} is outside the treatment dates ({fact.location}).")
    return issues


def _condition_met(condition: Optional[Dict[str, Any]], context: AssessmentContext) -> Optional[bool]:
    if condition is None:
        return True
    fact = context.fact(condition["fact"])
    if fact is None:
        return None
    return fact.value == condition["equals"]


def review_documents(context: AssessmentContext, results: List[DocumentResult]) -> DocumentReview:
    checklist = context.checklist
    usable: Dict[str, DocumentResult] = {}
    rows: List[DocumentRow] = []
    consistency: List[str] = []

    for result in results:
        if result.status != "FOUND":
            continue
        issues = _cross_check(result, context)
        consistency.extend(f"{result.document_id}: {i}" for i in issues)
        if result.detected_type == result.declared_type and result.verification_status == "VERIFIED" and not issues:
            usable.setdefault(result.detected_type, result)
            for name, fact in result.extracted_facts.items():
                context.record_fact(name, fact.value, fact.document_id, fact.location)

    if checklist is None:
        source_ref = None
        requirements = []
    else:
        source = checklist["procedural_source"]
        source_ref = f"{source['document']} v{source['version']}, {source['location']}"
        requirements = checklist["requirements"]

    requests: List[InformationRequest] = []
    matched_ids = set()
    for req in requirements:
        doc_type = req["document_type"]
        required = "Y" if req["requirement"] == "REQUIRED" else "CONDITIONAL"
        applies = _condition_met(req.get("condition"), context)
        submitted_as = [r for r in results if r.declared_type == doc_type]
        match = usable.get(doc_type)

        if applies is not True and match is None:
            note = "Condition not met." if applies is False else f"Condition fact '{req['condition']['fact']}' not documented; requirement not triggered."
            rows.append(DocumentRow(doc_type, required, "NOT_APPLICABLE", req["requirement_id"], issues=[note]))
            continue

        if match is not None:
            matched_ids.add(match.document_id)
            issues = [i["description"] for i in match.issues]
            rows.append(DocumentRow(
                doc_type, required, match.completeness_status, req["requirement_id"], match.document_id,
                match.declared_type, match.detected_type, match.verification_status, issues, [match.document_id],
            ))
            if match.completeness_status == "COMPLETE":
                continue
            status, problem = "INCOMPLETE", f"{doc_type} {match.document_id} is incomplete."
        else:
            issues = []
            for r in submitted_as:
                if r.status != "FOUND":
                    issues.append(f"Submitted {r.document_id} could not be verified: {r.reason}")
                elif r.detected_type == r.declared_type:
                    issues.append(f"Submitted {r.document_id} failed verification or consistency checks.")
                else:
                    issues.append(f"Submitted {r.document_id} declared {r.declared_type} but detected {r.detected_type}.")
            rows.append(DocumentRow(
                doc_type, required, "MISSING", req["requirement_id"], issues=issues or ["Not submitted."],
                evidence=[r.document_id for r in submitted_as],
            ))
            status, problem = "MISSING", f"Required {doc_type} is missing."

        requests.append(InformationRequest(
            request_id=f"REQ-{context.claim_id}-{len(requests) + 1}",
            required_item=doc_type,
            why_needed=f"{problem} {req['purpose']}",
            request_to=req["request_to"],
            requirement_id=req["requirement_id"],
            checklist_source=source_ref,
            policy_clause_id=None,
            reassessment_trigger=f"Reassess when a {doc_type} for {context.claim_id} is received and verified.",
        ))

    for result in results:
        if result.document_id in matched_ids:
            continue
        rows.append(DocumentRow(
            document_type=result.detected_type or result.declared_type or "UNKNOWN",
            required="N",
            status=result.completeness_status or "MISSING",
            document_id=result.document_id,
            submitted_type=result.declared_type,
            detected_type=result.detected_type,
            verification=result.verification_status,
            issues=[i["description"] for i in result.issues] + ([result.reason] if result.reason else []),
            evidence=[result.document_id],
        ))

    if checklist is None:
        consistency.append(f"No document checklist for claim type {context.claim_type}.")
    unresolved = requests or consistency or any(r.status == "INCOMPLETE" for r in rows if r.required != "N")
    return DocumentReview(
        claim_id=context.claim_id,
        rows=rows,
        conclusion="UNRESOLVED_ITEMS" if unresolved else "COMPLETE",
        requests=requests,
        checklist_id=checklist["checklist_id"] if checklist else None,
        checklist_version=checklist["version"] if checklist else None,
        checklist_source=checklist["procedural_source"] if checklist else None,
        consistency_issues=consistency,
    )
