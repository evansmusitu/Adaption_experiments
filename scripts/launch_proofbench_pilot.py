#!/usr/bin/env python3
"""Manually approved 100-row PROOFBENCH pilot; no automatic invocation.

Reads ADAPTION_API_KEY from GitHub Secrets. First obtains Adaption's official
estimate, and aborts unless the quote is within the 10-credit planning ceiling
and the account has enough credits. The actual invention uses a fixed
idempotency key to prevent accidental duplicate charges on retries.

Provider charges may differ from estimates. Review the quote before approval.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

URL = "https://api.prod.adaptionlabs.ai/api/v1/datasets/invent"
EXPECTED_APPROVAL = "I APPROVE 10 ADAPTION CREDITS"
NAME = "MUSITU PROOFBENCH - 100-row verification pilot 2026"
IDEMPOTENCY = "musitu-proofbench-2026-11-20-100-row-v1"
PROMPT = (
    "Create an original supervised fine-tuning dataset on mathematically "
    "verifiable financial reasoning for Zimbabwean small businesses. "
    "Use entirely fictional scenarios and amounts. Cover cash-flow, "
    "inventory, profit, duplicate payments, interest, reconciliation, "
    "missing currency exchange rates, and inconsistent constraints. "
    "Require explicit assumptions, traceable arithmetic, consistent units, "
    "and requests for missing input instead of invented facts. "
    "Use varied counterfactual situations and realistic short user questions."
)
QUOTE_MAX_CREDITS = 10.0


def api_post(key: str, payload: dict) -> dict:
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "musitu-proofbench-pilot/1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = response.read(200001)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("API HTTP status " + str(exc.code)) from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("API network error; do not auto-retry") from None
    if len(data) > 200000:
        raise RuntimeError("API response too large")
    try:
        result = json.loads(data)
    except (UnicodeDecodeError, ValueError):
        raise RuntimeError("Invalid API JSON") from None
    if not isinstance(result, dict):
        raise RuntimeError("Invalid API response structure")
    return result


def strictly_nonnegative_number(value):
    return type(value) in (int, float) and 0 <= value < 1_000_000


def main() -> int:
    if os.getenv("PILOT_APPROVAL", "") != EXPECTED_APPROVAL:
        print("STOP: Explicit manual 10-credit approval not supplied.")
        return 2
    if os.getenv("GITHUB_REF") != "refs/heads/main":
        print("STOP: Workflow must be dispatched on main.")
        return 2
    key = os.getenv("ADAPTION_API_KEY", "").strip()
    if not key:
        print("STOP: GitHub secret ADAPTION_API_KEY unavailable.")
        return 2

    base = {
        "rows": 100,
        "dataset_prompt": PROMPT,
        "name": NAME,
        "training_type": "instruction_dataset",
        "idempotency_key": IDEMPOTENCY,
    }
    try:
        quote = api_post(key, {**base, "estimate": True})
    except RuntimeError as exc:
        print("Quote failed:", str(exc))
        return 1
    est = quote.get("estimatedCredits", quote.get("estimated_credits"))
    available = quote.get("availableCredits", quote.get("available_credits"))
    if not strictly_nonnegative_number(est) or est > QUOTE_MAX_CREDITS:
        print("STOP: Missing or over-budget estimate.")
        return 1
    if not strictly_nonnegative_number(available) or available < est:
        print("STOP: Promotional credits insufficient or unknown.")
        return 1
    print("Adaption estimated credits:", est, "; permitted quote ceiling:", QUOTE_MAX_CREDITS)
    # One launch request only, with fixed idempotency; no automatic retries.
    try:
        response = api_post(key, base)
    except RuntimeError as exc:
        print("Launch outcome uncertain:", str(exc))
        print("Do not dispatch again without checking the Adaption dataset list.")
        return 1
    dataset_id = response.get("dataset_id", response.get("id"))
    status = response.get("status")
    if isinstance(dataset_id, str) and len(dataset_id) <= 128:
        print("New PROOFBENCH pilot dataset ID:", dataset_id)
    else:
        print("API response did not include a recognizable dataset ID.")
        return 1
    if status in ("running", "pending", "succeeded", "failed", "awaiting_input"):
        print("Dataset creation status:", status)
    print("Pilot submitted once. Further work should inspect this same dataset ID.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
