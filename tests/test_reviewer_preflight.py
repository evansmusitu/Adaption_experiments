"""Fail-closed review gate tests; no Adaption content or paid calls."""
from __future__ import annotations

import copy
import unittest

from proofbench.reviewer_preflight import inspect_review

DATASET_ID = "eefe77fe-ba8c-4d54-9341-97c327a47fd3"
RESTORED = {7, 10, 13, 26, 38, 44, 45, 48, 61, 76, 81, 83, 95, 96, 99}
SHA = {
    "source": "46f3ddb18efa5869b8dcd0b01839d1056397b3f14f690779c2faa1562a2a0c6b",
    "provider": "7127b6f681392ed43e63093ec371254c486c4e442f62d918d20944669dbeadb1",
    "candidate": "c84938d5febad9131c0dba3a2fa6938f5f56abce7e3009f8d3ee56e01a3dbc0a",
}


def fixture():
    manifest = {
        "label": "ORACLE_RESTORED_REVIEW_CANDIDATE_NOT_NATIVE_ADAPTION_OUTPUT",
        "dataset_id": DATASET_ID,
        "rows": 100,
        "provider_rows_unmodified": 85,
        "original_oracle_restored_rows": 15,
        "source_original_sha256": SHA["source"],
        "raw_provider_sha256": SHA["provider"],
        "candidate_sha256": SHA["candidate"],
    }
    review = {
        "dataset_id": DATASET_ID,
        "source_sha256": SHA["source"],
        "provider_sha256": SHA["provider"],
        "candidate_sha256": SHA["candidate"],
        "manual_review": True,
        "reviewed_on": "2026-11-21T19:00:00Z",
        "cases": [
            {
                "index_zero_based": i,
                "case_number": i + 1,
                "source": "restored_original" if i in RESTORED else "raw_provider",
                "verdict": "approved",
                "notes": "",
            }
            for i in range(100)
        ],
    }
    return review, manifest


class ReviewPreflightTests(unittest.TestCase):
    def test_100_complete_records_still_not_authed_or_publication_authorized(self):
        review, manifest = fixture()
        report = inspect_review(review, manifest)
        self.assertTrue(report["structurally_complete"])
        self.assertEqual(report["approved"], 100)
        self.assertFalse(report["reviewer_identity_verified"])
        self.assertFalse(report["output_redistribution_cleared"])
        self.assertFalse(report["ready_for_public_release"])

    def test_one_unreviewed_case_keeps_gate_closed(self):
        review, manifest = fixture()
        review["cases"][0]["verdict"] = "unreviewed"
        report = inspect_review(review, manifest)
        self.assertEqual(report["approved"], 99)
        self.assertFalse(report["structurally_complete"])

    def test_one_needs_fix_keeps_gate_closed(self):
        review, manifest = fixture()
        review["cases"][99]["verdict"] = "needs_fix"
        report = inspect_review(review, manifest)
        self.assertEqual(report["needs_fix"], 1)
        self.assertFalse(report["structurally_complete"])

    def test_rejects_duplicate_case_numbers(self):
        review, manifest = fixture()
        review["cases"][99]["case_number"] = 1
        with self.assertRaisesRegex(ValueError, "duplicate|case"):
            inspect_review(review, manifest)

    def test_rejects_hash_mismatch(self):
        review, manifest = fixture()
        review["candidate_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "digest|hash"):
            inspect_review(review, manifest)

    def test_rejects_mislabelled_restored_row(self):
        review, manifest = fixture()
        review["cases"][45]["source"] = "raw_provider"
        with self.assertRaisesRegex(ValueError, "source"):
            inspect_review(review, manifest)

    def test_manual_review_flag_alone_cannot_claim_human_completion(self):
        review, manifest = fixture()
        review["cases"][2]["verdict"] = "unreviewed"
        review["manual_review"] = True
        report = inspect_review(review, manifest)
        self.assertFalse(report["structurally_complete"])
        self.assertFalse(report["ready_for_public_release"])

    def test_rejects_invalid_note_type(self):
        review, manifest = fixture()
        review["cases"][3]["notes"] = {"reason": "untrusted"}
        with self.assertRaisesRegex(ValueError, "notes"):
            inspect_review(review, manifest)


if __name__ == "__main__":
    unittest.main()
