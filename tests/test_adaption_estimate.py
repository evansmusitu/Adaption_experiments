"""Contracts for estimate-only Adaption SDK calls. No real network requests."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from proofbench.adaption_estimate import estimate

VALID_ID = "11111111-2222-4333-8444-555555555555"


class QuoteOnlyTests(unittest.TestCase):
    def test_exact_estimate_only_mapping_and_limit(self):
        ds = Mock()
        ds.adapt.return_value = SimpleNamespace(
            estimate=True, run_id=None,
            estimated_credits_consumed=12.0, estimated_minutes=4.5
        )
        client = Mock(datasets=ds)
        factory = Mock(return_value=client)
        report = estimate(VALID_ID, "test-key", client_factory=factory)
        factory.assert_called_once_with(api_key="test-key")
        ds.adapt.assert_called_once_with(
            VALID_ID,
            estimate=True,
            column_mapping={"prompt": "prompt", "completion": "completion"},
            job_specification={"max_rows": 100},
            training_type="instruction_dataset",
        )
        self.assertEqual(report["estimated_credits"], 12.0)
        self.assertEqual(report["estimated_minutes"], 4.5)

    def test_rejects_unknown_or_malformed_id_without_network(self):
        factory = Mock()
        for bad in ("", "not-a-uuid", "../secrets", "5ef42194-6814-45fb-8841-8116482928fa"):
            with self.assertRaises(ValueError):
                estimate(bad, "token", client_factory=factory)
        factory.assert_not_called()

    def test_rejects_missing_credentials_without_network(self):
        factory = Mock()
        with self.assertRaises(PermissionError):
            estimate(VALID_ID, "", client_factory=factory)
        factory.assert_not_called()

    def test_rejects_if_provider_started_a_run(self):
        ds = Mock()
        ds.adapt.return_value = SimpleNamespace(
            estimate=False, run_id="unexpected-run",
            estimated_credits_consumed=10, estimated_minutes=3
        )
        with self.assertRaises(RuntimeError):
            estimate(VALID_ID, "token", client_factory=lambda **_: Mock(datasets=ds))

    def test_rejects_invalid_or_nonfinite_quote(self):
        ds = Mock()
        ds.adapt.return_value = SimpleNamespace(
            estimate=True, run_id=None,
            estimated_credits_consumed=float("nan"), estimated_minutes=1
        )
        with self.assertRaises(ValueError):
            estimate(VALID_ID, "token", client_factory=lambda **_: Mock(datasets=ds))


if __name__ == "__main__":
    unittest.main()
