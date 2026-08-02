from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import uuid4


class MemoryStore(Protocol):
    def remember(self, case: dict[str, Any], event: dict[str, Any]) -> None: ...
    def recall(self, case_id: str) -> dict[str, Any] | None: ...
    def history(self, case_id: str) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class Resolution:
    case_id: str
    status: str
    findings: list[str]
    evidence_sha256: str
    remembered_events: int
    decided_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "status": self.status,
            "findings": self.findings,
            "evidence_sha256": self.evidence_sha256,
            "remembered_events": self.remembered_events,
            "decided_at": self.decided_at,
        }


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def resolve_case(store: MemoryStore, payload: dict[str, Any]) -> Resolution:
    evidence = payload.get("evidence") or {}
    case_id = str(payload.get("case_id") or uuid4())
    previous = store.recall(case_id)
    findings: list[str] = []

    for field in ("source", "claim", "observed_at"):
        if not evidence.get(field):
            findings.append(f"missing:{field}")

    evidence_hash = canonical_sha256(evidence)
    if previous and previous.get("evidence_sha256") == evidence_hash:
        status = str(previous["status"])
        decision = "recalled"
    else:
        status = "needs_review" if findings else "verified"
        decision = "evaluated"

    decided_at = datetime.now(timezone.utc).isoformat()
    prior_events = store.history(case_id)
    resolution = Resolution(
        case_id=case_id,
        status=status,
        findings=findings,
        evidence_sha256=evidence_hash,
        remembered_events=len(prior_events) + 1,
        decided_at=decided_at,
    )
    store.remember(
        resolution.as_dict(),
        {
            "id": str(uuid4()),
            "case_id": case_id,
            "kind": decision,
            "payload": {"findings": findings, "input": payload},
            "created_at": decided_at,
        },
    )
    return resolution


def record_human_review(
    store: MemoryStore, case_id: str, reviewer: str, decision: str, note: str
) -> dict[str, Any]:
    current = store.recall(case_id)
    if current is None:
        raise KeyError(case_id)
    created_at = datetime.now(timezone.utc).isoformat()
    event = {
        "id": str(uuid4()),
        "case_id": case_id,
        "kind": "human_review",
        "payload": {"reviewer": reviewer, "decision": decision, "note": note},
        "created_at": created_at,
    }
    updated = dict(current)
    updated["status"] = decision
    updated["decided_at"] = created_at
    store.remember(updated, event)
    return {"case": updated, "event": event}

