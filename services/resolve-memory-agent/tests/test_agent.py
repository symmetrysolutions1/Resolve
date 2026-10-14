import unittest

from resolve_memory_agent.agent import record_human_review, resolve_case


class FakeMemory:
    def __init__(self):
        self.cases = {}
        self.events = {}

    def remember(self, case, event):
        self.cases[case["case_id"]] = dict(case)
        self.events.setdefault(case["case_id"], []).append(dict(event))

    def recall(self, case_id):
        return self.cases.get(case_id)

    def history(self, case_id):
        return self.events.get(case_id, [])


class ResolveMemoryTests(unittest.TestCase):
    def setUp(self):
        self.store = FakeMemory()
        self.evidence = {"source": "sensor-7", "claim": "within range", "observed_at": "2026-08-01T12:00:00Z"}

    def test_verifies_complete_evidence_and_remembers_it(self):
        result = resolve_case(self.store, {"evidence": self.evidence})
        self.assertEqual("verified", result.status)
        self.assertEqual(1, len(self.store.history(result.case_id)))

    def test_flags_incomplete_evidence(self):
        result = resolve_case(self.store, {"evidence": {"source": "sensor-7"}})
        self.assertEqual("needs_review", result.status)
        self.assertIn("missing:claim", result.findings)

    def test_reuses_prior_decision_across_sessions(self):
        first = resolve_case(self.store, {"evidence": self.evidence})
        second = resolve_case(self.store, {"case_id": first.case_id, "evidence": self.evidence})
        self.assertEqual("verified", second.status)
        self.assertEqual(2, second.remembered_events)
        self.assertEqual("recalled", self.store.history(first.case_id)[1]["kind"])

    def test_human_review_is_audited(self):
        first = resolve_case(self.store, {"evidence": {"source": "sensor-7"}})
        reviewed = record_human_review(self.store, first.case_id, "reviewer@example.org", "verified", "checked source")
        self.assertEqual("verified", reviewed["case"]["status"])
        self.assertEqual("human_review", self.store.history(first.case_id)[1]["kind"])


if __name__ == "__main__":
    unittest.main()

