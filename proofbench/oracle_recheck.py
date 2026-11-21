"""Independent, offline Decimal recheck of all PROOFBENCH training answer keys.

This deliberately does NOT import benchmark.py or its solution generator.
It verifies source fixture arithmetic/abstention, NOT AI model accuracy or
quality of Adaption's enhanced completions.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import re

AMOUNT = r"(\d+(?:\.\d+)?)"
CENT = Decimal("0.01")


def _capture(pattern: str, text: str, case: int):
    found = re.search(pattern, text, re.I | re.S)
    if not found:
        raise ValueError(f"case {case}: missing or ambiguous source figures")
    return found.groups()


def _expected(prompt: str, case: int):
    if "Opening stock is" in prompt:
        a, b, sold = map(int, _capture(
            r"Opening stock is (\d+) units; deliveries add (\d+) units.*?Recorded sales were (\d+)", prompt, case
        ))
        remainder = a + b - sold
        return ("inventory", None if remainder < 0 else Decimal(remainder), "negative stock" if remainder < 0 else None)
    if "A kiosk sells" in prompt:
        n, sell, fee = _capture(
            rf"A kiosk sells (\d+) products for USD {AMOUNT} each\. A processing charge of USD {AMOUNT}", prompt, case
        )
        if "The charge applies to EACH item" in prompt:
            value = Decimal(n) * (Decimal(sell) - Decimal(fee))
        elif "ONE flat charge for the entire sale" in prompt:
            value = Decimal(n) * Decimal(sell) - Decimal(fee)
        else:
            raise ValueError(f"case {case}: fee rule unspecified")
        return ("fees", value.quantize(CENT, ROUND_HALF_UP), None)
    if "Cash opened at" in prompt:
        start, receipt, payment = map(int, _capture(
            r"Cash opened at USD (\d+); two entries show USD (\d+) each; one payment is USD (\d+)", prompt, case
        ))
        if "SAME transaction ID" in prompt:
            count = 1
        elif "DISTINCT transaction IDs" in prompt:
            count = 2
        else:
            raise ValueError(f"case {case}: receipt reconciliation rule unspecified")
        return ("cash", Decimal(start + receipt * count - payment), None)
    if "The shop received ZiG" in prompt:
        amount = Decimal(_capture(rf"The shop received ZiG {AMOUNT}", prompt, case)[0])
        if "No exchange rate, source or date" in prompt:
            return ("fx", None, "exchange rate")
        rate = Decimal(_capture(rf"Use a hypothetical rate of {AMOUNT} ZiG for 1 USD", prompt, case)[0])
        if rate <= 0:
            raise ValueError(f"case {case}: invalid exchange rate")
        return ("fx", (amount / rate).quantize(CENT, ROUND_HALF_UP), None)
    if "A trader sells" in prompt:
        n, sell, cost = _capture(
            rf"A trader sells (\d+) units at USD {AMOUNT} each and pays USD {AMOUNT} per unit", prompt, case
        )
        if "Delivery cost has not been recorded or estimated" in prompt:
            return ("profit", None, "delivery cost")
        delivery = Decimal(_capture(rf"Total delivery cost was USD {AMOUNT}", prompt, case)[0])
        return ("profit", ((Decimal(sell) - Decimal(cost)) * int(n) - delivery).quantize(CENT, ROUND_HALF_UP), None)
    if "A deposit of" in prompt:
        amount, percentage = _capture(rf"A deposit of USD {AMOUNT} earns (\d+)%", prompt, case)
        principal, rate = Decimal(amount), Decimal(percentage) / Decimal(100)
        if "Apply SIMPLE interest" in prompt:
            total = principal * (1 + rate * 2)
        elif "Apply ANNUAL COMPOUND interest" in prompt:
            total = principal * (1 + rate) ** 2
        else:
            raise ValueError(f"case {case}: unspecified interest method")
        return ("interest", total.quantize(CENT, ROUND_HALF_UP), None)
    raise ValueError(f"case {case}: unexpected financial scenario family")


def verify_train(path) -> dict:
    target = Path(path)
    content = target.read_bytes()
    if not content or len(content) > 2_000_000:
        raise ValueError("Invalid or oversized training source file")
    try:
        rows = [json.loads(line) for line in content.splitlines() if line.strip()]
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid training JSONL") from exc
    if len(rows) != 240:
        raise ValueError("Expected exactly 240 training source cases")
    if any(
        not isinstance(row, dict) or set(row) != {"prompt", "completion"}
        or not isinstance(row["prompt"], str) or not row["prompt"].strip()
        or not isinstance(row["completion"], str) or not row["completion"].strip()
        for row in rows
    ):
        raise ValueError("Invalid training columns or row schema")
    if len({row["prompt"] for row in rows}) != len(rows):
        raise ValueError("Source contains duplicate prompts")

    families = Counter()
    numeric, clarification = 0, 0
    for i, row in enumerate(rows):
        family, expected, missing = _expected(row["prompt"], i)
        families[family] += 1
        completion = row["completion"]
        if expected is None:
            if not completion.startswith("Insufficient information.") or missing not in completion.lower():
                raise ValueError(f"case {i}: missing-information/clarification mismatch")
            clarification += 1
        else:
            amount = re.fullmatch(
                r"Result: (\d+(?:\.\d+)?) (?:USD|units)\. .+", completion, re.S
            )
            if not amount or Decimal(amount.group(1)) != expected:
                raise ValueError(f"case {i}: arithmetic result amount mismatch")
            if (" units." if family == "inventory" else " USD.") not in completion:
                raise ValueError(f"case {i}: numeric result unit mismatch")
            numeric += 1
    if len(families) != 6 or set(families.values()) != {40}:
        raise ValueError("Unexpected scenario-family coverage")
    return {
        "checked": len(rows),
        "verified": len(rows),
        "families": dict(sorted(families.items())),
        "numeric_cases": numeric,
        "clarification_cases": clarification,
        "method": "Independent Decimal arithmetic and strict missing-data rules",
        "establishes_model_accuracy": False,
        "authenticates_provider_output": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True)
    args = parser.parse_args()
    try:
        result = verify_train(args.train)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    print(json.dumps({"ok": True, **result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
