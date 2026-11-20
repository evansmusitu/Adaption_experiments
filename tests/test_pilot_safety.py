"""Security and idempotency tests for the manual-only PROOFBENCH pilot."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import launch_proofbench_pilot as pilot


class PilotSafetyTests(unittest.TestCase):
    def setUp(self):
        self.env = {
            "ADAPTION_API_KEY": "dummy-unit-test-only",
            "PILOT_APPROVAL": pilot.EXPECTED_APPROVAL,
            "GITHUB_REF": "refs/heads/main",
        }

    def test_disallows_missing_approval_without_network(self):
        env = dict(self.env, PILOT_APPROVAL="yes")
        with patch.dict(os.environ, env, clear=True):
            with patch.object(pilot, "api_post") as mock:
                self.assertEqual(pilot.main(), 2)
                mock.assert_not_called()

    def test_disallows_non_main_without_network(self):
        env = dict(self.env, GITHUB_REF="refs/heads/unsafe")
        with patch.dict(os.environ, env, clear=True):
            with patch.object(pilot, "api_post") as mock:
                self.assertEqual(pilot.main(), 2)
                mock.assert_not_called()

    def test_disallows_missing_secret_without_network(self):
        env = dict(self.env)
        env.pop("ADAPTION_API_KEY")
        with patch.dict(os.environ, env, clear=True):
            with patch.object(pilot, "api_post") as mock:
                self.assertEqual(pilot.main(), 2)
                mock.assert_not_called()

    def test_disallows_quote_over_budget(self):
        with patch.dict(os.environ, self.env, clear=True):
            with patch.object(pilot, "api_post", return_value={
                "estimatedCredits": 11, "availableCredits": 100
            }) as mock:
                self.assertEqual(pilot.main(), 1)
                self.assertEqual(mock.call_count, 1)
                self.assertIs(mock.call_args.args[1]["estimate"], True)

    def test_disallows_unknown_credit_balance(self):
        with patch.dict(os.environ, self.env, clear=True):
            with patch.object(pilot, "api_post", return_value={
                "estimatedCredits": 10
            }) as mock:
                self.assertEqual(pilot.main(), 1)
                self.assertEqual(mock.call_count, 1)

    def test_quote_and_launch_use_same_idempotency(self):
        with patch.dict(os.environ, self.env, clear=True):
            with patch.object(pilot, "api_post", side_effect=[
                {"estimatedCredits": 10, "availableCredits": 10},
                {"dataset_id": "unit-test-dataset", "status": "running"},
            ]) as mock:
                self.assertEqual(pilot.main(), 0)
                self.assertEqual(mock.call_count, 2)
                quoted = mock.call_args_list[0].args[1]
                launched = mock.call_args_list[1].args[1]
                self.assertIs(quoted["estimate"], True)
                self.assertNotIn("estimate", launched)
                self.assertEqual(
                    quoted["idempotency_key"], launched["idempotency_key"]
                )
                self.assertEqual(launched["rows"], 100)

if __name__ == "__main__":
    unittest.main()
