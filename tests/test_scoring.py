from pathlib import Path
import unittest

from resolve_scout.config import load_scoring_config, load_skill_config
from resolve_scout.models import Candidate
from resolve_scout.scoring import score_candidate


ROOT = Path(__file__).resolve().parents[1]


class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_scoring_config(ROOT / "config" / "scoring.toml")
        cls.skills = load_skill_config(ROOT / "config" / "skills.toml")

    def candidate(self, **overrides):
        values = {
            "id": "test:1",
            "title": "Automation fix",
            "url": "https://example.com/ticket",
            "platform": "upwork",
            "reward_usd": 100,
            "estimated_hours": 2,
            "contract_type": "contracted",
            "competition_count": 0,
            "funded": True,
            "preflight_complete": True,
            "scope_clarity": 0.9,
            "skills": ("python", "automation"),
        }
        values.update(overrides)
        return Candidate(**values)

    def test_fast_tracks_funded_100_dollar_two_hour_contract(self):
        result = score_candidate(self.candidate(), self.config, self.skills)
        self.assertEqual(result.decision, "GO")
        self.assertTrue(result.fast_track)
        self.assertGreater(result.expected_hourly_usd, 15)

    def test_rejects_unfunded_contract(self):
        result = score_candidate(
            self.candidate(funded=False),
            self.config,
            self.skills,
        )
        self.assertEqual(result.decision, "SKIP")
        self.assertTrue(any("fondos" in reason for reason in result.reasons))

    def test_rejects_active_competing_pr(self):
        result = score_candidate(
            self.candidate(
                platform="algora",
                contract_type="open_race",
                active_competing_pr=True,
                competition_count=1,
            ),
            self.config,
            self.skills,
        )
        self.assertEqual(result.decision, "SKIP")
        self.assertTrue(any("PR competidor" in reason for reason in result.reasons))

    def test_unverified_candidate_requires_review(self):
        result = score_candidate(
            self.candidate(preflight_complete=False),
            self.config,
            self.skills,
        )
        self.assertEqual(result.decision, "REVIEW")

    def test_rejects_effort_above_reward_tier(self):
        result = score_candidate(
            self.candidate(reward_usd=30, estimated_hours=3),
            self.config,
            self.skills,
        )
        self.assertEqual(result.decision, "SKIP")
        self.assertTrue(any("supera el tope" in reason for reason in result.reasons))

    def test_competition_reduces_expected_hourly(self):
        clean = score_candidate(
            self.candidate(platform="algora", contract_type="open_race"),
            self.config,
            self.skills,
        )
        crowded = score_candidate(
            self.candidate(
                platform="algora",
                contract_type="open_race",
                competition_count=2,
            ),
            self.config,
            self.skills,
        )
        self.assertLess(crowded.expected_hourly_usd, clean.expected_hourly_usd)


if __name__ == "__main__":
    unittest.main()
