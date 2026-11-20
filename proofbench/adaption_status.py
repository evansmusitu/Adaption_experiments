"""Read-only verification of the newly uploaded PROOFBENCH seed.

No adaptation, upload, training or paid operation is called here. Printed
status information contains only a validated dataset UUID, state and row count.
"""
from __future__ import annotations

import json
import os
import sys
from .adaption_config import validate_proofbench_source

EXPECTED_ROWS = 240
STATES = frozenset({"pending", "running", "awaiting_input", "succeeded", "failed"})


def inspect_import(dataset_id: str, token: str, client_factory=None) -> dict:
    validate_proofbench_source(dataset_id)
    if not isinstance(token, str) or not token.strip():
        raise PermissionError("ADAPTION_API_KEY is missing")
    if client_factory is None:
        from adaption import Adaption
        client_factory = Adaption
    client = client_factory(api_key=token)
    result = client.datasets.get_status(dataset_id)
    if getattr(result, "dataset_id", None) != dataset_id:
        raise RuntimeError("Adaption returned mismatched dataset metadata")
    state = getattr(result, "status", None)
    row_count = getattr(result, "row_count", None)
    if state not in STATES:
        raise RuntimeError("Unrecognized Adaption state")
    if row_count is not None and (type(row_count) is not int or row_count < 0):
        raise RuntimeError("Invalid Adaption row count")
    return {
        "dataset_id": dataset_id,
        "status": state,
        "row_count": row_count,
        "ready_for_quote": state == "awaiting_input" and row_count == EXPECTED_ROWS,
    }


def main() -> int:
    if os.getenv("GITHUB_REF") != "refs/heads/main":
        print("ERROR: status audit must run from main")
        return 2
    try:
        report = inspect_import(
            os.getenv("PROOFBENCH_DATASET_ID", ""),
            os.getenv("ADAPTION_API_KEY", ""),
        )
    except Exception:
        print("Read-only import-status check failed. Inspect Adaption account and dataset ID.")
        return 1
    print(json.dumps(report, sort_keys=True))
    if not report["ready_for_quote"]:
        print("NOT READY: do not request an adaptation quote or launch.")
        return 2
    print("READY FOR QUOTE: 240 original rows uploaded and awaiting adaptation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
