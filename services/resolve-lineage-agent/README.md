# Resolve Lineage Agent

Resolve Lineage Agent is a DataHub-native evidence resolution agent. It reads dataset
ownership, schema, lineage, and custom properties before deciding whether an evidence
package is trustworthy enough to advance. It then writes a compact resolution receipt
back to DataHub so the next reviewer or agent inherits the result.

This repository is a new project created for **Build with DataHub: The Agent
Hackathon**. It does not claim that the pre-existing Symmetry platform was built during
the competition. Symmetry's generic evidence concepts informed the use case; the agent,
DataHub gateway, rules, tests, and demo in this repository are new work.

## Why DataHub matters

A file hash alone cannot answer whether evidence came from the expected dataset, whether
that dataset has an accountable owner, whether upstream sources are known, or whether the
schema contains the fields the evidence claims. DataHub supplies that organizational
context. Resolve turns it into an auditable decision and contributes the decision back to
the graph as dataset custom properties.

## Workflow

1. Load an evidence manifest containing a dataset URN, claimed fields, and observations.
2. Read `datasetProperties`, `schemaMetadata`, `ownership`, and `upstreamLineage` from DataHub.
3. Evaluate deterministic governance and evidence rules.
4. Produce a canonical SHA-256 resolution receipt.
5. Optionally write status, digest, timestamp, and finding count back with
   DataHub's `DatasetPatchBuilder`.

## Run the reproducible demo

The offline mode exercises the complete decision pipeline without external credentials:

```bash
python -m resolve_lineage_agent.cli \
  --evidence examples/evidence-valid.json \
  --context examples/datahub-context.json \
  --output build/resolution.json
```

Run the intentionally incomplete example to see a blocked resolution:

```bash
python -m resolve_lineage_agent.cli \
  --evidence examples/evidence-incomplete.json \
  --context examples/datahub-context.json
```

## Connect to DataHub

Install the project and point it at a DataHub Quickstart or DataHub Cloud instance:

```bash
python -m pip install -e .
datahub docker quickstart
python -m resolve_lineage_agent.cli \
  --evidence examples/evidence-valid.json \
  --datahub-server http://localhost:8080 \
  --write-back
```

For an authenticated deployment, pass `--datahub-token` or set `DATAHUB_TOKEN`.

## Test

```bash
python -m unittest discover -s tests -v
```

## DataHub write-back properties

- `resolve.last_status`
- `resolve.last_manifest_sha256`
- `resolve.last_checked_at`
- `resolve.finding_count`

The patch operation adds or updates only these keys and preserves unrelated dataset
properties.

## License

Apache License 2.0. See [LICENSE](LICENSE).

