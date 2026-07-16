from __future__ import annotations

import json
import os
import re
from hashlib import sha1
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..models import Candidate


DEFAULT_QUERIES = (
    'is:issue is:open label:bounty',
    'is:issue is:open bounty in:title,body',
    'is:issue is:open reward in:title,body',
)

_AMOUNT = r"(?P<amount>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?)"
_REWARD_PATTERNS = (
    re.compile(rf"(?:US\$|\$)\s*{_AMOUNT}", re.IGNORECASE),
    re.compile(rf"\b(?:USD|USDC|USDT|USDG)\s*{_AMOUNT}\b", re.IGNORECASE),
    re.compile(rf"\b{_AMOUNT}\s*(?:USD|USDC|USDT|USDG)\b", re.IGNORECASE),
)

_SKILL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "python": ("python", "django", "flask", "fastapi", "pandas"),
    "automation": ("automation", "automatización", "workflow", "webhook"),
    "api": (" api ", "rest api", "graphql", "endpoint"),
    "playwright": ("playwright",),
    "javascript": ("javascript", "node.js", "nodejs"),
    "typescript": ("typescript",),
    "react": ("react",),
    "next.js": ("next.js", "nextjs"),
    "sql": (" sql ", "database query"),
    "postgresql": ("postgres", "postgresql"),
    "supabase": ("supabase",),
    "solidity": ("solidity", "smart contract", "ethereum", "evm"),
    "foundry": ("foundry", "forge test"),
    "wordpress": ("wordpress",),
    "woocommerce": ("woocommerce",),
    "php": (" php ",),
    "shopify": ("shopify",),
    "liquid": (" liquid ",),
    "n8n": ("n8n",),
    "zapier": ("zapier",),
    "make": ("make.com",),
    "google sheets": ("google sheets", "spreadsheet"),
    "scraping": ("scraping", "scraper", "crawl"),
    "csv": (" csv ",),
    "pdf": (" pdf ",),
    "docker": ("docker", "container"),
    "github actions": ("github actions", "workflow yml", "ci/cd"),
    "qa": ("quality assurance", " qa "),
    "testing": ("test", "regression"),
}


class GitHubSourceError(RuntimeError):
    pass


def parse_reward_usd(text: str) -> float | None:
    amounts: list[float] = []
    for pattern in _REWARD_PATTERNS:
        for match in pattern.finditer(text or ""):
            value = float(match.group("amount").replace(",", ""))
            if value > 0:
                amounts.append(value)
    return max(amounts) if amounts else None


def detect_skills(text: str) -> tuple[str, ...]:
    normalized = f" {(text or '').lower()} "
    matches = {
        skill
        for skill, keywords in _SKILL_KEYWORDS.items()
        if any(keyword in normalized for keyword in keywords)
    }
    return tuple(sorted(matches))


def estimate_hours(text: str) -> float:
    normalized = (text or "").lower()
    if any(word in normalized for word in ("migration", "architecture", "major refactor", "redesign")):
        return 16.0
    if any(word in normalized for word in ("feature", "refactor", "implement")):
        return 12.0
    if any(word in normalized for word in ("integration", "webhook", "automation", "scraping")):
        return 8.0
    if any(word in normalized for word in ("css", "copy change", "configuration", "small fix")):
        return 2.0
    if any(word in normalized for word in ("bug", "fix", "regression", "test")):
        return 4.0
    if any(word in normalized for word in ("typo", "readme", "documentation", "docs only")):
        return 1.0
    return 6.0


def estimate_scope_clarity(body: str) -> float:
    normalized = (body or "").lower()
    score = 0.35
    if len(normalized) >= 250:
        score += 0.10
    for signal in (
        "acceptance criteria",
        "expected behavior",
        "steps to reproduce",
        "reproduction",
        "must ",
        "test",
    ):
        if signal in normalized:
            score += 0.08
    return min(0.95, score)


def infer_platform(text: str) -> str:
    normalized = (text or "").lower()
    for platform in ("algora", "taskbounty", "onlydust", "superteam", "issuehunt", "opire"):
        if platform in normalized:
            return platform
    return "github"


def issue_to_candidate(issue: dict[str, Any]) -> Candidate | None:
    title = str(issue.get("title") or "")
    body = str(issue.get("body") or "")
    combined = f"{title}\n{body}"
    reward = parse_reward_usd(combined)
    if reward is None:
        return None

    labels = [
        str(item.get("name") or "")
        for item in issue.get("labels", [])
        if isinstance(item, dict)
    ]
    combined_with_labels = f"{combined}\n{' '.join(labels)}"
    platform = infer_platform(combined_with_labels)
    contract_type = "contest" if platform == "superteam" else "open_race"
    comments = int(issue.get("comments") or 0)
    assignees = issue.get("assignees") or []
    assigned = bool(issue.get("assignee") or assignees)
    url = str(issue.get("html_url") or "")
    source_id = str(issue.get("id") or sha1(url.encode("utf-8")).hexdigest()[:16])

    return Candidate(
        id=f"github:{source_id}",
        title=title or "Untitled GitHub bounty",
        url=url,
        platform=platform,
        reward_usd=reward,
        estimated_hours=estimate_hours(combined_with_labels),
        status="open" if str(issue.get("state") or "open").lower() == "open" else "closed",
        contract_type=contract_type,
        competition_count=0,
        active_competing_pr=False,
        assigned_to_other=assigned,
        funded=platform not in {"github", "issuehunt", "opire"},
        preflight_complete=False,
        scope_clarity=estimate_scope_clarity(body),
        skills=detect_skills(combined_with_labels),
        created_at=issue.get("created_at"),
        notes="Requiere verificar PRs activos y reglas de claim antes de comenzar.",
        source_data={
            "repository_url": issue.get("repository_url"),
            "comments": comments,
            "labels": labels,
        },
    )


class GitHubIssueSource:
    api_url = "https://api.github.com/search/issues"

    def __init__(self, token: str | None = None, timeout_seconds: float = 20.0) -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self.timeout_seconds = timeout_seconds

    def _fetch_page(self, query: str, page: int, per_page: int) -> dict[str, Any]:
        url = f"{self.api_url}?{urlencode({'q': query, 'page': page, 'per_page': per_page})}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "symmetry-resolve/0.1",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(url, headers=headers)

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubSourceError(f"GitHub API returned HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise GitHubSourceError(f"Could not reach GitHub API: {exc.reason}") from exc

    def collect(
        self,
        queries: tuple[str, ...] | list[str] | None = None,
        pages: int = 1,
        per_page: int = 50,
    ) -> list[Candidate]:
        if pages < 1:
            raise ValueError("pages must be at least 1")
        if not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")

        candidates: dict[str, Candidate] = {}
        for query in queries or DEFAULT_QUERIES:
            for page in range(1, pages + 1):
                payload = self._fetch_page(query, page, per_page)
                items = payload.get("items") or []
                if not items:
                    break
                for issue in items:
                    candidate = issue_to_candidate(issue)
                    if candidate is not None:
                        candidates[candidate.url or candidate.id] = candidate
                if len(items) < per_page:
                    break

        return list(candidates.values())
