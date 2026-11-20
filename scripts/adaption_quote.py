#!/usr/bin/env python3
"""Estimate an original PROOFBENCH seed run without creating any dataset.

Uses the documented Invent estimate=true API. This workflow does NOT launch
adaptations, training, dataset creation, or any other credit-consuming work.
Never print raw errors or private billing balances into a public GitHub log.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

ROWS = 100
URL = "https://api.prod.adaptionlabs.ai/api/v1/datasets/invent"
PROMPT = (
    "Original instruction-response training examples about verifiable numerical "
    "reasoning for Zimbabwean small-business scenarios. Cover cash-flow, inventory, "
    "profit, duplicate payments, interest, accounting constraints, and missing "
    "currency exchange rates. Require explicit numerical assumptions, correct "
    "calculation, and abstention when essential inputs are missing. Use fictional "
    "businesses and no private customer data."
)


def numeric(value):
    if type(value) in (float, int) and 0 <= value <= 10_000_000:
        return value
    return None


def main() -> int:
    token = os.environ.get("ADAPTION_API_KEY", "").strip()
    if not token:
        print("ERROR: GitHub secret ADAPTION_API_KEY missing")
        return 2
    payload = {
        "rows": ROWS,
        "dataset_prompt": PROMPT,
        "training_type": "instruction_dataset",
        "estimate": True,
    }
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(),
        method="POST", headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "musitu-estimate-only/2.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            body = response.read(100001)
    except urllib.error.HTTPError as exc:
        print(f"Adaption estimate failed with HTTP {exc.code}; no dataset creation requested.")
        return 1
    except (urllib.error.URLError, TimeoutError):
        print("Adaption API network error during estimate")
        return 1
    if len(body) > 100000:
        print("Estimate response unexpectedly large")
        return 1
    try:
        result = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        print("Estimate response invalid JSON")
        return 1
    if not isinstance(result, dict) or result.get("dataset_id") or result.get("run_id"):
        print("API did not provide a safe estimate-only response")
        return 1
    credits = numeric(result.get("estimatedCredits", result.get("estimated_credits")))
    available = numeric(result.get("availableCredits", result.get("available_credits")))
    if credits is None:
        print("Estimate request returned no recognized credit amount")
        return 1
    print("CONFIRMED: Invent estimate-only request returned successfully")
    print(f"Proposed PROOFBENCH pilot rows: {ROWS}")
    print(f"Estimated credits for new dataset: {credits:g}")
    if available is not None:
        print("Available promotional credits cover estimate:", available >= credits)
    else:
        print("Credit balance unavailable from estimate response")
    print("NO DATASET CREATION OR TRAINING REQUESTED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
