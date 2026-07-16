from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any


def _clamp_probability(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class Candidate:
    id: str
    title: str
    url: str
    platform: str
    reward_usd: float
    estimated_hours: float
    status: str = "open"
    contract_type: str = "unknown"
    competition_count: int = 0
    active_competing_pr: bool = False
    assigned_to_us: bool = False
    assigned_to_other: bool = False
    funded: bool = False
    preflight_complete: bool = False
    scope_clarity: float = 0.50
    payment_confidence: float | None = None
    platform_fee_rate: float | None = None
    skills: tuple[str, ...] = ()
    created_at: str | None = None
    deadline_at: str | None = None
    notes: str = ""
    source_data: dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Candidate id cannot be empty")
        if not self.title.strip():
            raise ValueError("Candidate title cannot be empty")
        if self.reward_usd < 0:
            raise ValueError("reward_usd cannot be negative")
        if self.estimated_hours <= 0:
            raise ValueError("estimated_hours must be positive")
        if self.competition_count < 0:
            raise ValueError("competition_count cannot be negative")

        object.__setattr__(self, "platform", self.platform.strip().lower() or "unknown")
        object.__setattr__(
            self,
            "contract_type",
            self.contract_type.strip().lower() or "unknown",
        )
        object.__setattr__(self, "status", self.status.strip().lower() or "unknown")
        object.__setattr__(self, "scope_clarity", _clamp_probability(self.scope_clarity))
        object.__setattr__(
            self,
            "skills",
            tuple(sorted({str(skill).strip().lower() for skill in self.skills if str(skill).strip()})),
        )
        if self.payment_confidence is not None:
            object.__setattr__(
                self,
                "payment_confidence",
                _clamp_probability(self.payment_confidence),
            )
        if self.platform_fee_rate is not None:
            object.__setattr__(
                self,
                "platform_fee_rate",
                _clamp_probability(self.platform_fee_rate),
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Candidate":
        allowed = {item.name for item in fields(cls)}
        values = {key: value for key, value in data.items() if key in allowed}
        values["skills"] = tuple(values.get("skills") or ())
        values["source_data"] = dict(values.get("source_data") or {})

        float_fields = (
            "reward_usd",
            "estimated_hours",
            "scope_clarity",
            "payment_confidence",
            "platform_fee_rate",
        )
        for name in float_fields:
            if name in values and values[name] not in (None, ""):
                values[name] = float(values[name])
            elif name in ("payment_confidence", "platform_fee_rate") and values.get(name) == "":
                values[name] = None

        if "competition_count" in values:
            values["competition_count"] = int(values["competition_count"])

        for name in (
            "active_competing_pr",
            "assigned_to_us",
            "assigned_to_other",
            "funded",
            "preflight_complete",
        ):
            if name in values and isinstance(values[name], str):
                values[name] = values[name].strip().lower() in {"1", "true", "yes", "si", "sí"}

        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["skills"] = list(self.skills)
        return data


@dataclass(frozen=True, slots=True)
class ScoredCandidate:
    candidate: Candidate
    decision: str
    priority_score: float
    gross_hourly_usd: float
    net_reward_usd: float
    acceptance_probability: float
    payment_probability: float
    expected_value_usd: float
    expected_hourly_usd: float
    effort_cap_hours: float
    skill_fit: float
    fast_track: bool
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.candidate.to_dict(),
            "decision": self.decision,
            "priority_score": round(self.priority_score, 2),
            "gross_hourly_usd": round(self.gross_hourly_usd, 2),
            "net_reward_usd": round(self.net_reward_usd, 2),
            "acceptance_probability": round(self.acceptance_probability, 4),
            "payment_probability": round(self.payment_probability, 4),
            "expected_value_usd": round(self.expected_value_usd, 2),
            "expected_hourly_usd": round(self.expected_hourly_usd, 2),
            "effort_cap_hours": round(self.effort_cap_hours, 2),
            "skill_fit": round(self.skill_fit, 4),
            "fast_track": self.fast_track,
            "reasons": list(self.reasons),
        }
