"""Independent prompt-text arithmetic audit for PROOFBENCH research fixtures.

This deliberately parses *question text* and derives its own arithmetic;
it does not import the generator's `_scenario`, `money`, or `_correct`.
It is a cross-check against accidentally wrong generated labels, not a
substitute for human blind evaluation or evidence of model quality.
"""
from __future__ import annotations

from collections import Counter
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re


def _extract(text: str, pattern: str) -> tuple[Decimal, ...]:
    found = re.search(pattern, text, flags=re.IGNORECASE)
    if found is None:
        raise ValueError("Prompt parser failed for a required numerical field")
    return tuple(Decimal(value) for value in found.groups())


def _expected(row: dict) -> tuple[str, str | None, str]:
    text = row["prompt"]
    family = row["family"]
    d = Decimal
    if family == "fx_missing":
        (amount,) = _extract(text, r"received ZiG (\d+)")
        unit = "USD"
        if "No exchange rate" in text:
            return "clarify", None, unit
        (rate,) = _extract(text, r"rate of (\d+(?:\.\d+)?) ZiG")
        expected = amount / rate
    elif family == "inventory_conflict":
        opening, delivered = _extract(text, r"Opening stock is (\d+) units; deliveries add (\d+)")
        (sold,) = _extract(text, r"Recorded sales were (\d+) units")
        unit = "units"
        if sold > opening + delivered:
            return "clarify", None, unit
        expected = opening + delivered - sold
    elif family == "receipt_identity":
        opening, receipt, payment = _extract(
            text,
            r"Cash opened at USD (\d+); two entries show USD (\d+) each; one payment is USD (\d+)"
        )
        unit = "USD"
        expected = opening + receipt * (2 if "DISTINCT transaction" in text else 1) - payment
    elif family == "interest_method":
        principal, rate = _extract(text, r"deposit of USD (\d+) earns (\d+)%")
        unit = "USD"
        expected = principal * (
            1 + rate * 2 / 100 if "SIMPLE interest" in text else (1 + rate / 100) ** 2
        )
    elif family == "profit_overhead":
        qty, price, cost = _extract(
            text, r"sells (\d+) units at USD (\d+(?:\.\d+)?) each and pays USD (\d+(?:\.\d+)?)"
        )
        unit = "USD"
        if "delivery cost has not" in text.lower():
            return "clarify", None, unit
        (overhead,) = _extract(text, r"delivery cost was USD (\d+(?:\.\d+)?)")
        expected = qty * (price - cost) - overhead
    elif family == "fee_basis":
        qty, price, fee = _extract(
            text,
            r"sells (\d+) products for USD (\d+(?:\.\d+)?) each\. "
            r"A processing charge of USD (\d+(?:\.\d+)?)"
        )
        unit = "USD"
        expected = qty * (price - fee) if "EACH item" in text else qty * price - fee
    else:
        raise ValueError("Unknown financial scenario family")
    if not expected.is_finite():
        raise ValueError("Non-finite audit computation")
    if unit == "USD":
        expected = expected.quantize(d("0.01"), rounding=ROUND_HALF_UP)
    return "numeric", str(expected), unit


def verify_case(row: dict) -> bool:
    try:
        kind, value, unit = _expected(row)
        label = row["gold"]
        if label["kind"] != kind or label["unit"] != unit:
            return False
        if kind == "clarify":
            return label["value"] is None
        got = Decimal(str(label["value"]))
        return got.is_finite() and got == Decimal(value)
    except (KeyError, ValueError, TypeError, InvalidOperation, ZeroDivisionError):
        return False


def audit_cases(rows: list[dict]) -> dict:
    failures = []
    families = set()
    for row in rows:
        families.add(row.get("family"))
        if not verify_case(row):
            failures.append(str(row.get("id", "unknown"))[:100])
    return {
        "checked": len(rows),
        "failures": len(failures),
        "families_checked": len(families),
        "failed_case_ids": failures[:20],
        "assurance": "Independent numerical-oracle cross-check, NOT model accuracy or human review.",
    }
