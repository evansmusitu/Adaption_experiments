"""Strictly manual, idempotent, cost-quoted Adaption PROOFBENCH pilot.

No automatic triggers. A quote may persist dataset column mappings, but
only a specifically approved, within-ceiling request may start adaptation.
Provider response errors are deliberately suppressed from public logs.
"""
from __future__ import annotations

import json
import math
import os
import sys

from .adaption_config import MAX_ROWS, pilot_config

APPROVAL_PHRASE = "I APPROVE UP TO 10 ADAPTION CREDITS"
CREDIT_CEILING = 10.0


def launch_pilot(dataset_id, api_key, approval, git_ref, client_factory=None):
    if approval != APPROVAL_PHRASE:
        raise PermissionError("Exact owner approval missing")
    if git_ref != "refs/heads/main":
        raise PermissionError("Adaptation may only be dispatched on main")
    if not isinstance(api_key, str) or not api_key.strip():
        raise PermissionError("Adaption API key is missing")
    config = pilot_config(dataset_id)
    if client_factory is None:
        from adaption import Adaption
        client_factory = Adaption

    client = client_factory(api_key=api_key)
    quote = client.datasets.adapt(dataset_id, estimate=True, **config)
    if getattr(quote, "estimate", None) is not True or getattr(quote, "run_id", None) is not None:
        raise RuntimeError("Adaption did not confirm estimate-only response")
    credits = getattr(quote, "estimated_credits_consumed", None)
    if type(credits) not in (int, float) or not math.isfinite(credits) or credits < 0 or credits > CREDIT_CEILING:
        raise ValueError("Quote unavailable or exceeds 10-credit ceiling")

    # Exactly one provider call to start work; fixed idempotency key prevents
    # duplicate cost on an accidental repeat if supported by the provider.
    run = client.datasets.adapt(dataset_id, **config)
    run_id = getattr(run, "run_id", None)
    if not isinstance(run_id, str) or not run_id:
        raise RuntimeError("Launch outcome uncertain. Inspect Adaption; never auto-retry.")
    return {
        "dataset_id": dataset_id,
        "run_id": run_id,
        "max_rows": MAX_ROWS,
        "quoted_credits": round(float(credits), 3),
        "credit_ceiling": CREDIT_CEILING,
        "approval_received": True,
    }


def main():
    try:
        result = launch_pilot(
            os.getenv("PROOFBENCH_DATASET_ID", ""),
            os.getenv("ADAPTION_API_KEY", ""),
            os.getenv("PROOFBENCH_CREDIT_APPROVAL", ""),
            os.getenv("GITHUB_REF", ""),
        )
    except (PermissionError, ValueError):
        print("DENIED: missing approval, invalid dataset ID or unacceptable credit quote.")
        return 2
    except Exception:
        print("FAILED OR UNCERTAIN: inspect Adaption account before any re-dispatch.")
        return 1
    print(json.dumps(result, sort_keys=True))
    print("Pilot submitted once. This is not proof of completed adaptation or improvement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
