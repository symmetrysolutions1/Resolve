from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import ScoredCandidate


def _safe_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _write_json(scored: list[ScoredCandidate], path: Path) -> None:
    counts = {
        decision: sum(item.decision == decision for item in scored)
        for decision in ("GO", "REVIEW", "SKIP")
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "summary": {"total": len(scored), **counts},
                "candidates": [item.to_dict() for item in scored],
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
        handle.write("\n")


def _write_csv(scored: list[ScoredCandidate], path: Path) -> None:
    rows = [item.to_dict() for item in scored]
    columns = [
        "decision",
        "priority_score",
        "platform",
        "reward_usd",
        "estimated_hours",
        "gross_hourly_usd",
        "expected_hourly_usd",
        "acceptance_probability",
        "payment_probability",
        "competition_count",
        "fast_track",
        "title",
        "url",
        "skills",
        "reasons",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            row["skills"] = ", ".join(row.get("skills", []))
            row["reasons"] = " | ".join(row.get("reasons", []))
            writer.writerow(row)


def _write_markdown(scored: list[ScoredCandidate], path: Path) -> None:
    counts = {
        decision: sum(item.decision == decision for item in scored)
        for decision in ("GO", "REVIEW", "SKIP")
    }
    lines = [
        "# Shortlist Resolve",
        "",
        (
            f"Total: {len(scored)} | GO: {counts['GO']} | "
            f"REVIEW: {counts['REVIEW']} | SKIP: {counts['SKIP']}"
        ),
        "",
        "| Decisión | Score | Plataforma | Premio | Horas | USD/h esperado | Ticket |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for item in scored:
        candidate = item.candidate
        title = _safe_markdown(candidate.title)
        link = f"[{title}]({candidate.url})" if candidate.url else title
        lines.append(
            f"| {item.decision} | {item.priority_score:.1f} | "
            f"{_safe_markdown(candidate.platform)} | USD {candidate.reward_usd:.0f} | "
            f"{candidate.estimated_hours:.1f} | USD {item.expected_hourly_usd:.2f} | {link} |"
        )

    lines.extend(["", "## Razones", ""])
    for item in scored:
        lines.append(f"### {item.decision} — {_safe_markdown(item.candidate.title)}")
        lines.append("")
        for reason in item.reasons:
            lines.append(f"- {reason}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_reports(
    scored: list[ScoredCandidate],
    output_dir: str | Path,
) -> dict[str, Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": destination / "ranked.json",
        "csv": destination / "ranked.csv",
        "markdown": destination / "shortlist.md",
    }
    _write_json(scored, paths["json"])
    _write_csv(scored, paths["csv"])
    _write_markdown(scored, paths["markdown"])
    return paths
