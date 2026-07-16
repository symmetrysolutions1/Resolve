import unittest

from resolve_scout.sources.github import (
    detect_skills,
    estimate_hours,
    issue_to_candidate,
    parse_reward_usd,
)


class RewardParserTests(unittest.TestCase):
    def test_parses_common_usd_formats(self):
        cases = {
            "Fix bug - $30": 30.0,
            "Bounty USD 100": 100.0,
            "Reward: 250 USDC": 250.0,
            "Prize USDG 1,500": 1500.0,
            "Plain dollar amount $1000": 1000.0,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(parse_reward_usd(text), expected)

    def test_returns_highest_explicit_currency_amount(self):
        self.assertEqual(parse_reward_usd("First USD 30, final payout $100"), 100.0)

    def test_ignores_plain_numbers(self):
        self.assertIsNone(parse_reward_usd("Issue 300 needs 2 tests"))

    def test_detects_skills_and_effort(self):
        text = "Python API automation with webhook and regression tests"
        self.assertIn("python", detect_skills(text))
        self.assertIn("automation", detect_skills(text))
        self.assertEqual(estimate_hours(text), 8.0)

    def test_converts_github_issue_to_unverified_candidate(self):
        issue = {
            "id": 123,
            "title": "$100 Fix Python API regression",
            "body": (
                "Steps to reproduce are listed here. Expected behavior is documented. "
                "Acceptance criteria: add a regression test and update the endpoint."
            ),
            "html_url": "https://github.com/acme/repo/issues/1",
            "repository_url": "https://api.github.com/repos/acme/repo",
            "state": "open",
            "comments": 0,
            "labels": [{"name": "bounty"}],
            "assignees": [],
        }
        candidate = issue_to_candidate(issue)
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.reward_usd, 100.0)
        self.assertFalse(candidate.preflight_complete)
        self.assertEqual(candidate.contract_type, "open_race")

    def test_comments_do_not_claim_known_competitors(self):
        issue = {
            "id": 124,
            "title": "$100 Fix Python API regression",
            "body": "Acceptance criteria: add a regression test.",
            "html_url": "https://github.com/acme/repo/issues/2",
            "state": "open",
            "comments": 20,
            "labels": [{"name": "bounty"}],
            "assignees": [],
        }
        candidate = issue_to_candidate(issue)
        self.assertEqual(candidate.competition_count, 0)
        self.assertEqual(candidate.source_data["comments"], 20)


if __name__ == "__main__":
    unittest.main()
