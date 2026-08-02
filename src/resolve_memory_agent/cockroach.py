from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from typing import Any, Iterator


SCHEMA = """
CREATE TABLE IF NOT EXISTS resolve_cases (
  case_id UUID PRIMARY KEY,
  status STRING NOT NULL,
  evidence_sha256 STRING NOT NULL,
  findings JSONB NOT NULL,
  decided_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS resolve_memory_events (
  event_id UUID PRIMARY KEY,
  case_id UUID NOT NULL REFERENCES resolve_cases(case_id),
  kind STRING NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  INDEX memory_by_case (case_id, created_at DESC)
);
"""


class CockroachMemoryStore:
    def __init__(self, database_url: str | None = None, max_retries: int = 3):
        self.database_url = database_url or os.environ["DATABASE_URL"]
        self.max_retries = max_retries

    @contextmanager
    def _connection(self) -> Iterator[Any]:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            yield connection

    def initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(SCHEMA)

    def remember(self, case: dict[str, Any], event: dict[str, Any]) -> None:
        import psycopg

        for attempt in range(self.max_retries):
            try:
                with self._connection() as connection:
                    connection.execute(
                        """
                        UPSERT INTO resolve_cases
                          (case_id, status, evidence_sha256, findings, decided_at, updated_at)
                        VALUES (%s, %s, %s, %s::JSONB, %s, now())
                        """,
                        (
                            case["case_id"], case["status"], case["evidence_sha256"],
                            json.dumps(case["findings"]), case["decided_at"],
                        ),
                    )
                    connection.execute(
                        """
                        INSERT INTO resolve_memory_events
                          (event_id, case_id, kind, payload, created_at)
                        VALUES (%s, %s, %s, %s::JSONB, %s)
                        """,
                        (
                            event["id"], event["case_id"], event["kind"],
                            json.dumps(event["payload"]), event["created_at"],
                        ),
                    )
                return
            except psycopg.errors.SerializationFailure:
                if attempt + 1 == self.max_retries:
                    raise
                time.sleep(0.05 * (2**attempt))

    def recall(self, case_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT case_id::STRING, status, evidence_sha256, findings, decided_at
                FROM resolve_cases WHERE case_id = %s
                """,
                (case_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "case_id": row[0], "status": row[1], "evidence_sha256": row[2],
            "findings": row[3], "decided_at": row[4].isoformat(),
        }

    def history(self, case_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT event_id::STRING, kind, payload, created_at
                FROM resolve_memory_events
                WHERE case_id = %s ORDER BY created_at ASC
                """,
                (case_id,),
            ).fetchall()
        return [
            {"id": row[0], "kind": row[1], "payload": row[2], "created_at": row[3].isoformat()}
            for row in rows
        ]

