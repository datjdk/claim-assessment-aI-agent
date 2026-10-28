"""Runs the assessment workflow: tools in order, prerequisites enforced, tool errors converted to unresolved results."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, Callable, Dict, List, Optional, TypeVar

from claim_agent import llm
from claim_agent.audit import AuditTrail, utc_now
from claim_agent.context import AssessmentContext, create_assessment_context
from claim_agent.decision import decide
from claim_agent.document_review import DocumentReview, review_documents
from claim_agent.fixtures import FixtureStore
from claim_agent.report import EXPLANATION_SECTIONS, build_report, explanation_facts
from claim_agent.tools import benefit as benefit_tool
from claim_agent.tools import documents as documents_tool
from claim_agent.tools import medical as medical_tool
from claim_agent.tools import policy as policy_tool
from claim_agent.tools.benefit import BenefitResult
from claim_agent.tools.documents import DocumentResult
from claim_agent.tools.medical import MedicalResult
from claim_agent.tools.policy import PolicyResult
from claim_agent.validator import validate_report

T = TypeVar("T")

TOOL_VERSIONS = {
    "verifyDocument": documents_tool.TOOL_VERSION,
    "lookupPolicy": policy_tool.TOOL_VERSION,
    "checkMedicalNecessity": medical_tool.TOOL_VERSION,
    "calculateBenefit": benefit_tool.TOOL_VERSION,
}
STEP_VERSIONS = {"documentReview": "documentReview/1.0", "decide": "decide/1.0", "validateReport": "validateReport/1.0"}
CLINICAL_FACTS = ("diagnosis", "procedures", "medical_indication_present")
PREVIEW_CHARS = 72


@dataclass
class Assessment:
    report: Dict[str, Any]
    audit: AuditTrail
    context: AssessmentContext
    policy: PolicyResult


def safe_tool_call(audit: AuditTrail, name: str, inputs: Dict[str, Any], call: Callable[[], T], on_error: Callable[[str], T]) -> T:
    """Run a tool and record it. An exception becomes an explicit unresolved result, never an assumption."""
    try:
        result = call()
    except Exception as e:  # noqa: BLE001 - every tool failure must be recorded, not raised
        reason = f"{name} failed: {type(e).__name__}: {e}"
        audit.record("TOOL_CALL", name, "ERROR", tool_version=TOOL_VERSIONS[name], input=inputs, reason=reason)
        return on_error(reason)
    audit.record("TOOL_CALL", name, "OK", tool_version=TOOL_VERSIONS[name], input=inputs, output=result)
    return result


def _clinical_facts_sufficient(context: AssessmentContext) -> bool:
    # A diagnosis fact must exist (its value may be an explicit null) along with procedures and the
    # medical-indication finding; claimant-reported values never count.
    return all(context.fact(name) is not None for name in CLINICAL_FACTS)


def _clinical_gap(context: AssessmentContext, review: DocumentReview) -> str:
    """Why medical necessity cannot be checked, naming the document requirement or facts that are missing."""
    row = review.row_for("MEDICAL_REPORT")
    if row is not None and row.status != "COMPLETE":
        detected = {r.document_id: r.detected_type for r in review.rows if r.required == "N" and r.document_id}
        submitted = [f"{d} is {detected[d]}" for d in row.evidence if detected.get(d)]
        return f"No verified MEDICAL_REPORT: {row.requirement_id} {row.status}" + (f" ({'; '.join(submitted)})" if submitted else "") + "."
    missing = [name for name in CLINICAL_FACTS if context.fact(name) is None]
    return "Verified clinical facts missing: " + ", ".join(missing) + "."


def _calculation_blockers(policy: PolicyResult, review: DocumentReview, medical: MedicalResult) -> List[str]:
    """What prevents the benefit calculation; empty when it can run."""
    blockers = []
    if policy.status != "FOUND":
        blockers.append(f"policy {policy.policy_id} unresolved ({policy.reason})")
    for request in review.requests:
        row = review.row_for(request.required_item)
        blockers.append(f"{request.requirement_id} {request.required_item} {row.status if row else 'MISSING'}")
    if medical.result not in ("SUPPORTED", "NOT_SUPPORTED"):
        blockers.append(f"medical necessity {medical.result}")
    return blockers


def _preview(text: Optional[str]) -> str:
    flat = re.sub(r"\s+", " ", text or "").strip()
    return flat if len(flat) <= PREVIEW_CHARS else flat[: PREVIEW_CHARS - 1] + "…"


def _llm_exchange_logger(audit: AuditTrail, client: llm.OpenRouterClient) -> llm.ExchangeHook:
    """Record one audit event per OpenRouter request, with short request and response text."""

    def record(exchange: Dict[str, Any], messages: List[Dict[str, str]]) -> None:
        request = [{"role": m["role"], "chars": len(m["content"]), "text": _preview(m["content"])} for m in messages]
        reply = exchange.get("raw_content")
        usage = exchange.get("usage") or {}
        audit.record(
            "LLM_REQUEST", "openrouter.chat", "ERROR" if "error" in exchange else "OK",
            tool_version=f"openrouter:{client.config.model}",
            input={"url": client.config.url, "model": client.config.model, "attempt": exchange["attempt"], "request_preview": request},
            output={
                "response_id": exchange.get("response_id"),
                "served_model": exchange.get("served_model"),
                "tokens_in": usage.get("prompt_tokens"),
                "tokens_out": usage.get("completion_tokens"),
                "validation_problems": exchange.get("validation_problems", []),
                "response_preview": {"chars": len(reply), "text": _preview(reply)} if reply is not None else None,
            },
            reason=exchange.get("error"),
        )

    return record


def assess_claim(
    claim_id: str,
    store: Optional[FixtureStore] = None,
    llm_client: Optional[llm.OpenRouterClient] = None,
    clock: Callable[[], datetime] = utc_now,
) -> Assessment:
    store = store or FixtureStore.load()
    context = create_assessment_context(claim_id, store)
    audit = AuditTrail.start(claim_id, context.context_version, clock)

    documents = []
    for ref in context.claim["documents"]:
        doc_id = ref["document_id"]
        documents.append(safe_tool_call(
            audit, "verifyDocument", {"documentId": doc_id},
            lambda: documents_tool.verify_document(doc_id, context),
            lambda reason: DocumentResult(doc_id, "UNRESOLVED", declared_type=ref.get("declared_type"), reason=reason),
        ))

    # Document review promotes verified facts first; exclusion checks in lookupPolicy depend on them.
    review = review_documents(context, documents)
    audit.record(
        "STEP", "documentReview", "OK", tool_version=STEP_VERSIONS["documentReview"],
        input={"checklist": f"{review.checklist_id} v{review.checklist_version}"}, output=review,
    )
    policy = safe_tool_call(
        audit, "lookupPolicy", {"policyId": context.policy_id},
        lambda: policy_tool.lookup_policy(context.policy_id, context),
        lambda reason: PolicyResult(context.policy_id, "UNRESOLVED", reason=reason),
    )
    for request in review.requests:
        request.policy_clause_id = policy.document_requirement_clause_ids.get(request.required_item)

    if _clinical_facts_sufficient(context):
        diagnosis = context.fact("diagnosis").value
        procedures = list(context.fact("procedures").value)
        medical = safe_tool_call(
            audit, "checkMedicalNecessity", {"diagnosis": diagnosis, "procedures": procedures},
            lambda: medical_tool.check_medical_necessity(diagnosis, procedures, context),
            lambda reason: MedicalResult("REFER_TO_MEDICAL_REVIEW", diagnosis, procedures, reason=reason),
        )
    else:
        reason = _clinical_gap(context, review)
        medical = MedicalResult("INSUFFICIENT_EVIDENCE", None, [], reason=reason)
        audit.record_skipped_step("checkMedicalNecessity", reason)

    amount = str(context.submitted_amount)
    blockers = _calculation_blockers(policy, review, medical)
    if not blockers:
        benefit = safe_tool_call(
            audit, "calculateBenefit", {"policyId": context.policy_id, "claimType": context.claim_type, "amount": amount},
            lambda: benefit_tool.calculate_benefit(context.policy_id, context.claim_type, amount, context),
            lambda reason: BenefitResult("PENDING", context.policy_id, context.claim_type, context.currency, context.submitted_amount, pending_reasons=[reason]),
        )
    else:
        reason = "Blocked by: " + "; ".join(blockers) + "."
        benefit = BenefitResult(
            "PENDING", context.policy_id, context.claim_type, context.currency, context.submitted_amount, pending_reasons=[reason],
        )
        audit.record_skipped_step("calculateBenefit", reason)

    decision = decide(review, policy, medical, benefit)
    audit.record(
        "STEP", "decide", "OK", tool_version=STEP_VERSIONS["decide"],
        output={
            "outcome": decision.outcome,
            "assessment_status": decision.assessment_status,
            "recommended_payable": decision.recommended_payable,
            "reasons": len(decision.reasons),
            "information_requests": [r.request_id for r in decision.information_requests],
            "escalations": len(decision.escalations),
        },
    )
    report = build_report(
        context, review, policy, medical, benefit, decision,
        assessment_id=f"ASM-{uuid.uuid4().hex[:10]}",
        assessed_at=clock().isoformat(),
        audit_reference=audit.reference,
        tool_versions=TOOL_VERSIONS,
    )

    if llm_client is not None:
        drafted = llm.draft_explanations(
            llm_client, explanation_facts(report), EXPLANATION_SECTIONS, on_exchange=_llm_exchange_logger(audit, llm_client)
        )
        audit.record(
            "LLM_CALL", "draftExplanations", "OK" if drafted.status == "DRAFTED" else "ERROR",
            tool_version=f"openrouter:{drafted.config['model']}",
            input={"sections": EXPLANATION_SECTIONS, "config": drafted.config, "url": drafted.config["url"],
                   "request_body": drafted.request_body},
            output={"status": drafted.status, "attempts": drafted.attempts, "served_model": drafted.served_model,
                    "response_id": drafted.response_id, "exchanges": drafted.exchanges},
            reason="; ".join(drafted.errors) or None,
        )
        report["explanations"] = {
            "status": drafted.status,
            "sections": drafted.explanations,
            "llm": {**drafted.config, "served_model": drafted.served_model, "response_id": drafted.response_id},
            "errors": drafted.errors,
        }
        report["metadata"]["llm"] = drafted.config

    submitted_ids = {d["document_id"] for d in context.claim["documents"]}
    report["validation"] = validate_report(report, policy, submitted_ids)
    report["policy_citations"]["coverage_check"] = report["validation"]["citation_check"]
    if report["validation"]["status"] != "PASS":
        report["assessment_status"] = "ESCALATED"
        report["recommendation"]["escalations"].append("Report failed validation: " + "; ".join(report["validation"]["errors"]))
    audit.record(
        "STEP", "validateReport", "OK" if report["validation"]["status"] == "PASS" else "FAIL",
        tool_version=STEP_VERSIONS["validateReport"],
        output={**report["validation"], "assessment_status": report["assessment_status"]},
    )
    return Assessment(report, audit, context, policy)
