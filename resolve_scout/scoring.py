from __future__ import annotations

from collections.abc import Iterable

from .config import ScoringConfig, SkillConfig
from .models import Candidate, ScoredCandidate


DECISION_ORDER = {"GO": 0, "REVIEW": 1, "SKIP": 2}


def _competition_key(count: int) -> str:
    if count <= 0:
        return "zero"
    if count == 1:
        return "one"
    if count == 2:
        return "two"
    return "three_plus"


def _skill_fit(candidate: Candidate, skills: SkillConfig) -> float:
    candidate_skills = set(candidate.skills)
    if not candidate_skills:
        return 0.50

    if candidate_skills & skills.avoid and not (
        candidate_skills & skills.primary or candidate_skills & skills.expansion
    ):
        return 0.10

    primary_matches = len(candidate_skills & skills.primary)
    expansion_matches = len(candidate_skills & skills.expansion)
    if primary_matches:
        return min(1.0, 0.80 + (0.05 * primary_matches) + (0.025 * expansion_matches))
    if expansion_matches:
        return min(0.85, 0.65 + (0.05 * expansion_matches))
    return 0.45


def _acceptance_probability(candidate: Candidate, config: ScoringConfig) -> float:
    contract_type = candidate.contract_type
    if candidate.assigned_to_us and contract_type != "contracted":
        contract_type = "assigned"
    base = config.acceptance_probability.get(
        contract_type,
        config.acceptance_probability.get("unknown", 0.40),
    )

    if candidate.contract_type in {"open_race", "contest"} and not candidate.assigned_to_us:
        multiplier = config.competition_multiplier.get(
            _competition_key(candidate.competition_count),
            1.0,
        )
        base *= multiplier
    elif candidate.competition_count:
        base *= max(0.60, 1.0 - (0.10 * candidate.competition_count))

    return max(0.0, min(1.0, base))


def _payment_probability(candidate: Candidate, config: ScoringConfig) -> float:
    if candidate.payment_confidence is not None:
        return candidate.payment_confidence
    return config.payment_probability.get(
        candidate.platform,
        config.payment_probability.get("unknown", 0.60),
    )


def _fee_rate(candidate: Candidate, config: ScoringConfig) -> float:
    if candidate.platform_fee_rate is not None:
        return candidate.platform_fee_rate
    return config.platform_fee_rate.get(
        candidate.platform,
        config.platform_fee_rate.get("unknown", 0.0),
    )


def score_candidate(
    candidate: Candidate,
    config: ScoringConfig,
    skills: SkillConfig,
) -> ScoredCandidate:
    reasons: list[str] = []
    blocking_reasons: list[str] = []

    fee_rate = _fee_rate(candidate, config)
    net_reward = candidate.reward_usd * (1.0 - fee_rate)
    gross_hourly = candidate.reward_usd / candidate.estimated_hours
    acceptance_probability = _acceptance_probability(candidate, config)
    payment_probability = _payment_probability(candidate, config)
    expected_value = net_reward * acceptance_probability * payment_probability
    expected_hourly = expected_value / candidate.estimated_hours
    effort_cap = config.effort_cap_for(candidate.reward_usd)
    skill_fit = _skill_fit(candidate, skills)

    fast_track = (
        candidate.reward_usd >= config.fast_track_reward_usd
        and candidate.estimated_hours <= config.fast_track_hours
        and candidate.competition_count == 0
        and not candidate.active_competing_pr
        and candidate.scope_clarity >= max(config.min_scope_clarity, 0.75)
    )

    if candidate.status != "open":
        blocking_reasons.append("El ticket no está abierto.")
    if not config.min_reward_usd <= candidate.reward_usd <= config.max_reward_usd:
        blocking_reasons.append(
            f"Recompensa fuera del rango USD {config.min_reward_usd:.0f}-{config.max_reward_usd:.0f}."
        )
    if candidate.estimated_hours > effort_cap:
        blocking_reasons.append(
            f"Esfuerzo estimado {candidate.estimated_hours:.1f}h supera el tope {effort_cap:.1f}h."
        )
    if candidate.assigned_to_other and not candidate.assigned_to_us:
        blocking_reasons.append("El trabajo ya está asignado a otra persona.")
    if (
        config.reject_active_competing_pr
        and candidate.active_competing_pr
        and not candidate.assigned_to_us
    ):
        blocking_reasons.append("Existe un PR competidor activo.")
    if (
        config.require_funded_contract
        and candidate.contract_type == "contracted"
        and not candidate.funded
    ):
        blocking_reasons.append("El contrato no tiene milestone/fondos confirmados.")
    if candidate.scope_clarity < config.min_scope_clarity:
        blocking_reasons.append(
            f"Claridad de alcance {candidate.scope_clarity:.0%} inferior al mínimo "
            f"{config.min_scope_clarity:.0%}."
        )
    if expected_hourly < config.min_expected_hourly_usd:
        blocking_reasons.append(
            f"Valor esperado USD {expected_hourly:.2f}/h inferior al objetivo "
            f"USD {config.min_expected_hourly_usd:.2f}/h."
        )

    if fast_track:
        reasons.append("Fast track: al menos USD 100, hasta 2h y sin competencia visible.")
    if candidate.competition_count:
        reasons.append(
            f"Competencia declarada: {candidate.competition_count}; se descuenta probabilidad de cobro."
        )
    else:
        reasons.append("Sin competidores declarados.")
    if candidate.contract_type in {"open_race", "contest"}:
        reasons.append("El pago depende de ganar o ser seleccionado.")
    if candidate.contract_type == "contracted" and candidate.funded:
        reasons.append("Contrato con fondos confirmados.")
    if not candidate.preflight_complete and not blocking_reasons:
        reasons.append("Falta preflight manual: estado, asignación, PRs, alcance y pago.")

    rate_ratio = min(
        3.0,
        expected_hourly / max(config.min_expected_hourly_usd, 0.01),
    )
    rate_score = (rate_ratio / 3.0) * 45.0
    clarity_score = candidate.scope_clarity * 20.0
    skill_score = skill_fit * 15.0
    payment_score = payment_probability * 10.0
    competition_score = (
        config.competition_multiplier.get(_competition_key(candidate.competition_count), 0.0)
        * 10.0
    )
    fast_track_bonus = 5.0 if fast_track else 0.0
    priority_score = min(
        100.0,
        rate_score
        + clarity_score
        + skill_score
        + payment_score
        + competition_score
        + fast_track_bonus,
    )

    if blocking_reasons:
        decision = "SKIP"
    elif not candidate.preflight_complete:
        decision = "REVIEW"
    else:
        decision = "GO"

    reasons = blocking_reasons + reasons
    return ScoredCandidate(
        candidate=candidate,
        decision=decision,
        priority_score=priority_score,
        gross_hourly_usd=gross_hourly,
        net_reward_usd=net_reward,
        acceptance_probability=acceptance_probability,
        payment_probability=payment_probability,
        expected_value_usd=expected_value,
        expected_hourly_usd=expected_hourly,
        effort_cap_hours=effort_cap,
        skill_fit=skill_fit,
        fast_track=fast_track,
        reasons=tuple(reasons),
    )


def score_candidates(
    candidates: Iterable[Candidate],
    config: ScoringConfig,
    skills: SkillConfig,
) -> list[ScoredCandidate]:
    scored = [score_candidate(candidate, config, skills) for candidate in candidates]
    return sorted(
        scored,
        key=lambda item: (
            DECISION_ORDER[item.decision],
            -item.priority_score,
            -item.expected_hourly_usd,
            -item.candidate.reward_usd,
        ),
    )
