from __future__ import annotations

import base64
import json
from typing import Any

from .agent import record_human_review, resolve_case
from .cockroach import CockroachMemoryStore


HTML = """<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width'>
<title>Resolve Memory Agent</title><style>body{font:16px system-ui;max-width:820px;margin:40px auto;padding:0 20px;background:#07111f;color:#e9f1ff}textarea,input{width:100%;box-sizing:border-box;margin:8px 0;padding:12px;border-radius:8px;border:1px solid #345;background:#0d1d30;color:#fff}button{padding:12px 18px;background:#35d0a0;border:0;border-radius:8px;font-weight:700}pre{white-space:pre-wrap;background:#0d1d30;padding:16px;border-radius:8px}.muted{color:#9fb2c8}</style></head>
<body><h1>Resolve Memory Agent</h1><p class=muted>CockroachDB-backed evidence memory running on AWS.</p>
<input id=case placeholder='Case UUID (leave empty for a new case)'><textarea id=evidence rows=8>{"source":"field-sensor-7","claim":"temperature within range","observed_at":"2026-08-01T12:00:00Z"}</textarea>
<button onclick=run()>Resolve and remember</button><pre id=out>Ready.</pre><script>async function run(){let b={evidence:JSON.parse(evidence.value)};if(case.value)b.case_id=case.value;let r=await fetch('/api/resolve',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(b)});let j=await r.json();out.textContent=JSON.stringify(j,null,2);if(j.case_id)case.value=j.case_id}</script></body></html>"""


def _response(status: int, body: Any, content_type: str = "application/json") -> dict[str, Any]:
    value = body if isinstance(body, str) else json.dumps(body)
    return {"statusCode": status, "headers": {"content-type": content_type}, "body": value}


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    path = event.get("rawPath") or event.get("path") or "/"
    method = (event.get("requestContext", {}).get("http", {}).get("method") or event.get("httpMethod") or "GET").upper()
    if method == "GET" and path == "/":
        return _response(200, HTML, "text/html; charset=utf-8")

    store = CockroachMemoryStore()
    store.initialize()
    if method == "POST" and path == "/api/resolve":
        raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            raw = base64.b64decode(raw).decode()
        return _response(200, resolve_case(store, json.loads(raw)).as_dict())
    if method == "GET" and path.startswith("/api/cases/"):
        case_id = path.removeprefix("/api/cases/").split("/")[0]
        case = store.recall(case_id)
        return _response(200 if case else 404, {"case": case, "history": store.history(case_id) if case else []})
    if method == "POST" and path.endswith("/review") and path.startswith("/api/cases/"):
        case_id = path.removeprefix("/api/cases/").removesuffix("/review").strip("/")
        raw = event.get("body") or "{}"
        payload = json.loads(raw)
        try:
            return _response(200, record_human_review(store, case_id, payload["reviewer"], payload["decision"], payload.get("note", "")))
        except KeyError:
            return _response(404, {"error": "case_not_found"})
    return _response(404, {"error": "not_found"})

