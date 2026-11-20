"""Offline security tests for Adaption upload gating and dataset integrity."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from proofbench.benchmark import write_release
from proofbench.adaption_bridge import validate_training_export, upload_once

APPROVAL = "APPROVE PROOFBENCH DATA UPLOAD"


class AdaptionBridgeTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.folder = Path(self.work.name)
        write_release(self.folder)

    def test_verified_export_is_only_prompt_completion(self):
        info = validate_training_export(self.folder)
        self.assertEqual(info["rows"], 240)
        self.assertEqual(len(info["sha256"]), 64)
        self.assertTrue((self.folder / "train.jsonl").exists())

    def test_tampering_with_training_data_fails_closed(self):
        with (self.folder / "train.jsonl").open("a", encoding="utf-8") as f:
            f.write('{"prompt":"injected","completion":"bad"}\n')
        with self.assertRaises(ValueError):
            validate_training_export(self.folder)

    def test_denied_approval_never_calls_provider(self):
        fake = Mock(return_value="new-id")
        with self.assertRaises(PermissionError):
            upload_once(self.folder, approval="yes", git_ref="refs/heads/main",
                        api_key="test", uploader=fake)
        fake.assert_not_called()

    def test_denied_branch_never_calls_provider(self):
        fake = Mock(return_value="new-id")
        with self.assertRaises(PermissionError):
            upload_once(self.folder, approval=APPROVAL, git_ref="refs/pull/1/merge",
                        api_key="test", uploader=fake)
        fake.assert_not_called()

    def test_missing_api_key_never_calls_provider(self):
        fake = Mock(return_value="new-id")
        with self.assertRaises(PermissionError):
            upload_once(self.folder, approval=APPROVAL, git_ref="refs/heads/main",
                        api_key="", uploader=fake)
        fake.assert_not_called()

    def test_sdk_upload_creates_adaptation_ready_source_without_launch(self):
        """Import should be adaptation-ready, but must not start a paid run."""
        import sys
        from types import SimpleNamespace
        from unittest.mock import patch
        from proofbench.adaption_bridge import _adaption_sdk_upload

        dataset_client = Mock()
        dataset_client.upload_file.return_value = SimpleNamespace(dataset_id="adapt-source-test-id")
        fake_client = Mock()
        fake_client.datasets = dataset_client
        fake_adaption = SimpleNamespace(Adaption=Mock(return_value=fake_client))
        with patch.dict(sys.modules, {"adaption": fake_adaption}):
            dataset_id = _adaption_sdk_upload("train.jsonl", "secret-for-tests")
        self.assertEqual(dataset_id, "adapt-source-test-id")
        fake_adaption.Adaption.assert_called_once_with(api_key="secret-for-tests")
        dataset_client.upload_file.assert_called_once_with(
            "train.jsonl",
            processing_mode="adapt",
        )
        dataset_client.adapt.assert_not_called()
        fake_client.autoscientist.create.assert_not_called()

    def test_success_calls_provider_once_on_verified_file(self):
        fake = Mock(return_value="verified-dataset-id")
        result = upload_once(self.folder, approval=APPROVAL, git_ref="refs/heads/main",
                             api_key="test-key", uploader=fake)
        self.assertEqual(result["dataset_id"], "verified-dataset-id")
        self.assertEqual(result["rows"], 240)
        fake.assert_called_once_with(str(self.folder / "train.jsonl"), "test-key")


if __name__ == "__main__":
    unittest.main()
