"""Offline read-only PROOFBENCH provider-export safety tests."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from proofbench.adaption_export import (
    DATASET_ID, EXPECTED_ROWS, download_for_review, extract_verified_rows,
)
from proofbench.benchmark import write_release


class AdaptionExportTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        write_release(self.root / "source")
        self.train = self.root / "source" / "train.jsonl"
        train = [json.loads(line) for line in self.train.read_text().splitlines() if line.strip()]
        self.rows = [
            {
                "original_prompt": row["prompt"],
                "original_completion": row["completion"],
                "rephrased_prompt": row["prompt"] + " (please solve carefully)",
                "final_completion": row["completion"] + " Confirmed.",
                "sensitive_provider_metadata": "never-export-this",
            }
            for row in train[:EXPECTED_ROWS]
        ]

    def payload(self):
        return ("\n".join(json.dumps(row) for row in self.rows) + "\n").encode("utf-8")

    def factory(self, status="succeeded", processed=EXPECTED_ROWS):
        ds = Mock()
        ds.get_status.return_value = SimpleNamespace(status=status, processed_rows=processed)
        ds.download.return_value.read.return_value = self.payload()
        factory = Mock(return_value=SimpleNamespace(datasets=ds))
        return factory, ds

    def test_projects_only_provider_and_source_verified_pairs(self):
        orig, new = extract_verified_rows(self.payload(), self.train)
        self.assertEqual(len(orig), 100)
        self.assertEqual(len(new), 100)
        self.assertEqual(orig[0]["prompt"], self.rows[0]["original_prompt"])
        self.assertEqual(new[0]["completion"], self.rows[0]["final_completion"])
        self.assertNotIn("sensitive_provider_metadata", new[0])

    def test_download_is_read_only_and_writes_distinct_hashed_review_files(self):
        factory, ds = self.factory()
        out = self.root / "out"
        metadata = download_for_review(out, "test-token", client_factory=factory)
        self.assertEqual(metadata["review_rows"], 100)
        self.assertEqual(metadata["source_rows"], 240)
        self.assertNotEqual(metadata["original_sha256"], metadata["improved_sha256"])
        self.assertFalse(metadata["content_review_completed"])
        ds.get_status.assert_called_once_with(DATASET_ID)
        ds.download.assert_called_once_with(DATASET_ID, file_format="jsonl")
        ds.adapt.assert_not_called()
        ds.upload_file.assert_not_called()
        self.assertEqual(hashlib.sha256((out / "improved.jsonl").read_bytes()).hexdigest(), metadata["improved_sha256"])
        self.assertNotIn("never-export-this", (out / "improved.jsonl").read_text())

    def test_unready_dataset_never_downloaded(self):
        for status, count in [("running", 100), ("succeeded", 99)]:
            with self.subTest(status=status, count=count):
                factory, ds = self.factory(status=status, processed=count)
                with self.assertRaises(ValueError):
                    download_for_review(self.root / "out", "token", client_factory=factory)
                ds.download.assert_not_called()

    def test_missing_key_never_contacts_provider(self):
        factory, ds = self.factory()
        with self.assertRaises(PermissionError):
            download_for_review(self.root / "out", "", client_factory=factory)
        factory.assert_not_called()

    def test_modified_provider_original_pair_fails_closed(self):
        self.rows[0]["original_completion"] = "Wrong"
        with self.assertRaises(ValueError):
            extract_verified_rows(self.payload(), self.train)

    def test_missing_enhanced_completion_fails_closed(self):
        del self.rows[0]["final_completion"]
        with self.assertRaises(ValueError):
            extract_verified_rows(self.payload(), self.train)

    def test_duplicate_provider_row_fails_closed(self):
        self.rows[-1] = self.rows[0].copy()
        with self.assertRaises(ValueError):
            extract_verified_rows(self.payload(), self.train)


if __name__ == "__main__":
    unittest.main()
