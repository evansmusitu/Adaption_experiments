"""Read-only, review-only export of one completed PROOFBENCH Adaption pilot.

NEVER calls adapt, create, upload or any credit-consuming operation.
The output is a GitHub Actions review artifact, not a published/reviewed dataset.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from .benchmark import write_release

DATASET_ID = "eefe77fe-ba8c-4d54-9341-97c327a47fd3"
EXPECTED_ROWS = 100
MAX_BYTES = 8_000_000


def _pick(row: dict, *keys: str) -> str:
    for key in keys:
        val = row.get(key)
        if isinstance(val, str) and val.strip() and val.strip().upper() != "N/A":
            return val
    return ""


def extract_verified_rows(raw: bytes, original_training: Path):
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ValueError("Provider JSONL missing or unexpectedly large")
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    if len(rows) != EXPECTED_ROWS or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Expected exactly 100 provider output records")
    train_rows = [json.loads(line) for line in original_training.read_bytes().splitlines() if line.strip()]
    if len(train_rows) != 240:
        raise ValueError("Source training release has unexpected row count")
    originals = {row["prompt"]: row["completion"] for row in train_rows}
    if len(originals) != 240:
        raise ValueError("Training source contains duplicate prompts")

    source_export, improved_export, seen = [], [], set()
    for row in rows:
        question = _pick(row, "original_prompt", "prompt")
        answer = _pick(row, "original_completion", "completion")
        new_question = _pick(row, "enhanced_prompt", "rephrased_prompt")
        new_answer = _pick(row, "enhanced_completion", "final_completion")
        if not question or not answer or not new_question or not new_answer:
            raise ValueError("Provider export missing required original/enhanced columns")
        if question not in originals or originals[question] != answer or question in seen:
            raise ValueError("Provider original row does not match unique synthetic release input")
        seen.add(question)
        source_export.append({"prompt": question, "completion": answer})
        improved_export.append({"prompt": new_question, "completion": new_answer})

    if source_export == improved_export:
        raise ValueError("Provider output is byte-for-byte unchanged")
    return source_export, improved_export


def download_for_review(out_dir: Path, api_key: str, *, client_factory=None):
    if not isinstance(api_key, str) or not api_key.strip():
        raise PermissionError("No Adaption API key")
    if client_factory is None:
        from adaption import Adaption
        client_factory = Adaption
    client = client_factory(api_key=api_key)
    status = client.datasets.get_status(DATASET_ID)
    progress = getattr(status, "progress", None)
    processed = getattr(progress, "processed_rows", None)
    print("EXPORT SAFE CHECK: status =", getattr(status, "status", None),
          "processed rows =", processed)
    if status.status != "succeeded":
        raise ValueError("Provider dataset is not fully adapted and ready for read-only export")
    # The SDK nests processed_rows inside progress, which may be null after
    # completion. Always enforce exactly 100 actual exported records below.
    if processed is not None and (type(processed) is not int or processed != EXPECTED_ROWS):
        raise ValueError("Provider reports an unexpected processed-row count")

    data = client.datasets.download(DATASET_ID, file_format="jsonl").read()
    print("EXPORT SAFE CHECK: returned type =", type(data).__name__,
          "byte count =", len(data) if isinstance(data, bytes) else "non-bytes")
    if isinstance(data, bytes) and data:
        try:
            first_line = next(line for line in data.splitlines() if line.strip())
            first_row = json.loads(first_line)
            if isinstance(first_row, dict):
                # Log ONLY field names, never any row contents or model output.
                print("EXPORT SAFE CHECK: provider field names =", sorted(first_row))
        except (ValueError, StopIteration, TypeError):
            print("EXPORT SAFE CHECK: not parseable as standard JSONL")
    # Rebuild the exact checked-in deterministic synthetic seed release.
    generated = out_dir / "_verified_training_source"
    write_release(generated)
    originals, improved = extract_verified_rows(data, generated / "train.jsonl")

    out_dir.mkdir(parents=True, exist_ok=True)
    checksums = {}
    for name, values in (("original.jsonl", originals), ("improved.jsonl", improved)):
        payload = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in values).encode("utf-8")
        target = out_dir / name
        target.write_bytes(payload)
        checksums[name] = hashlib.sha256(payload).hexdigest()
    metadata = {
        "dataset_id": DATASET_ID,
        "source_rows": 240,
        "review_rows": EXPECTED_ROWS,
        "provider_status": "succeeded",
        "original_sha256": checksums["original.jsonl"],
        "improved_sha256": checksums["improved.jsonl"],
        "source_matches_reproducible_train": True,
        "read_only_download": True,
        "content_review_completed": False,
        "intended_use": "For audit only; do not publish as peer-reviewed or model-accuracy evidence",
    }
    (out_dir / "review_manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main() -> int:
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        print("EXPORT DENIED: main branch only")
        return 2
    try:
        result = download_for_review(Path("review_only"), os.environ.get("ADAPTION_API_KEY", ""))
    except (ValueError, PermissionError) as exc:
        # Messages below are ours and deliberately contain no provider payload.
        print("EXPORT CONTRACT FAILURE:", str(exc))
        return 1
    except Exception as exc:
        # Print the exception class ONLY, not the provider message/headers/URLs.
        print("EXPORT SDK FAILURE CLASS:", type(exc).__name__)
        return 1
    print("Read-only Adaption export verified:", result["review_rows"], "rows")
    print("Original SHA-256:", result["original_sha256"])
    print("Improved SHA-256:", result["improved_sha256"])
    print("Independent content-quality review NOT completed. No adaptation or training was launched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
