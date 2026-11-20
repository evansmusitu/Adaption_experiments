"""Research validity checks for paired improvement statistics (offline only)."""
import unittest

from proofbench.benchmark import make_cases
from proofbench.comparison import compare


def oracle_predictions(rows):
    return [{"id": x["id"], **x["gold"]} for x in rows]


def invalid_predictions(rows):
    wrong = []
    for r in rows:
        kind = "numeric" if r["gold"]["kind"] == "clarify" else "clarify"
        wrong.append({"id": r["id"], "kind": kind, "value": None, "unit": r["gold"]["unit"]})
    return wrong


class MatchedComparisonTests(unittest.TestCase):
    def test_no_measured_change_means_zero_difference(self):
        cases = make_cases("dev", pairs_per_family=2)
        same = oracle_predictions(cases)
        report = compare(cases, same, same, resamples=200)
        self.assertEqual(report["baseline_accuracy"], 1)
        self.assertEqual(report["candidate_accuracy"], 1)
        self.assertEqual(report["delta_accuracy"], 0)
        self.assertEqual(report["mcnemar_exact_p"], 1)
        self.assertEqual(report["paired_bootstrap_95"], [0, 0])

    def test_clear_improvement_has_positive_pair_bootstrap_ci(self):
        cases = make_cases("dev", pairs_per_family=3)
        old, new = invalid_predictions(cases), oracle_predictions(cases)
        report = compare(cases, old, new, resamples=300)
        self.assertEqual(report["baseline_accuracy"], 0)
        self.assertEqual(report["candidate_accuracy"], 1)
        self.assertEqual(report["delta_accuracy"], 1)
        self.assertEqual(report["discordant"]["candidate_only_correct"], len(cases))
        self.assertEqual(report["discordant"]["baseline_only_correct"], 0)
        self.assertEqual(report["paired_bootstrap_95"], [1, 1])
        self.assertLess(report["mcnemar_exact_p"], 0.01)
        self.assertEqual(report["paired_scenario_groups"], len(cases)//2)

    def test_missing_predictions_count_as_failures(self):
        cases = make_cases("stress", pairs_per_family=2)
        report = compare(cases, [], oracle_predictions(cases), resamples=200)
        self.assertEqual(report["baseline_accuracy"], 0)
        self.assertEqual(report["candidate_accuracy"], 1)

    def test_unknown_and_duplicate_predictions_are_rejected(self):
        cases = make_cases("stress", pairs_per_family=1)
        good = oracle_predictions(cases)
        with self.assertRaises(ValueError):
            compare(cases, good, good + [good[0]], resamples=100)
        with self.assertRaises(ValueError):
            compare(cases, good + [{"id": "not-a-case", "kind": "numeric"}], good, resamples=100)

    def test_invalid_bootstrap_setting_rejected(self):
        cases = make_cases("dev", pairs_per_family=1)
        with self.assertRaises(ValueError):
            compare(cases, [], [], resamples=0)


if __name__ == "__main__":
    unittest.main()
