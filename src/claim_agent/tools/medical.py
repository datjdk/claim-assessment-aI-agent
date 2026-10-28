"""checkMedicalNecessity(diagnosis, procedures): SUPPORTED, NOT_SUPPORTED, INSUFFICIENT_EVIDENCE or REFER_TO_MEDICAL_REVIEW from clinical_rules.json."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from claim_agent.context import AssessmentContext, Fact

TOOL_VERSION = "checkMedicalNecessity/1.0"


@dataclass
class MedicalResult:
    result: str
    diagnosis: Optional[str]
    procedures: List[str]
    rule_id: Optional[str] = None
    rationale: Optional[str] = None
    rule_set_version: Optional[str] = None
    source: Optional[str] = None
    source_location: Optional[str] = None
    evidence: List[Fact] = field(default_factory=list)
    reason: Optional[str] = None


def _norm(text: Optional[str]) -> Optional[str]:
    return text.strip().casefold() if isinstance(text, str) else None


def _matches(rule, diagnosis: Optional[str], procedures: List[str]) -> bool:
    return _norm(rule["diagnosis"]) == _norm(diagnosis) and sorted(map(_norm, rule["procedures"])) == sorted(
        map(_norm, procedures)
    )


def check_medical_necessity(diagnosis: Optional[str], procedures: List[str], context: AssessmentContext) -> MedicalResult:
    """Match verified clinical facts against the clinical rules."""
    rule_set = context.store.clinical_rule_set

    def result(outcome, reason=None, rule=None, evidence=()):
        return MedicalResult(
            result=outcome,
            diagnosis=diagnosis,
            procedures=list(procedures),
            rule_id=rule["rule_id"] if rule else None,
            rationale=rule["rationale"] if rule else None,
            rule_set_version=rule_set["version"],
            source=rule_set["source"],
            source_location=rule["source_location"] if rule else None,
            evidence=list(evidence),
            reason=reason,
        )

    if not procedures:
        return result("INSUFFICIENT_EVIDENCE", "No verified procedures were supplied.")

    clinical = [f for f in (context.fact("diagnosis"), context.fact("procedures")) if f is not None]
    verified_dx, verified_px = context.fact("diagnosis"), context.fact("procedures")
    if (verified_dx and _norm(verified_dx.value) != _norm(diagnosis)) or (
        verified_px and sorted(map(_norm, verified_px.value)) != sorted(map(_norm, procedures))
    ):
        return result(
            "REFER_TO_MEDICAL_REVIEW", "Requested diagnosis or procedures differ from the verified medical record.", evidence=clinical
        )

    rule = next((r for r in context.store.clinical_rules if _matches(r, diagnosis, procedures)), None)
    if rule is None:
        if diagnosis is None:
            return result("INSUFFICIENT_EVIDENCE", "No diagnosis and no matching rule; a null diagnosis alone does not establish absence of medical indication.")
        return result("REFER_TO_MEDICAL_REVIEW", "No clinical rule matches this diagnosis and procedure combination.", evidence=clinical)

    evidence = list(clinical)
    for name, expected in rule.get("required_facts", {}).items():
        fact = context.fact(name)
        if fact is None:
            return result("INSUFFICIENT_EVIDENCE", f"Rule {rule['rule_id']} needs verified fact '{name}', which is not documented.")
        if fact.value != expected:
            return result(
                "REFER_TO_MEDICAL_REVIEW",
                f"Verified fact '{name}' ({fact.value!r}) contradicts rule {rule['rule_id']} ({expected!r}).",
                evidence=evidence + [fact],
            )
        if fact not in evidence:
            evidence.append(fact)
    return result(rule["result"], rule=rule, evidence=evidence)
