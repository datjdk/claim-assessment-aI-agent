"""Read-only access to the fictional JSON fixtures in sample_data/.

Lookups return None when a record is not found. Callers must turn that into an
explicit unresolved result rather than assuming a value.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "sample_data"

FIXTURE_FILES = (
    "claims.json",
    "policies.json",
    "documents.json",
    "document_checklists.json",
    "clinical_rules.json",
    "benefit_balances.json",
    "submission_deadlines.json",
)

Record = Dict[str, Any]


def _load(path: Path) -> Record:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@dataclass(frozen=True)
class FixtureStore:
    claims: Dict[str, Record]
    policies: Dict[str, Record]
    documents: Dict[str, Record]
    checklists: Dict[str, Record]
    clinical_rule_set: Record
    clinical_rules: List[Record]
    balances: List[Record]
    submission_rule_sets: List[Record]
    fixture_versions: Dict[str, str]

    @classmethod
    def load(cls, data_dir: Optional[Path] = None) -> "FixtureStore":
        data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        raw = {name: _load(data_dir / name) for name in FIXTURE_FILES}
        clinical = raw["clinical_rules.json"]
        return cls(
            claims={c["claim_id"]: c for c in raw["claims.json"]["claims"]},
            policies={p["policy_id"]: p for p in raw["policies.json"]["policies"]},
            documents={d["document_id"]: d for d in raw["documents.json"]["documents"]},
            checklists={c["claim_type"]: c for c in raw["document_checklists.json"]["checklists"]},
            clinical_rule_set=clinical["rule_set"],
            clinical_rules=clinical["rules"],
            balances=raw["benefit_balances.json"]["balances"],
            submission_rule_sets=raw["submission_deadlines.json"]["rule_sets"],
            fixture_versions={name: data["fixture_version"] for name, data in raw.items()},
        )

    def claim(self, claim_id: str) -> Optional[Record]:
        return self.claims.get(claim_id)

    def policy(self, policy_id: str) -> Optional[Record]:
        return self.policies.get(policy_id)

    def document(self, document_id: str) -> Optional[Record]:
        return self.documents.get(document_id)

    def checklist(self, claim_type: str) -> Optional[Record]:
        return self.checklists.get(claim_type)

    def submission_rule_set(self, policy_id: str) -> Optional[Record]:
        return next((r for r in self.submission_rule_sets if policy_id in r["applies_to_policy_ids"]), None)

    def balance(self, policy_id: str, member_id: str, benefit_type: str) -> Optional[Record]:
        for b in self.balances:
            if (b["policy_id"], b["member_id"], b["benefit_type"]) == (policy_id, member_id, benefit_type):
                return b
        return None
