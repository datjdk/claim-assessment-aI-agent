"""verifyDocument(documentId): detected type, completeness, issues and extracted facts for one submitted document."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from claim_agent.context import AssessmentContext, Fact

TOOL_VERSION = "verifyDocument/1.0"


@dataclass
class DocumentResult:
    document_id: str
    status: str  # FOUND | UNRESOLVED
    declared_type: Optional[str] = None
    detected_type: Optional[str] = None
    completeness_status: Optional[str] = None
    verification_status: Optional[str] = None
    issues: List[Dict[str, Any]] = field(default_factory=list)
    extracted_facts: Dict[str, Fact] = field(default_factory=dict)
    reason: Optional[str] = None


def verify_document(document_id: str, context: AssessmentContext) -> DocumentResult:
    """Return status FOUND with the document's findings, or UNRESOLVED with a reason.

    Does not record facts into the context; the orchestrator decides which facts are verified.
    """
    submitted = next((d for d in context.claim["documents"] if d["document_id"] == document_id), None)
    if submitted is None:
        return DocumentResult(document_id, "UNRESOLVED", reason=f"Document {document_id} was not submitted with claim {context.claim_id}.")
    declared = submitted.get("declared_type")

    doc = context.store.document(document_id)
    if doc is None:
        return DocumentResult(document_id, "UNRESOLVED", declared_type=declared, reason=f"No record found for document {document_id}.")
    if doc["claim_id"] != context.claim_id:
        return DocumentResult(
            document_id, "UNRESOLVED", declared_type=declared,
            reason=f"Document {document_id} belongs to claim {doc['claim_id']}, not {context.claim_id}.",
        )

    issues = [dict(i) for i in doc.get("issues", [])]
    if declared and declared != doc["detected_type"] and not any(i.get("code") == "TYPE_MISMATCH" for i in issues):
        issues.append({"code": "TYPE_MISMATCH", "description": f"Submitted as {declared} but detected as {doc['detected_type']}."})

    return DocumentResult(
        document_id=document_id,
        status="FOUND",
        declared_type=declared,
        detected_type=doc["detected_type"],
        completeness_status=doc["completeness_status"],
        verification_status=doc["verification_status"],
        issues=issues,
        extracted_facts={f["fact"]: Fact(f["value"], document_id, f["location"]) for f in doc["extracted_facts"]},
    )
