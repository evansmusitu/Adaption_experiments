#!/usr/bin/env python3
"""Read-only overlap audit of 3 previously generated Adaption datasets.

Dataset rows and prompts remain in memory; output is aggregate-only. This
script never invokes adaptation, translation, training or a credit charge.
"""
import json
import os
import sys

from adaption_profile import DATASETS, PREFIX, MAX_DOWNLOAD_BYTES, get_bytes

# The GitHub checkout root is added for importing the package.
from proofbench.overlap import analyze


def main() -> int:
    key = os.getenv("ADAPTION_API_KEY", "").strip()
    if not key:
        print("ERROR: ADAPTION_API_KEY not available")
        return 2
    grouped = []
    try:
        for dataset_id in DATASETS:
            raw = get_bytes(
                PREFIX + dataset_id + "/download?fileFormat=jsonl",
                key, MAX_DOWNLOAD_BYTES
            )
            rows = []
            for line in raw.splitlines():
                if line.strip():
                    row = json.loads(line)
                    if not isinstance(row, dict):
                        raise ValueError("Invalid JSONL record shape")
                    # Keep only the field required for in-memory comparisons.
                    rows.append({"enhanced_prompt": row.get("enhanced_prompt")})
            grouped.append(rows)
    except Exception:
        print("ERROR: dataset read or JSONL validation failed; no raw content printed.")
        return 1
    print(json.dumps(analyze(grouped), sort_keys=True))
    print("No adaptation, dataset mutation or paid work was started.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
