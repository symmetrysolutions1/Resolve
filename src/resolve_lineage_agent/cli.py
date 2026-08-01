"""Command-line interface for the Resolve Lineage Agent."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .agent import resolve_evidence
from .datahub_gateway import DataHubGateway


def _read_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve evidence with DataHub context")
    parser.add_argument("--evidence", required=True, help="Evidence manifest JSON")
    parser.add_argument("--context", help="Offline DataHub context JSON")
    parser.add_argument("--datahub-server", help="DataHub GMS URL")
    parser.add_argument("--datahub-token", default=os.getenv("DATAHUB_TOKEN"))
    parser.add_argument("--write-back", action="store_true")
    parser.add_argument("--output", help="Optional receipt output path")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    evidence = _read_json(args.evidence)

    gateway = None
    if args.context:
        context = _read_json(args.context)
    elif args.datahub_server:
        gateway = DataHubGateway(args.datahub_server, args.datahub_token)
        context = gateway.read_context(evidence["dataset_urn"])
    else:
        raise SystemExit("Provide --context for offline mode or --datahub-server for live mode")

    receipt = resolve_evidence(evidence, context)
    rendered = json.dumps(receipt, indent=2, sort_keys=True)
    print(rendered)

    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered + "\n", encoding="utf-8")

    if args.write_back:
        if gateway is None:
            raise SystemExit("--write-back requires --datahub-server")
        gateway.write_resolution(evidence["dataset_urn"], receipt)

    return 0 if receipt["status"] == "verified" else 2


if __name__ == "__main__":
    raise SystemExit(main())

