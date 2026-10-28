"""Audit trail: every tool call's input, output, status, timestamp, tool and context versions, skipped steps with reasons, and overrides."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from claim_agent.serialize import to_jsonable


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


@dataclass
class AuditEvent:
    sequence: int
    event: str  # TOOL_CALL | SKIPPED_STEP | LLM_CALL | HUMAN_REVIEW
    name: str
    status: str  # OK | ERROR | SKIPPED | RECORDED
    timestamp: str
    context_version: str
    tool_version: Optional[str] = None
    input: Any = None
    output: Any = None
    reason: Optional[str] = None


@dataclass
class AuditTrail:
    reference: str
    claim_id: str
    context_version: str
    clock: Callable[[], datetime] = field(default=utc_now, repr=False)
    events: List[AuditEvent] = field(default_factory=list)

    @classmethod
    def start(cls, claim_id: str, context_version: str, clock: Callable[[], datetime] = utc_now) -> "AuditTrail":
        return cls(f"AUD-{claim_id}-{uuid.uuid4().hex[:8]}", claim_id, context_version, clock)

    def record(self, event: str, name: str, status: str, **details: Any) -> AuditEvent:
        entry = AuditEvent(
            sequence=len(self.events) + 1,
            event=event,
            name=name,
            status=status,
            timestamp=self.clock().isoformat(),
            context_version=self.context_version,
            tool_version=details.get("tool_version"),
            input=to_jsonable(details.get("input")),
            output=to_jsonable(details.get("output")),
            reason=details.get("reason"),
        )
        self.events.append(entry)
        return entry

    def record_skipped_step(self, name: str, reason: str) -> None:
        self.record("SKIPPED_STEP", name, "SKIPPED", reason=reason)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference": self.reference,
            "claim_id": self.claim_id,
            "context_version": self.context_version,
            "events": [to_jsonable(e) for e in self.events],
        }
