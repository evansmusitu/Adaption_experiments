"""Submission evidence integrity tests. All inputs in tests are MOCK fixtures."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from proofbench.submission_gate import inspect

SOURCE_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
IMPROVED_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"


def write_fixture(root):
    root.mkdir(exist_ok=True, parents=True)
    (root / "README.md").write_text("A complete experiment README", encoding="utf-8")
    (root / "demo").mkdir(exist_ok=True)
    (root / "demo" / "index.html").write_text("<html>Reproducible demo</html>", encoding="utf-8")
    (root / "evidence").mkdir(exist_ok=True)
    originals = (root / "evidence" / "original.jsonl")
    improved = (root / "evidence" / "improved.jsonl")
    originals.write_text('{"prompt":"Q","completion":"A"}\n', encoding="utf-8")
    improved.write_text('{"enhanced_prompt":"Q2","enhanced_completion":"A2"}\n', encoding="utf-8")
    entry = {
        "original_dataset_id": SOURCE_ID,
        "improved_dataset_id": IMPROVED_ID,
        "run_id": "dataset-run-0001",
        "evaluation_provider": "adaption",
        "evaluation_status": "succeeded",
        "score_before": 8.1,
        "score_after": 8.5,
        "original_file": "evidence/original.jsonl",
        "improved_file": "evidence/improved.jsonl",
        "original_sha256": hashlib.sha256(originals.read_bytes()).hexdigest(),
        "improved_sha256": hashlib.sha256(improved.read_bytes()).hexdigest(),
        "source_license": "CC0-1.0",
    }
    (root / "evidence" / "manifest.json").write_text(json.dumps(entry), encoding="utf-8")
    return entry


class SubmissionIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.entry = write_fixture(self.root)

    def _set(self, **changes):
        self.entry.update(changes)
        (self.root / "evidence" / "manifest.json").write_text(json.dumps(self.entry), encoding="utf-8")

    def test_all_required_structural_evidence(self):
        report = inspect(self.root)
        self.assertTrue(report["structurally_ready"])
        self.assertEqual(report["errors"], [])

    def test_missing_evidence_is_blocked(self):
        (self.root / "evidence" / "manifest.json").unlink()
        self.assertFalse(inspect(self.root)["structurally_ready"])

    def test_modified_dataset_file_detected_by_hash(self):
        with (self.root / "evidence" / "improved.jsonl").open("a") as f:
            f.write('{"prompt":"tampered"}\n')
        self.assertFalse(inspect(self.root)["structurally_ready"])

    def test_same_dataset_identifier_rejected(self):
        self._set(improved_dataset_id=SOURCE_ID)
        self.assertFalse(inspect(self.root)["structurally_ready"])

    def test_same_dataset_identifier_allowed_only_for_verified_in_place_run_shape(self):
        # Adaption may process source and enhanced rows in one dataset ID,
        # distinguished by a real run ID and two different exported artifacts.
        self._set(
            improved_dataset_id=SOURCE_ID,
            in_place_adaptation=True,
            run_id=f"dataset-{SOURCE_ID}-1795285525492",
        )
        self.assertTrue(inspect(self.root)["structurally_ready"])

    def test_in_place_flag_rejects_unrelated_run_identifier(self):
        self._set(
            improved_dataset_id=SOURCE_ID,
            in_place_adaptation=True,
            run_id="dataset-unrelated-1795285525492",
        )
        self.assertFalse(inspect(self.root)["structurally_ready"])

    def test_in_place_flag_does_not_bypass_file_integrity(self):
        self._set(
            improved_dataset_id=SOURCE_ID,
            in_place_adaptation=True,
            run_id=f"dataset-{SOURCE_ID}-1795285525492",
        )
        (self.root / "evidence" / "improved.jsonl").unlink()
        self.assertFalse(inspect(self.root)["structurally_ready"])

    def test_fake_unfinished_evaluation_rejected(self):
        self._set(evaluation_status="pending")
        self.assertFalse(inspect(self.root)["structurally_ready"])

    def test_no_demo_rejected(self):
        (self.root / "demo" / "index.html").unlink()
        self.assertFalse(inspect(self.root)["structurally_ready"])

    def test_missing_or_non_numeric_scores_rejected(self):
        self._set(score_after="TBD")
        self.assertFalse(inspect(self.root)["structurally_ready"])

    def test_path_escape_rejected(self):
        self._set(improved_file="../not-in-evidence.jsonl")
        self.assertFalse(inspect(self.root)["structurally_ready"])


if __name__ == "__main__":
    unittest.main()
