"""Offline contracts for secure, read-only Adaption import inspection."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from proofbench.adaption_status import inspect_import

ID = "11111111-2222-4333-8444-555555555555"


class ImportStatusTests(unittest.TestCase):
    def fake(self, status="awaiting_input", count=240):
        ds = Mock()
        ds.get_status.return_value = SimpleNamespace(dataset_id=ID, status=status, row_count=count)
        maker = Mock(return_value=SimpleNamespace(datasets=ds))
        return maker, ds

    def test_ready_only_when_waiting_for_adaptation_and_240_rows(self):
        factory, ds = self.fake()
        report = inspect_import(ID, "test-key", factory)
        self.assertEqual(report, {"dataset_id": ID, "status": "awaiting_input", "row_count": 240, "ready_for_quote": True})
        factory.assert_called_once_with(api_key="test-key")
        ds.get_status.assert_called_once_with(ID)
        ds.adapt.assert_not_called()

    def test_wrong_row_count_fails_closed(self):
        factory, _ = self.fake(count=239)
        self.assertFalse(inspect_import(ID, "key", factory)["ready_for_quote"])

    def test_pending_and_succeeded_not_ready_for_quote(self):
        for status in ("pending", "running", "succeeded", "failed"):
            with self.subTest(status=status):
                factory, _ = self.fake(status=status)
                self.assertFalse(inspect_import(ID, "key", factory)["ready_for_quote"])

    def test_invent_id_and_missing_secret_rejected_without_call(self):
        factory, _ = self.fake()
        with self.assertRaises(ValueError):
            inspect_import("5ef42194-6814-45fb-8841-8116482928fa", "key", factory)
        with self.assertRaises(PermissionError):
            inspect_import(ID, "", factory)
        factory.assert_not_called()

    def test_disallows_mismatched_provider_id(self):
        factory, ds = self.fake()
        ds.get_status.return_value.dataset_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
        with self.assertRaises(RuntimeError):
            inspect_import(ID, "key", factory)


if __name__ == "__main__":
    unittest.main()
