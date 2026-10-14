import unittest

from resolve_lineage_agent.agent import resolve_evidence


URN = "urn:li:dataset:(urn:li:dataPlatform:s3,evidence,PROD)"


class ResolveEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.context = {
            "urn": URN,
            "owners": ["urn:li:corpuser:reviewer"],
            "upstreams": ["urn:li:dataset:(urn:li:dataPlatform:s3,raw,PROD)"],
            "schema_fields": ["id", "score"],
        }
        self.evidence = {
            "dataset_urn": URN,
            "claimed_fields": ["id", "score"],
            "observations": [{"id": "1", "score": 0.9}],
        }

    def test_verifies_complete_evidence(self):
        receipt = resolve_evidence(
            self.evidence, self.context, checked_at="2026-08-01T00:00:00+00:00"
        )
        self.assertEqual(receipt["status"], "verified")
        self.assertEqual(receipt["findings"], [])
        self.assertEqual(len(receipt["receipt_sha256"]), 64)

    def test_blocks_unknown_claimed_field(self):
        evidence = {**self.evidence, "claimed_fields": ["id", "secret_score"]}
        receipt = resolve_evidence(evidence, self.context)
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("FIELD_NOT_IN_DATAHUB_SCHEMA", [item["code"] for item in receipt["findings"]])

    def test_blocks_unowned_dataset(self):
        context = {**self.context, "owners": []}
        receipt = resolve_evidence(self.evidence, context)
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("UNOWNED_DATASET", [item["code"] for item in receipt["findings"]])

    def test_receipt_digest_is_deterministic(self):
        first = resolve_evidence(self.evidence, self.context, checked_at="fixed")
        second = resolve_evidence(self.evidence, self.context, checked_at="fixed")
        self.assertEqual(first["receipt_sha256"], second["receipt_sha256"])


if __name__ == "__main__":
    unittest.main()

