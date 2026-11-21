"""Offline contracts for audit-only, unlicensed provider review materials."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from proofbench.benchmark import write_release
from proofbench.candidate_integrity import verify_bundle

RESTORED = [7, 10, 13, 26, 38, 44, 45, 48, 61, 76, 81, 83, 95, 96, 99]


class CandidateIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        write_release(self.root / "dataset")
        originals = [json.loads(x) for x in (self.root / "dataset" / "train.jsonl").read_text().splitlines()]
        self.original = originals[:100]
        # Fake provider outputs are deliberately NOT genuine Adaption rows.
        self.improved = [{"prompt": row["prompt"] + " Rephrased.",
                          "completion": row["completion"] + " Provider improvement."}
                         for row in self.original]
        self.candidate = [self.original[i] if i in RESTORED else self.improved[i]
                          for i in range(100)]
        self.review = self.root / "review_only"
        self.review.mkdir()
        self.manifest = {
            "label": "ORACLE_RESTORED_REVIEW_CANDIDATE_NOT_NATIVE_ADAPTION_OUTPUT",
            "dataset_id": "eefe77fe-ba8c-4d54-9341-97c327a47fd3",
            "provider_run_id": "dataset-eefe77fe-ba8c-4d54-9341-97c327a47fd3-1795285525492",
            "provider_native_quality_score_applies_only_to_raw_provider_output": True,
            "rows": 100,
            "provider_rows_unmodified": 85,
            "original_oracle_restored_rows": 15,
            "confirmed_or_mismatched_enhanced_outputs_restored": [i for i in RESTORED if i != 45],
            "additional_prompt_drift_restored": [45],
            "independent_expert_review_completed": False,
            "real_model_comparison_completed": False,
            "provider_quality_grade_for_candidate": None,
        }
        self.write()

    def write(self):
        pairs = [
            ("original.jsonl", self.original, "source_original_sha256"),
            ("raw_adaption_improved.jsonl", self.improved, "raw_provider_sha256"),
            ("oracle_restored_candidate.jsonl", self.candidate, "candidate_sha256"),
        ]
        for filename, rows, digest_name in pairs:
            content = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows).encode()
            (self.review / filename).write_bytes(content)
            self.manifest[digest_name] = hashlib.sha256(content).hexdigest()
        (self.review / "candidate_manifest.json").write_text(json.dumps(self.manifest))

    def check(self):
        return verify_bundle(self.review, self.root / "dataset" / "train.jsonl")

    def test_preserves_85_provider_and_restores_15_exact_original_pairs(self):
        report = self.check()
        self.assertEqual(report["rows"], 100)
        self.assertEqual(report["retained_provider_rows"], 85)
        self.assertEqual(report["restored_original_rows"], 15)
        self.assertTrue(report["all_candidate_rows_exactly_traced"])
        self.assertFalse(report["cleared_for_public_release"])

    def test_rejects_unauthorized_candidate_change_even_with_matching_hash(self):
        self.candidate[1] = {"prompt": "injected", "completion": "wrong"}
        self.write()
        with self.assertRaisesRegex(ValueError, "exactly provider"):
            self.check()

    def test_rejects_wrong_source_even_with_new_matching_hashes(self):
        self.original[0] = {"prompt": "unknown question", "completion": "unknown answer"}
        self.write()
        with self.assertRaisesRegex(ValueError, "training source"):
            self.check()

    def test_rejects_tampering_without_manifest_update(self):
        (self.review / "oracle_restored_candidate.jsonl").write_text("tampered")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.check()

    def test_rejects_unapproved_restoration_manifest(self):
        self.manifest["additional_prompt_drift_restored"] = []
        (self.review / "candidate_manifest.json").write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, "restoration indices"):
            self.check()

    def test_rejects_claimed_quality_grade_on_corrected_candidate(self):
        self.manifest["provider_quality_grade_for_candidate"] = "A"
        (self.review / "candidate_manifest.json").write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, "quality grade"):
            self.check()

    def test_rejects_duplicate_exported_source_row(self):
        self.original[1] = self.original[0]
        self.write()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check()


if __name__ == "__main__":
    unittest.main()
