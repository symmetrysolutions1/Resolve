from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import tomllib


@dataclass(frozen=True, slots=True)
class EffortTier:
    max_reward_usd: float
    max_effort_hours: float


@dataclass(frozen=True, slots=True)
class ScoringConfig:
    min_reward_usd: float
    max_reward_usd: float
    min_expected_hourly_usd: float
    max_elapsed_hours: float
    fast_track_reward_usd: float
    fast_track_hours: float
    effort_tiers: tuple[EffortTier, ...]
    acceptance_probability: dict[str, float]
    competition_multiplier: dict[str, float]
    payment_probability: dict[str, float]
    platform_fee_rate: dict[str, float]
    min_scope_clarity: float
    reject_active_competing_pr: bool
    require_funded_contract: bool

    def effort_cap_for(self, reward_usd: float) -> float:
        for tier in self.effort_tiers:
            if reward_usd <= tier.max_reward_usd:
                return min(tier.max_effort_hours, self.max_elapsed_hours)
        return min(self.effort_tiers[-1].max_effort_hours, self.max_elapsed_hours)


@dataclass(frozen=True, slots=True)
class SkillConfig:
    primary: frozenset[str]
    expansion: frozenset[str]
    avoid: frozenset[str]


def _read_toml(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    with resolved.open("rb") as handle:
        return tomllib.load(handle)


def load_scoring_config(path: str | Path) -> ScoringConfig:
    data = _read_toml(path)
    market = data["market"]
    gates = data["gates"]
    tiers = tuple(
        sorted(
            (
                EffortTier(
                    max_reward_usd=float(item["max_reward_usd"]),
                    max_effort_hours=float(item["max_effort_hours"]),
                )
                for item in data["effort"]["tiers"]
            ),
            key=lambda item: item.max_reward_usd,
        )
    )
    if not tiers:
        raise ValueError("At least one effort tier is required")

    return ScoringConfig(
        min_reward_usd=float(market["min_reward_usd"]),
        max_reward_usd=float(market["max_reward_usd"]),
        min_expected_hourly_usd=float(market["min_expected_hourly_usd"]),
        max_elapsed_hours=float(market["max_elapsed_hours"]),
        fast_track_reward_usd=float(market["fast_track_reward_usd"]),
        fast_track_hours=float(market["fast_track_hours"]),
        effort_tiers=tiers,
        acceptance_probability={
            str(key): float(value) for key, value in data["acceptance_probability"].items()
        },
        competition_multiplier={
            str(key): float(value) for key, value in data["competition_multiplier"].items()
        },
        payment_probability={
            str(key): float(value) for key, value in data["payment_probability"].items()
        },
        platform_fee_rate={
            str(key): float(value) for key, value in data["platform_fee_rate"].items()
        },
        min_scope_clarity=float(gates["min_scope_clarity"]),
        reject_active_competing_pr=bool(gates["reject_active_competing_pr"]),
        require_funded_contract=bool(gates["require_funded_contract"]),
    )


def load_skill_config(path: str | Path) -> SkillConfig:
    data = _read_toml(path)["skills"]

    def normalize(values: list[str]) -> frozenset[str]:
        return frozenset(str(value).strip().lower() for value in values if str(value).strip())

    return SkillConfig(
        primary=normalize(data.get("primary", [])),
        expansion=normalize(data.get("expansion", [])),
        avoid=normalize(data.get("avoid", [])),
    )
