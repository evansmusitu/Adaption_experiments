"""MUSITU PROOFBENCH: reproducible, oracle-backed adversarial finance tasks.

This produces *synthetic research fixtures*, not certified financial advice,
human-reviewed ground truth, or evidence of model improvement. Training exports
contain only (prompt, completion); evaluation fixtures retain separate oracles.
All generation is offline and deterministic. Requires Python 3.10+ only.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import random

FAMILIES = (
    "fx_missing", "inventory_conflict", "receipt_identity",
    "interest_method", "profit_overhead", "fee_basis",
)
SPLITS = ("train", "dev", "stress")
FRAMINGS = {
    "train": ("A fictional Zimbabwean business records:", "Work out the answer."),
    "dev": ("An auditor inspects a fictional business statement:", "What follows from the records?"),
    "stress": ("A reviewer challenges the fictional ledger below:", "Give a justified conclusion."),
}
CENT = Decimal("0.01")


def money(value) -> str:
    return str(Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP))


def _scenario(family: str, split: str, index: int, seed: int) -> tuple[dict, dict]:
    """Return paired (variant A, variant B) records from one underlying scenario."""
    digest = hashlib.sha256(f"{seed}:{split}:{family}:{index}".encode()).hexdigest()
    rng = random.Random(int(digest[:16], 16))
    stem, closing = FRAMINGS[split]
    number = lambda low, high: Decimal(rng.randint(low, high)) / 100
    symbol = f"{split}-{family}-{index:04d}"
    pair_id = symbol
    def case(variant, rule, question, value, unit, explanation, *, clarify=False):
        prompt = f"{stem}\n{question}\nCondition: {rule}\n{closing}"
        kind = "clarify" if clarify else "numeric"
        completion = (
            "Insufficient information. " + explanation
            if clarify else f"Result: {value} {unit}. " + explanation
        )
        return {
            "id": f"{symbol}-{variant}", "pair_id": pair_id,
            "scenario_id": symbol, "template_id": f"{family}:{split}:v1",
            "split": split, "variant": variant, "family": family,
            "prompt": prompt, "completion": completion,
            "gold": {"kind": kind, "value": None if clarify else str(value), "unit": unit},
            "provenance": {
                "source": "deterministic_synthetic", "license": "CC0-1.0",
                "reviewed_by_human": False, "model_generated": False,
            },
        }

    if family == "fx_missing":
        zig = rng.randint(200, 7000)
        rate = number(1500, 3500)
        q = f"The shop received ZiG {zig}. Convert it to US dollars to two decimals."
        a = case("a", f"Use a hypothetical rate of {rate} ZiG for 1 USD.", q,
                 money(Decimal(zig) / rate), "USD", "Divide ZiG by the supplied ZiG/USD rate.")
        b = case("b", "No exchange rate, source or date is available.", q, None,
                 "USD", "A dated, sourced ZiG/USD exchange rate must be provided.", clarify=True)
    elif family == "inventory_conflict":
        opening, delivered = rng.randint(12, 70), rng.randint(6, 40)
        sold = rng.randint(1, opening)
        q = f"Opening stock is {opening} units; deliveries add {delivered} units. What stock remains?"
        a = case("a", f"Recorded sales were {sold} units.", q,
                 opening + delivered - sold, "units", "Opening plus deliveries minus sales.")
        b = case("b", f"Recorded sales were {opening + delivered + rng.randint(1, 20)} units.", q,
                 None, "units", "These records imply negative stock; reconcile movements first.", clarify=True)
    elif family == "receipt_identity":
        opening = rng.randint(100, 1000)
        receipt, payment = rng.randint(20, 200), rng.randint(5, 80)
        q = (f"Cash opened at USD {opening}; two entries show USD {receipt} each; "
             f"one payment is USD {payment}. Determine the closing cash balance.")
        a = case("a", "The receipt entries have DISTINCT transaction IDs R1 and R2.", q,
                 money(opening + receipt * 2 - payment), "USD",
                 "Two different receipts count twice.")
        b = case("b", "Both receipt entries have the SAME transaction ID R1.", q,
                 money(opening + receipt - payment), "USD",
                 "One receipt duplicated in a report counts once.")
    elif family == "interest_method":
        principal = rng.randint(200, 3000)
        rate = rng.choice([5, 8, 10, 12])
        q = (f"A deposit of USD {principal} earns {rate}% per annum for exactly "
             "two years with no fees. What is the end balance?")
        a_value = Decimal(principal) * (1 + Decimal(rate) * 2 / 100)
        b_value = Decimal(principal) * (1 + Decimal(rate) / 100) ** 2
        a = case("a", "Apply SIMPLE interest.", q, money(a_value), "USD",
                 "Principal times (1 + annual rate times years).")
        b = case("b", "Apply ANNUAL COMPOUND interest.", q, money(b_value), "USD",
                 "Principal times (1 + annual rate) squared.")
    elif family == "profit_overhead":
        quantity = rng.randint(4, 60)
        price, cost, overhead = number(500, 3000), number(100, 450), number(300, 2500)
        q = (f"A trader sells {quantity} units at USD {price} each and pays "
             f"USD {cost} per unit to purchase them. Calculate profit after delivery.")
        profit = (price - cost) * quantity - overhead
        a = case("a", f"Total delivery cost was USD {overhead}.", q,
                 money(profit), "USD", "Sales minus stock purchases minus delivery.")
        b = case("b", "Delivery cost has not been recorded or estimated.", q,
                 None, "USD", "Profit after delivery requires the delivery cost.", clarify=True)
    elif family == "fee_basis":
        quantity = rng.randint(3, 35)
        price, fee = number(500, 2500), number(40, 260)
        q = (f"A kiosk sells {quantity} products for USD {price} each. "
             f"A processing charge of USD {fee} is assessed. "
             "What is net cash from sales after the charge?")
        a = case("a", "The charge applies to EACH item sold.", q,
                 money(quantity * (price - fee)), "USD",
                 "Subtract one charge per item.")
        b = case("b", "The charge is ONE flat charge for the entire sale.", q,
                 money(quantity * price - fee), "USD",
                 "Subtract the single fee once.")
    else:
        raise ValueError("Unknown task family: " + family)
    if a["gold"] == b["gold"]:
        raise AssertionError("Counterfactual pair must change the correct response")
    return a, b


def make_cases(split: str, pairs_per_family: int = 10, seed: int = 20261120) -> list[dict]:
    if split not in SPLITS:
        raise ValueError("Split must be train, dev or stress")
    if not isinstance(pairs_per_family, int) or not 1 <= pairs_per_family <= 1000:
        raise ValueError("pairs_per_family must be 1..1000")
    rows = []
    for family in FAMILIES:
        for index in range(pairs_per_family):
            rows.extend(_scenario(family, split, index, seed))
    return rows


def validate_splits(parts: dict[str, list[dict]]) -> None:
    all_ids = set()
    all_scenarios = {}
    all_templates = {}
    all_prompts = set()
    for split, rows in parts.items():
        if split not in SPLITS:
            raise ValueError("Unexpected split")
        groups = defaultdict(list)
        for row in rows:
            if row["split"] != split or row["id"] in all_ids or row["prompt"] in all_prompts:
                raise ValueError("Split mismatch, duplicate ID or repeated prompt")
            all_ids.add(row["id"])
            all_prompts.add(row["prompt"])
            for field, owner in (("scenario_id", all_scenarios), ("template_id", all_templates)):
                value = row[field]
                if value in owner and owner[value] != split:
                    raise ValueError(f"Cross-split {field} leakage")
                owner[value] = split
            groups[row["pair_id"]].append(row)
        for pair in groups.values():
            if len(pair) != 2 or {r["variant"] for r in pair} != {"a", "b"}:
                raise ValueError("Broken counterfactual pair")
            if pair[0]["gold"] == pair[1]["gold"]:
                raise ValueError("Counterfactual did not change the oracle")


def _correct(expected: dict, predicted: dict | None) -> bool:
    if not isinstance(predicted, dict) or predicted.get("kind") != expected["kind"]:
        return False
    if expected["kind"] == "clarify":
        return predicted.get("value") is None
    if predicted.get("unit") != expected["unit"]:
        return False
    value = predicted.get("value")
    if value is None or isinstance(value, bool):
        return False
    try:
        actual, reference = Decimal(str(value)), Decimal(expected["value"])
        return actual.is_finite() and abs(actual - reference) <= Decimal("0.005")
    except (InvalidOperation, ValueError, TypeError):
        return False


def score_predictions(cases: list[dict], predictions: list[dict]) -> dict:
    gold = {row["id"]: row for row in cases}
    if len(gold) != len(cases):
        raise ValueError("Duplicate case ID")
    by_id = {}
    for pred in predictions:
        if not isinstance(pred, dict) or "id" not in pred:
            raise ValueError("Malformed prediction")
        if pred["id"] in by_id:
            raise ValueError("Duplicate prediction ID")
        if pred["id"] not in gold:
            raise ValueError("Unknown prediction ID")
        by_id[pred["id"]] = pred
    by_family = defaultdict(lambda: [0, 0])
    pairs = defaultdict(list)
    correct = 0
    correct_numeric = 0
    numeric_total = 0
    correct_clarify = 0
    clarify_total = 0
    for row in cases:
        ok = _correct(row["gold"], by_id.get(row["id"]))
        correct += int(ok)
        by_family[row["family"]][0] += int(ok)
        by_family[row["family"]][1] += 1
        pairs[row["pair_id"]].append(ok)
        if row["gold"]["kind"] == "numeric":
            numeric_total += 1
            correct_numeric += int(ok)
        else:
            clarify_total += 1
            correct_clarify += int(ok)
    pairs_passed = sum(len(v) == 2 and all(v) for v in pairs.values())
    total = len(cases)
    return {
        "total": total, "correct": correct,
        "accuracy": round(correct / total, 6) if total else 0,
        "pairs_total": len(pairs), "pairs_both_correct": pairs_passed,
        "strict_pair_accuracy": round(pairs_passed / len(pairs), 6) if pairs else 0,
        "numeric_accuracy": round(correct_numeric / numeric_total, 6) if numeric_total else None,
        "clarification_accuracy": round(correct_clarify / clarify_total, 6) if clarify_total else None,
        "missing_predictions": total - len(by_id),
        "by_family": {
            family: {"correct": counts[0], "total": counts[1]}
            for family, counts in sorted(by_family.items())
        },
        "disclaimer": "Scores supplied external predictions; not Adaption quality scores or model-training evidence.",
    }


def write_release(output_dir, *, seed: int = 20261120) -> dict:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    splits = {
        "train": make_cases("train", 20, seed),
        "dev": make_cases("dev", 10, seed),
        "stress": make_cases("stress", 8, seed),
    }
    validate_splits(splits)
    digests = {}
    for split, rows in splits.items():
        records = (
            [{"prompt": r["prompt"], "completion": r["completion"]} for r in rows]
            if split == "train" else rows
        )
        body = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)
        name = split + ".jsonl"
        (target / name).write_text(body, encoding="utf-8")
        digests[name] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    manifest = {
        "version": "proofbench-paired-v1",
        "seed": seed, "counts": {k: len(v) for k, v in splits.items()},
        "families": list(FAMILIES), "sha256": digests,
        "license": "CC0-1.0",
        "data_origin": "deterministic fictional templates, not a model-generated dataset",
        "review_status": "NOT human-reviewed, NOT an independent blind benchmark",
        "measurement_status": "No model predictions or measured generalization improvement",
        "train_columns": ["prompt", "completion"],
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def _read_jsonl(path):
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="generated")
    parser.add_argument("--predictions", help="External JSONL with id,kind,value,unit")
    parser.add_argument("--cases", help="Dev/stress JSONL with gold answers")
    args = parser.parse_args()
    if args.predictions:
        if not args.cases:
            parser.error("--cases required when scoring predictions")
        print(json.dumps(score_predictions(_read_jsonl(args.cases), _read_jsonl(args.predictions)),
                         indent=2, sort_keys=True))
    else:
        print(json.dumps(write_release(args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
