#!/usr/bin/env python3
"""No-charge, estimate-only Adaption pilot. Do NOT launch an adaptation.

Only one fixed, existing dataset is quoted. This sends estimate=true and never
submits any request that could start a training/adaptation run. Some Adaption
estimate requests can persist submitted column mappings/expansion settings; we
intentionally submit neither to preserve the dataset's existing configuration.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

HOST = "https://api.prod.adaptionlabs.ai"
DATASET_ID = "5ef42194-6814-45fb-8841-8116482928fa"
PILOT_ROWS = 100


def main() -> int:
    token = os.environ.get("ADAPTION_API_KEY", "").strip()
    if not token:
        print("ERROR: GitHub secret ADAPTION_API_KEY is absent")
        return 2
    payload = {
        "estimate": True,
        "column_mapping": {"prompt": "enhanced_prompt", "completion": "enhanced_completion"},
        "job_specification": {"max_rows": PILOT_ROWS},
    }
    request = urllib.request.Request(
        HOST + "/api/v1/datasets/" + DATASET_ID + "/adapt",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "musitu-adaption-estimate-only/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            raw = response.read(100_001)
    except urllib.error.HTTPError as exc:
        print(f"Adaption estimate request rejected: HTTP {exc.code}. No adaptation was requested.")
        return 1
    except (urllib.error.URLError, TimeoutError):
        print("Adaption estimate network connection failed")
        return 1
    if len(raw) > 100_000:
        print("Estimate response exceeded bounded limit")
        return 1
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        print("Estimate response was not valid JSON")
        return 1
    if not isinstance(result, dict):
        print("Estimate response has invalid shape")
        return 1
    if result.get("estimate") is not True or result.get("run_id"):
        print("WARNING: API did not explicitly confirm estimate-only behavior")
        return 1

    credits = result.get("estimatedCreditsConsumed")
    minutes = result.get("estimatedMinutes")
    if (type(credits) not in (int, float) or credits < 0
            or type(minutes) not in (int, float) or minutes < 0):
        print("Estimate response lacks valid credit/time figures")
        return 1
    print("CONFIRMED: Adaption returned estimate=true; no run ID.")
    print(f"Pilot size: {PILOT_ROWS} rows from existing 2,000-row dataset.")
    print(f"Estimated credits: {credits:g}")
    print(f"Estimated minutes: {minutes:g}")
    print("Multimodal pricing applied:", result.get("multimodalPricingApplied") is True)
    print("No adaptation or training job was started by this script.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
