from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import json
import unittest

from resolve_scout.cli import main


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_doctor(self):
        output = StringIO()
        with redirect_stdout(output):
            result = main(["doctor"])
        self.assertEqual(result, 0)
        self.assertIn("Doctor: OK", output.getvalue())

    def test_demo_writes_all_reports(self):
        destination = ROOT / ".artifacts" / "test-demo"
        destination.mkdir(parents=True, exist_ok=True)
        output = StringIO()
        with redirect_stdout(output):
            result = main(["demo", "--output", str(destination)])
        self.assertEqual(result, 0)

        self.assertTrue((destination / "ranked.json").exists())
        self.assertTrue((destination / "ranked.csv").exists())
        self.assertTrue((destination / "shortlist.md").exists())

        payload = json.loads((destination / "ranked.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["summary"]["total"], 8)
        self.assertGreaterEqual(payload["summary"]["GO"], 2)
        self.assertGreaterEqual(payload["summary"]["SKIP"], 2)


if __name__ == "__main__":
    unittest.main()
