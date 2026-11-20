"""Manual-only Adaption dataset import, with strict data-hash/approval gates.

Uploading an import is NOT adaptation, model training or an evaluation result.
This code must never be invoked by pull-request or push-triggered CI. It can
change data in the Adaption account; do not rerun after an uncertain outcome.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from .benchmark import write_release

APPROVAL = "APPROVE PROOFBENCH DATA UPLOAD"
EXPECTED_ROWS = 240


def validate_training_export(folder) -> dict:
    target = Path(folder)
    manifest_path = target / "manifest.json"
    train_path = target / "train.jsonl"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        raw = train_path.read_bytes()
    except (OSError, ValueError) as exc:
        raise ValueError("Training bundle is incomplete") from None
    digest = hashlib.sha256(raw).hexdigest()
    if (
        manifest.get("sha256", {}).get("train.jsonl") != digest
        or manifest.get("counts", {}).get("train") != EXPECTED_ROWS
        or manifest.get("train_columns") != ["prompt", "completion"]
    ):
        raise ValueError("Training bundle hash or schema manifest mismatch")
    try:
        rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    except (UnicodeDecodeError, ValueError):
        raise ValueError("Invalid JSONL training bundle") from None
    if len(rows) != EXPECTED_ROWS:
        raise ValueError("Unexpected training row count")
    if any(
        not isinstance(row, dict) or set(row) != {"prompt", "completion"}
        or any(not isinstance(row[field], str) or not row[field].strip()
               for field in ("prompt", "completion"))
        for row in rows
    ):
        raise ValueError("Unexpected content in the training-only export")
    if len({row["prompt"] for row in rows}) != len(rows):
        raise ValueError("Duplicate training prompts detected")
    return {"sha256": digest, "rows": len(rows)}


def _adaption_sdk_upload(filename: str, token: str) -> str:
    # Imported only AFTER explicit approval and integrity checks.
    from adaption import Adaption
    client = Adaption(api_key=token)
    result = client.datasets.upload_file(filename)
    dataset_id = getattr(result, "dataset_id", None)
    if not isinstance(dataset_id, str) or not dataset_id:
        raise RuntimeError("Adaption upload response was missing dataset_id")
    return dataset_id


def upload_once(folder, *, approval: str, git_ref: str, api_key: str, uploader=None):
    if approval != APPROVAL:
        raise PermissionError("Exact manual approval phrase not supplied")
    if git_ref != "refs/heads/main":
        raise PermissionError("Upload must be dispatched from the protected main ref")
    if not isinstance(api_key, str) or not api_key.strip():
        raise PermissionError("ADAPTION_API_KEY is unavailable")
    metadata = validate_training_export(folder)
    upload = uploader if uploader is not None else _adaption_sdk_upload
    result_id = upload(str(Path(folder) / "train.jsonl"), api_key)
    if not isinstance(result_id, str) or not 1 <= len(result_id) <= 128:
        raise RuntimeError("Invalid Adaption dataset identifier")
    return {"dataset_id": result_id, **metadata}


def main():
    work = Path("generated")
    write_release(work)
    try:
        result = upload_once(
            work,
            approval=os.getenv("PROOFBENCH_UPLOAD_APPROVAL", ""),
            git_ref=os.getenv("GITHUB_REF", ""),
            api_key=os.getenv("ADAPTION_API_KEY", ""),
        )
    except PermissionError as exc:
        print("UPLOAD DENIED:", type(exc).__name__)
        return 2
    except Exception:
        # Never print the provider exception, headers, presigned URLs or credentials.
        print("UPLOAD FAILED OR OUTCOME UNCERTAIN. Inspect Adaption datasets before retrying.")
        return 1
    print("Adaption import created:", result["dataset_id"])
    print("Rows:", result["rows"])
    print("SHA256:", result["sha256"])
    print("No adaptation, training or model evaluation requested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
