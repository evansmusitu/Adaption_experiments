"""Regression tests for a separately implemented financial arithmetic oracle."""
import json
import tempfile
import unittest
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch
from proofbench.benchmark import write_release
from proofbench.oracle_recheck import verify_train


class SourceOracleRecheckTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = Path(self.dir.name) / "train.jsonl"
        write_release(Path(self.dir.name))
        self.rows = [json.loads(s) for s in self.path.read_text().splitlines()]

    def save(self):
        self.path.write_text("".join(json.dumps(row) + "\n" for row in self.rows))

    def test_all_240_cases_are_independently_correct_in_six_equal_families(self):
        report = verify_train(self.path)
        self.assertEqual(report["checked"], 240)
        self.assertEqual(report["verified"], 240)
        self.assertEqual(set(report["families"].values()), {40})
        self.assertEqual(len(report["families"]), 6)
        self.assertFalse(report["establishes_model_accuracy"])

    def test_altered_numeric_result_fails_closed(self):
        idx = next(i for i, row in enumerate(self.rows) if row["completion"].startswith("Result:"))
        self.rows[idx]["completion"] = "Result: 999999.99 USD. Incorrect number."
        self.save()
        with self.assertRaisesRegex(ValueError, "case|mismatch|amount"):
            verify_train(self.path)

    def test_fake_converted_amount_with_no_fx_rate_rejected(self):
        idx = next(i for i, row in enumerate(self.rows) if "No exchange rate" in row["prompt"])
        self.rows[idx]["completion"] = "Result: 100.00 USD. Guess."
        self.save()
        with self.assertRaisesRegex(ValueError, "case|mismatch|missing"):
            verify_train(self.path)

    def test_duplicate_prompt_rejected(self):
        self.rows[1] = dict(self.rows[0])
        self.save()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            verify_train(self.path)

    def test_cli_distinguishes_success_boolean_from_verified_row_count(self):
        from proofbench.oracle_recheck import main
        output = StringIO()
        with patch("sys.argv", ["oracle_recheck", "--train", str(self.path)]):
            with redirect_stdout(output):
                rc = main()
        report = json.loads(output.getvalue())
        self.assertEqual(rc, 0)
        self.assertIs(report["ok"], True)
        self.assertEqual(report["verified"], 240)

    def test_missing_case_rejected(self):
        self.rows.pop()
        self.save()
        with self.assertRaisesRegex(ValueError, "240"):
            verify_train(self.path)

    def test_unexpected_column_rejected(self):
        self.rows[0]["private_identifier"] = "secret"
        self.save()
        with self.assertRaisesRegex(ValueError, "columns|schema"):
            verify_train(self.path)


if __name__ == "__main__":
    unittest.main()
