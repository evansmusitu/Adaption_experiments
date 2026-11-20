"""Estimate-only quote for a newly uploaded PROOFBENCH dataset.

IMPORTANT: Provider estimate=True may persist the submitted column mapping
on the dataset. It does not start adaptation or reserve credit. Never call
this module for a launch or on a pull_request event.
"""
from __future__ import annotations

import json
import math
import os
import sys

from .adaption_config import MAX_ROWS, pilot_config



def estimate(dataset_id: str, token: str, client_factory=None) -> dict:
    config = pilot_config(dataset_id)
    if not isinstance(token, str) or not token.strip():
        raise PermissionError("ADAPTION_API_KEY not available")
    if client_factory is None:
        from adaption import Adaption
        client_factory = Adaption
    client = client_factory(api_key=token)
    result = client.datasets.adapt(dataset_id, estimate=True, **config)
    if result.estimate is not True or result.run_id is not None:
        raise RuntimeError("API did not prove estimate-only mode; inspect provider state")
    credits = result.estimated_credits_consumed
    minutes = result.estimated_minutes
    if any(type(n) not in (int, float) or not math.isfinite(n) or n < 0
           for n in (credits, minutes)):
        raise ValueError("Missing or non-finite quoted credits or duration")
    return {
        "dataset_id": dataset_id,
        "max_rows": MAX_ROWS,
        "estimated_credits": round(credits, 3),
        "estimated_minutes": round(minutes, 3),
        "estimate_only": True,
        "launched": False,
    }


def main():
    dataset_id = os.getenv("PROOFBENCH_DATASET_ID", "")
    key = os.getenv("ADAPTION_API_KEY", "")
    if os.getenv("GITHUB_REF") != "refs/heads/main":
        print("STOP: manual quotation must use main")
        return 2
    try:
        result = estimate(dataset_id, key)
    except (ValueError, PermissionError, RuntimeError):
        print("QUOTE FAILED: ID, credentials or provider estimate invalid. No retry.")
        return 1
    except Exception:
        print("QUOTE UNKNOWN: inspect provider status before another request.")
        return 1
    print(json.dumps(result, sort_keys=True))
    print("This was an estimate only. No credit-consuming job was launched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
