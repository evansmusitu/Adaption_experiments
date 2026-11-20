#!/usr/bin/env python3
"""Quote adaptation of existing Dataset 3, without launching it.

Uses the documented estimate=true API. The request may save the supplied
column mapping on the dataset; no credits are reserved and no run is started.
No secrets, row contents or raw API bodies are printed to public Actions logs.
"""
import json
import os
import sys
import urllib.error
import urllib.request

DATASET_ID = "5ef42194-6814-45fb-8841-8116482928fa"
BASE = "https://api.prod.adaptionlabs.ai/api/v1/datasets/"
ROWS = 100

def main():
    key = os.getenv("ADAPTION_API_KEY", "").strip()
    if not key:
        print("ERROR: missing ADAPTION_API_KEY secret")
        return 2
    payload = {
        "estimate": True,
        "training_type": "instruction_dataset",
        "column_mapping": {"prompt": "enhanced_prompt", "completion": "enhanced_completion"},
        "job_specification": {"max_rows": ROWS},
    }
    request = urllib.request.Request(
        BASE + DATASET_ID + "/adapt",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "musitu-existing-dataset-estimate-only/1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            raw = response.read(100_001)
    except urllib.error.HTTPError as exc:
        print("Adaption adaptation quote HTTP status:", exc.code)
        return 1
    except (urllib.error.URLError, TimeoutError):
        print("Adaption adaptation quote network error")
        return 1
    if len(raw) > 100_000:
        print("Unexpectedly large quote response")
        return 1
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        print("Invalid quote response format")
        return 1
    if not isinstance(result, dict) or result.get("estimate") is not True or result.get("run_id"):
        print("UNEXPECTED: API did not explicitly confirm estimate only; do not retry")
        return 1
    credits = result.get("estimatedCreditsConsumed")
    minutes = result.get("estimatedMinutes")
    if type(credits) not in (int, float) or credits < 0:
        print("Quote response lacks valid credit figure")
        return 1
    print("CONFIRMED: estimate-only; no adaptation run requested")
    print("Dataset: 3 (existing 2,000-row finance-heavy dataset)")
    print("Pilot size:", ROWS)
    print("Estimated credits:", round(credits, 3))
    if type(minutes) in (int, float) and 0 <= minutes < 100_000:
        print("Estimated minutes:", round(minutes, 2))
    print("No adaptation job launched. Actual run requires a separate approval gate.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
