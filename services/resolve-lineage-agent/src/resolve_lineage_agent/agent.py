"""Deterministic resolution engine for DataHub-backed evidence."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def _canonical_digest(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def resolve_evidence(
    evidence: dict[str, Any],
    context: dict[str, Any],
    *,
    checked_at: str | None = None,
) -> dict[str, Any]:
    """Evaluate evidence against metadata context and return a signed-by-hash receipt."""
    findings: list[dict[str, str]] = []
    dataset_urn = evidence.get("dataset_urn")

    if not dataset_urn:
        findings.append({"code": "MISSING_DATASET_URN", "severity": "blocker"})
    elif dataset_urn != context.get("urn"):
        findings.append({"code": "DATASET_CONTEXT_MISMATCH", "severity": "blocker"})

    if not context.get("owners"):
        findings.append({"code": "UNOWNED_DATASET", "severity": "blocker"})

    if not context.get("upstreams"):
        findings.append({"code": "MISSING_UPSTREAM_LINEAGE", "severity": "warning"})

    available_fields = set(context.get("schema_fields", []))
    claimed_fields = set(evidence.get("claimed_fields", []))
    for missing in sorted(claimed_fields - available_fields):
        findings.append(
            {"code": "FIELD_NOT_IN_DATAHUB_SCHEMA", "severity": "blocker", "field": missing}
        )

    observations = evidence.get("observations", [])
    if not observations:
        findings.append({"code": "NO_OBSERVATIONS", "severity": "blocker"})

    blocking = sum(1 for item in findings if item["severity"] == "blocker")
    status = "verified" if blocking == 0 else "blocked"
    timestamp = checked_at or datetime.now(timezone.utc).isoformat()

    receipt_body = {
        "agent": "resolve-lineage-agent",
        "version": "0.1.0",
        "dataset_urn": dataset_urn,
        "checked_at": timestamp,
        "status": status,
        "findings": findings,
        "context_summary": {
            "owner_count": len(context.get("owners", [])),
            "upstream_count": len(context.get("upstreams", [])),
            "schema_field_count": len(available_fields),
        },
        "evidence_sha256": _canonical_digest(evidence),
    }
    return {**receipt_body, "receipt_sha256": _canonical_digest(receipt_body)}

