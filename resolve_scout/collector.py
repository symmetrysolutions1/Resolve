from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import Candidate


def _normalize_json_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("candidates"), list):
        return payload["candidates"]
    raise ValueError("JSON input must be a list or an object with a candidates list")


def load_candidates(path: str | Path) -> list[Candidate]:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".json":
        with source.open("r", encoding="utf-8") as handle:
            rows = _normalize_json_payload(json.load(handle))
    elif suffix == ".csv":
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
            for row in rows:
                if row.get("skills"):
                    row["skills"] = [
                        value.strip() for value in row["skills"].split(",") if value.strip()
                    ]
    else:
        raise ValueError("Only .json and .csv candidate files are supported")

    return [Candidate.from_dict(dict(row)) for row in rows]


def save_candidates(candidates: list[Candidate], path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(
            {"candidates": [candidate.to_dict() for candidate in candidates]},
            handle,
            ensure_ascii=False,
            indent=2,
        )
        handle.write("\n")
    return destination
