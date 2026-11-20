"""Estimate-only quote for a newly uploaded PROOFBENCH dataset.

IMPORTANT: Provider estimate=True may persist the submitted column mapping
on the dataset. It does not start adaptation or reserve credit. Never call
this module for a launch or on a pull_request event.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
import uuid

_EXISTING_INVENT_DATASETS = {
    "61d434c2-b617-45b0-82f5-44771db25498",
    "b17502e7-d482-4a5d-bae0-a9ea55b7bfe1",
    "5ef42194-6814-45fb-8841-8116482928fa",
}


def estimate(dataset_id: str, token: str, client_factory=None) -> dict:
    if not isinstance(dataset_id, str) or not re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        dataset_id,
    ):
        raise ValueError("Use the ID of the new PROOFBENCH dataset, not a URL")
    if dataset_id in _EXISTING_INVENT_DATASETS:
        raise ValueError("Existing invented datasets are not valid PROOFBENCH source IDs")
    if not isinstance(token, str) or not token.strip():
        raise PermissionError("ADAPTION_API_KEY not available")
    if client_factory is None:
        from adaption import Adaption
        client_factory = Adaption
    client = client_factory(api_key=token)
    result = client.datasets.adapt(
        dataset_id,
        estimate=True,
        column_mapping={"prompt": "prompt", "completion": "completion"},
        job_specification={"max_rows": 100},
        training_type="instruction_dataset",
    )
    if result.estimate is not True or result.run_id is not None:
        raise RuntimeError("API did not prove estimate-only mode; inspect provider state")
    credits = result.estimated_credits_consumed
    minutes = result.estimated_minutes
    if any(type(n) not in (int, float) or not math.isfinite(n) or n < 0
           for n in (credits, minutes)):
        raise ValueError("Missing or non-finite quoted credits or duration")
    return {
        "dataset_id": dataset_id,
        "max_rows": 100,
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
