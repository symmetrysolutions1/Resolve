# Resolve Memory Agent

Resolve Memory Agent is an evidence-resolution service whose durable operational memory lives in CockroachDB and whose public API is designed for AWS Lambda. It remembers cases, evidence hashes, decisions, retries, and human reviews across sessions.

## Why CockroachDB and AWS

CockroachDB is not a passive dependency: every resolution upserts the current case and appends an immutable memory event in the same transaction. Repeated evidence recalls the prior decision, while changed evidence is evaluated again. Serializable transaction failures are retried with bounded exponential backoff. AWS SAM deploys the agent as a public Lambda Function URL.

## Architecture

1. A reviewer sends evidence to `POST /api/resolve`.
2. The agent hashes the canonical evidence and recalls prior case memory.
3. It evaluates new evidence or reuses an identical prior decision.
4. CockroachDB transactionally stores the case and append-only event.
5. `GET /api/cases/{id}` returns the durable history; human review is recorded at `POST /api/cases/{id}/review`.

## Local verification

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

For a real CockroachDB run, create a Basic cluster and set its TLS connection string as `DATABASE_URL`. The first request creates the two application tables.

## AWS deployment

Install AWS SAM CLI, authenticate an AWS account, then run:

```powershell
sam build
sam deploy --guided --parameter-overrides DatabaseUrl="$env:DATABASE_URL"
```

Never commit the connection string. CloudFormation treats the parameter as `NoEcho`, and the deployed Lambda receives it only as an environment variable.

## Hackathon disclosure

This standalone project was created for the 2026 CockroachDB × AWS Build with Agentic Memory hackathon. It applies general evidence-resolution concepts explored by Symmetry Solutions, but the code, CockroachDB schema, AWS template, memory model, and demo application in this repository are new hackathon work.

## License

Apache-2.0.
