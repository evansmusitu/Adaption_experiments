"""Offline credit, security, idempotency and cost-estimate guard tests."""
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

from proofbench.adaption_run import launch_pilot

DATASET_ID = "12345678-1234-4123-8123-123456789abc"
APPROVAL = "I APPROVE UP TO 10 ADAPTION CREDITS"


def sdk(quote_credit=8):
    datasets = Mock()
    datasets.adapt.side_effect = [
        SimpleNamespace(estimate=True, run_id=None,
                        estimated_credits_consumed=quote_credit,
                        estimated_minutes=4.5),
        SimpleNamespace(estimate=False, run_id="run-real-test-value",
                        estimated_credits_consumed=quote_credit,
                        estimated_minutes=4.5),
    ]
    factory = Mock(return_value=SimpleNamespace(datasets=datasets))
    return factory, datasets


class CreditGuardTests(unittest.TestCase):
    def test_refuses_missing_user_approval(self):
        factory, datasets = sdk()
        with self.assertRaises(PermissionError):
            launch_pilot(DATASET_ID, "key", "go", "refs/heads/main", factory)
        factory.assert_not_called()

    def test_refuses_wrong_branch(self):
        factory, datasets = sdk()
        with self.assertRaises(PermissionError):
            launch_pilot(DATASET_ID, "key", APPROVAL, "refs/pull/2/merge", factory)
        factory.assert_not_called()

    def test_refuses_missing_key(self):
        factory, datasets = sdk()
        with self.assertRaises(PermissionError):
            launch_pilot(DATASET_ID, "", APPROVAL, "refs/heads/main", factory)
        factory.assert_not_called()

    def test_refuses_known_invent_dataset(self):
        factory, datasets = sdk()
        with self.assertRaises(ValueError):
            launch_pilot("5ef42194-6814-45fb-8841-8116482928fa",
                         "key", APPROVAL, "refs/heads/main", factory)
        factory.assert_not_called()

    def test_refuses_quote_above_fixed_ceiling(self):
        factory, datasets = sdk(11)
        with self.assertRaises(ValueError):
            launch_pilot(DATASET_ID, "key", APPROVAL, "refs/heads/main", factory)
        self.assertEqual(datasets.adapt.call_count, 1)
        self.assertIs(datasets.adapt.call_args.kwargs["estimate"], True)

    def test_quote_must_be_explicit_estimate_only(self):
        factory, datasets = sdk()
        datasets.adapt.side_effect = [
            SimpleNamespace(estimate=True, run_id="unexpected",
                            estimated_credits_consumed=1,
                            estimated_minutes=0.5)
        ]
        with self.assertRaises(RuntimeError):
            launch_pilot(DATASET_ID, "key", APPROVAL, "refs/heads/main", factory)
        self.assertEqual(datasets.adapt.call_count, 1)

    def test_same_configuration_and_idempotency_for_quote_and_launch(self):
        factory, datasets = sdk(9)
        result = launch_pilot(DATASET_ID, "key", APPROVAL, "refs/heads/main", factory)
        self.assertEqual(result["run_id"], "run-real-test-value")
        self.assertEqual(result["quoted_credits"], 9)
        self.assertEqual(datasets.adapt.call_count, 2)
        quote, launch = datasets.adapt.call_args_list
        self.assertEqual(quote.args, (DATASET_ID,))
        self.assertEqual(launch.args, (DATASET_ID,))
        self.assertEqual(quote.kwargs["estimate"], True)
        self.assertNotIn("estimate", launch.kwargs)
        quoted_cfg = {k:v for k,v in quote.kwargs.items() if k != "estimate"}
        self.assertEqual(quoted_cfg, launch.kwargs)
        self.assertEqual(launch.kwargs["job_specification"]["max_rows"], 100)
        self.assertIn(DATASET_ID, launch.kwargs["job_specification"]["idempotency_key"])

    def test_malformed_id_refused_without_network(self):
        factory, datasets = sdk()
        with self.assertRaises(ValueError):
            launch_pilot("../../wrong", "key", APPROVAL, "refs/heads/main", factory)
        factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
