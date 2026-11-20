#!/usr/bin/env python3
"""MUSITU PROOFBENCH: deterministic *development* cases and strict scorer.

Public template-based dev cases are NOT blind tests or model results.
No networking, third-party libraries, API secrets, or real customer data.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import json
from pathlib import Path

PENNY = Decimal("0.01")


def money(value: Decimal) -> str:
    return str(value.quantize(PENNY, rounding=ROUND_HALF_UP))


def build_cases() -> list[dict]:
    cases = []
    for i in range(20):
        qty = 8 + i
        sale = Decimal(250 + i * 7) / 100
        cost = Decimal(120 + i * 3) / 100
        transport = Decimal(3 + (i % 4))
        expected_profit = money(Decimal(qty) * (sale - cost) - transport)
        cases.append({
            "id": f"profit_{i:02d}", "family": "profit",
            "prompt": (
                f"A shop sold {qty} items at USD {sale} each. Unit cost was USD {cost} "
                f"and delivery cost USD {transport}. Calculate profit after delivery."
            ), "expected_value": expected_profit, "needs_clarification": False,
        })

        zig = Decimal(50 + i * 7)
        rate = Decimal(10 + (i % 9)) / 10
        pair = f"fx_{i:02d}"
        cases.append({
            "id": f"fx_missing_{i:02d}", "family": "missing_exchange_rate",
            "pair_id": pair,
            "prompt": (
                f"A customer paid {zig} ZiG. Convert it to USD, but no ZiG per USD "
                f"exchange rate is provided. What amount in USD should be recorded?"
            ), "expected_value": None, "needs_clarification": True,
        })
        cases.append({
            "id": f"fx_given_{i:02d}", "family": "explicit_exchange_rate",
            "pair_id": pair,
            "prompt": (
                f"A customer paid {zig} ZiG. Convert it to USD using the explicitly "
                f"provided rate of {rate} ZiG per USD. What amount in USD should be recorded?"
            ), "expected_value": money(zig / rate), "needs_clarification": False,
        })

        a = Decimal(11 + i)
        b = Decimal(20 + i * 2)
        cases.append({
            "id": f"receipt_{i:02d}", "family": "deduplicate_payments",
            "prompt": (
                f"Payment records show receipt A USD {a}, receipt B USD {b}, "
                f"and receipt A USD {a} again (duplicate). "
                f"What is the sum of distinct receipts?"
            ), "expected_value": money(a + b), "needs_clarification": False,
        })

        principal = Decimal(100 + i * 20)
        rate_pct = Decimal(4 + i % 6)
        months = 3 + i % 9
        interest = principal * rate_pct * Decimal(months) / Decimal(1200)
        cases.append({
            "id": f"interest_{i:02d}", "family": "simple_interest",
            "prompt": (
                f"For principal USD {principal}, calculate SIMPLE interest only "
                f"at {rate_pct}% per annum for {months} months. "
                f"Assume no compounding."
            ), "expected_value": money(interest), "needs_clarification": False,
        })
    assert len(cases) == 100
    ids = [x["id"] for x in cases]
    assert len(ids) == len(set(ids))
    return cases


def score(cases: list[dict], predictions: list[dict]) -> dict:
    by_id = {}
    for prediction in predictions:
        if not isinstance(prediction, dict) or not isinstance(prediction.get("id"), str):
            raise ValueError("Every prediction requires a string id")
        if prediction["id"] in by_id:
            raise ValueError("Duplicate prediction id")
        by_id[prediction["id"]] = prediction

    expected_ids = {case["id"] for case in cases}
    if set(by_id) != expected_ids:
        raise ValueError("Missing or extra prediction IDs: require exactly one per dev case")

    successes = {}
    family_results = defaultdict(lambda: [0, 0])
    true_missing = 0
    predicted_missing = 0
    true_missing_predicted = 0
    for case in cases:
        item = by_id[case["id"]]
        wants_clarification = case["needs_clarification"]
        claimed_missing = item.get("needs_clarification") is True
        if wants_clarification:
            true_missing += 1
        if claimed_missing:
            predicted_missing += 1
            if wants_clarification:
                true_missing_predicted += 1

        if wants_clarification:
            correct = claimed_missing and item.get("prediction_value") is None
        elif claimed_missing:
            correct = False
        else:
            try:
                raw_value = item["prediction_value"]
                if isinstance(raw_value, bool) or raw_value is None:
                    correct = False
                else:
                    value = Decimal(str(raw_value))
                    expected = Decimal(case["expected_value"])
                    correct = value.is_finite() and abs(value - expected) <= PENNY
            except (KeyError, InvalidOperation, ValueError):
                correct = False
        successes[case["id"]] = correct
        family_results[case["family"]][0] += int(correct)
        family_results[case["family"]][1] += 1

    pairs = defaultdict(list)
    for case in cases:
        if "pair_id" in case:
            pairs[case["pair_id"]].append(successes[case["id"]])
    if not all(len(values) == 2 for values in pairs.values()):
        raise ValueError("Each contrast pair must have exactly two cases")

    return {
        "n": len(cases),
        "correct": sum(successes.values()),
        "accuracy": round(sum(successes.values()) / len(cases), 4),
        "abstention_precision": (
            round(true_missing_predicted / predicted_missing, 4)
            if predicted_missing else None
        ),
        "abstention_recall": round(true_missing_predicted / true_missing, 4),
        "contrast_pairs": len(pairs),
        "both_correct_pairs": sum(all(v) for v in pairs.values()),
        "per_family": {k: {"correct": v[0], "total": v[1]}
                       for k, v in sorted(family_results.items())},
    }


def self_test() -> None:
    cases = build_cases()
    oracle = [
        {"id": case["id"], "prediction_value": case["expected_value"],
         "needs_clarification": case["needs_clarification"]}
        for case in cases
    ]
    full = score(cases, oracle)
    assert full["correct"] == 100 and full["both_correct_pairs"] == 20
    wrong = [dict(x) for x in oracle]
    wrong[0]["prediction_value"] = "999999.99"
    failed = score(cases, wrong)
    assert failed["correct"] == 99
    wrong2 = [dict(x) for x in oracle]
    missing_idx = next(i for i, x in enumerate(cases) if x["needs_clarification"])
    wrong2[missing_idx]["needs_clarification"] = False
    wrong2[missing_idx]["prediction_value"] = "0"
    assert score(cases, wrong2)["correct"] == 99
    print("Self-test passed: 100 dev cases, 20 controlled FX contrast pairs,")
    print("correct oracle accepted and incorrect/unsafe outputs rejected.")
    print("WARNING: no AI model was evaluated.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="write public development-only JSONL")
    parser.add_argument("--predictions", type=Path, help="JSONL prediction file to score")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    cases = build_cases()
    if args.self_test:
        self_test()
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(
            "".join(json.dumps(item, sort_keys=True) + "\n" for item in cases),
            encoding="utf-8",
        )
        print("Development cases written:", len(cases))
    if args.predictions:
        predictions = [
            json.loads(line) for line in
            args.predictions.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        print(json.dumps(score(cases, predictions), sort_keys=True, indent=2))
    if not (args.self_test or args.write or args.predictions):
        parser.print_help()


if __name__ == "__main__":
    main()
