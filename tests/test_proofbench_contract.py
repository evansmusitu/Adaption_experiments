"""Contract tests for deterministic, adversarial financial-reasoning fixtures.

Each test exercises the same functions users invoke from the CLI. Tests never
call Adaption or use credentials.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from proofbench.benchmark import (
    make_cases, validate_splits, score_predictions, write_release,
)

FAMILIES = {
    "fx_missing", "inventory_conflict", "receipt_identity",
    "interest_method", "profit_overhead", "fee_basis",
}


def predictions_from_gold(cases):
    return [
        {
            "id": row["id"], "kind": row["gold"]["kind"],
            "value": row["gold"]["value"], "unit": row["gold"]["unit"],
        }
        for row in cases
    ]


class ProofbenchContractTests(unittest.TestCase):
    def test_family_coverage_and_reproducibility(self):
        first = make_cases("train", pairs_per_family=3)
        again = make_cases("train", pairs_per_family=3)
        self.assertEqual(first, again)
        self.assertEqual(len(first), 36)  # 6 families x 3 pairs x 2 variants
        self.assertEqual({r["family"] for r in first}, FAMILIES)
        self.assertEqual(len({r["id"] for r in first}), 36)
        self.assertEqual(len({r["pair_id"] for r in first}), 18)
        self.assertTrue(all(r["provenance"]["source"] == "deterministic_synthetic" for r in first))

    def test_splits_have_disjoint_scenarios_and_templates(self):
        parts = {s: make_cases(s, pairs_per_family=3) for s in ("train", "dev", "stress")}
        validate_splits(parts)
        for a in parts:
            for b in parts:
                if a != b:
                    self.assertFalse(
                        {r["scenario_id"] for r in parts[a]} &
                        {r["scenario_id"] for r in parts[b]}
                    )
                    self.assertFalse(
                        {r["template_id"] for r in parts[a]} &
                        {r["template_id"] for r in parts[b]}
                    )

    def test_every_pair_forces_a_different_correct_response(self):
        rows = make_cases("stress", pairs_per_family=4)
        pairs = {}
        for row in rows:
            pairs.setdefault(row["pair_id"], []).append(row)
            self.assertTrue(row["prompt"])
            self.assertTrue(row["completion"])
            gold = row["gold"]
            self.assertIn(gold["kind"], ("numeric", "clarify"))
            if gold["kind"] == "numeric":
                self.assertTrue(Decimal(gold["value"]).is_finite())
                self.assertIn(gold["unit"], ("USD", "units"))
            else:
                self.assertIsNone(gold["value"])
        self.assertEqual(len(pairs), 24)
        for pair_rows in pairs.values():
            self.assertEqual(len(pair_rows), 2)
            self.assertNotEqual(pair_rows[0]["prompt"], pair_rows[1]["prompt"])
            self.assertNotEqual(pair_rows[0]["gold"], pair_rows[1]["gold"])

    def test_perfect_predictions_and_pair_accuracy(self):
        rows = make_cases("dev", pairs_per_family=2)
        report = score_predictions(rows, predictions_from_gold(rows))
        self.assertEqual(report["total"], 24)
        self.assertEqual(report["correct"], 24)
        self.assertEqual(report["accuracy"], 1)
        self.assertEqual(report["strict_pair_accuracy"], 1)
        self.assertEqual(report["pairs_total"], 12)
        self.assertEqual(report["missing_predictions"], 0)

    def test_missing_and_incorrect_predictions_are_failures(self):
        rows = make_cases("dev", pairs_per_family=2)
        preds = predictions_from_gold(rows)
        preds[0]["kind"] = "clarify" if preds[0]["kind"] == "numeric" else "numeric"
        preds.pop(1)
        report = score_predictions(rows, preds)
        self.assertEqual(report["correct"], 22)
        self.assertEqual(report["missing_predictions"], 1)
        self.assertLess(report["strict_pair_accuracy"], 1)

    def test_unknown_duplicate_and_nonfinite_predictions_fail(self):
        rows = make_cases("dev", pairs_per_family=1)
        preds = predictions_from_gold(rows)
        with self.assertRaises(ValueError):
            score_predictions(rows, preds + [dict(preds[0])])
        with self.assertRaises(ValueError):
            score_predictions(rows, preds + [{"id": "unknown", "kind": "clarify"}])
        target = next(i for i, r in enumerate(rows) if r["gold"]["kind"] == "numeric")
        preds[target]["value"] = "NaN"
        self.assertLess(score_predictions(rows, preds)["accuracy"], 1)

    def test_clarification_units_are_not_interchangeable(self):
        rows = make_cases("dev", pairs_per_family=1)
        preds = predictions_from_gold(rows)
        target = next(i for i, row in enumerate(rows) if row["gold"]["kind"] == "clarify")
        preds[target]["unit"] = "units" if rows[target]["gold"]["unit"] == "USD" else "USD"
        self.assertEqual(score_predictions(rows, preds)["correct"], len(rows) - 1)

    def test_numeric_units_are_not_interchangeable(self):
        rows = make_cases("dev", pairs_per_family=1)
        preds = predictions_from_gold(rows)
        target = next(i for i, r in enumerate(rows) if r["gold"]["unit"] == "USD")
        preds[target]["unit"] = "units"
        self.assertEqual(score_predictions(rows, preds)["correct"], len(rows) - 1)

    def test_release_is_reproducible_and_valid_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            report1 = write_release(dest)
            before = {
                p.name: p.read_bytes()
                for p in dest.glob("*.jsonl")
            }
            report2 = write_release(dest)
            after = {p.name: p.read_bytes() for p in dest.glob("*.jsonl")}
            self.assertEqual(report1, report2)
            self.assertEqual(before, after)
            self.assertEqual(report1["counts"]["train"], 240)
            self.assertEqual(report1["counts"]["dev"], 120)
            self.assertEqual(report1["counts"]["stress"], 96)
            self.assertEqual(set(report1["sha256"]), set(before))
            train_row = json.loads((dest / "train.jsonl").read_text().splitlines()[0])
            self.assertEqual(set(train_row), {"prompt", "completion"})
            self.assertNotIn("gold", train_row)


if __name__ == "__main__":
    unittest.main()
