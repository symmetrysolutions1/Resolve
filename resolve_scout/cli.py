from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import platform
import sys

from .collector import load_candidates, save_candidates
from .config import load_scoring_config, load_skill_config
from .reporting import write_reports
from .scoring import score_candidates
from .sources.github import DEFAULT_QUERIES, GitHubIssueSource, GitHubSourceError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCORING = PROJECT_ROOT / "config" / "scoring.toml"
DEFAULT_SKILLS = PROJECT_ROOT / "config" / "skills.toml"
DEFAULT_DEMO = PROJECT_ROOT / "data" / "examples" / "candidates.json"


def _add_config_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, default=DEFAULT_SCORING)
    parser.add_argument("--skills", type=Path, default=DEFAULT_SKILLS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resolve",
        description="Recolecta y prioriza tickets por valor esperado por hora.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Valida runtime y configuración.")
    _add_config_arguments(doctor)

    demo = subparsers.add_parser("demo", help="Ejecuta el flujo offline de demostración.")
    _add_config_arguments(demo)
    demo.add_argument("--input", type=Path, default=DEFAULT_DEMO)
    demo.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "runs" / "demo")

    score = subparsers.add_parser("score", help="Puntúa candidatos JSON o CSV.")
    _add_config_arguments(score)
    score.add_argument("--input", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)

    collect = subparsers.add_parser("collect", help="Recolecta tickets en vivo.")
    _add_config_arguments(collect)
    collect.add_argument("--source", choices=("github",), default="github")
    collect.add_argument("--query", action="append", dest="queries")
    collect.add_argument("--pages", type=int, default=1)
    collect.add_argument("--per-page", type=int, default=50)
    collect.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "runs" / "latest")

    return parser


def _load_engine(args: argparse.Namespace):
    return load_scoring_config(args.config), load_skill_config(args.skills)


def _print_result(scored, paths: dict[str, Path]) -> None:
    counts = Counter(item.decision for item in scored)
    print(
        f"Evaluados: {len(scored)} | GO: {counts['GO']} | "
        f"REVIEW: {counts['REVIEW']} | SKIP: {counts['SKIP']}"
    )
    for item in scored[:5]:
        print(
            f"{item.decision:6} {item.priority_score:5.1f} "
            f"USD {item.candidate.reward_usd:>6.0f} "
            f"USD {item.expected_hourly_usd:>6.2f}/h  {item.candidate.title}"
        )
    print(f"Reporte: {paths['markdown']}")


def _score_file(args: argparse.Namespace) -> int:
    config, skills = _load_engine(args)
    candidates = load_candidates(args.input)
    scored = score_candidates(candidates, config, skills)
    paths = write_reports(scored, args.output)
    _print_result(scored, paths)
    return 0


def _doctor(args: argparse.Namespace) -> int:
    config, skills = _load_engine(args)
    print(f"Python: {platform.python_version()}")
    print(f"Config: {args.config}")
    print(f"Skills: {len(skills.primary)} primary, {len(skills.expansion)} expansion")
    print(
        f"Mercado: USD {config.min_reward_usd:.0f}-{config.max_reward_usd:.0f}; "
        f"mínimo esperado USD {config.min_expected_hourly_usd:.0f}/h"
    )
    if sys.version_info < (3, 11):
        print("ERROR: Python 3.11 or newer is required.", file=sys.stderr)
        return 1
    print("Doctor: OK")
    return 0


def _collect(args: argparse.Namespace) -> int:
    config, skills = _load_engine(args)
    queries = tuple(args.queries) if args.queries else DEFAULT_QUERIES
    source = GitHubIssueSource()
    try:
        candidates = source.collect(
            queries=queries,
            pages=args.pages,
            per_page=args.per_page,
        )
    except GitHubSourceError as exc:
        print(f"Collection failed: {exc}", file=sys.stderr)
        return 2

    raw_path = save_candidates(candidates, args.output / "candidates.json")
    scored = score_candidates(candidates, config, skills)
    paths = write_reports(scored, args.output)
    print(f"Raw candidates: {raw_path}")
    _print_result(scored, paths)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "doctor":
        return _doctor(args)
    if args.command in {"demo", "score"}:
        return _score_file(args)
    if args.command == "collect":
        return _collect(args)
    parser.error(f"Unknown command: {args.command}")
    return 2
