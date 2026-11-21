"""Static evidence integrity gate for the Adaption Dataset Challenge.

Passing means structurally complete and hash-consistent, NOT that the
Adaption run or evaluation is authentic. Provider and human verification
remain separate manual acceptance requirements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys


def _valid_uuid(value) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        value
    ))


def _valid_score(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 10


def inspect(root) -> dict:
    root = Path(root).resolve()
    errors = []
    for path in (root / "README.md", root / "demo" / "index.html"):
        if not path.is_file() or path.stat().st_size == 0:
            errors.append("Missing or empty: " + path.name)

    manifest_path = root / "evidence" / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("Manifest is not a JSON object")
    except (OSError, ValueError, UnicodeDecodeError):
        return {
            "structurally_ready": False,
            "errors": errors + ["Missing or invalid evidence/manifest.json"],
            "assurance": "STATIC ONLY — never proves Adaption provider authenticity",
        }

    a, b = manifest.get("original_dataset_id"), manifest.get("improved_dataset_id")
    if not _valid_uuid(a) or not _valid_uuid(b):
        errors.append("Original/improved Adaption dataset identifiers are missing or invalid")
    elif a == b:
        # Some Adaption pipelines enhance rows in-place under one dataset UUID.
        # Require an explicit declaration and a run ID tied to that UUID;
        # both original and improved physical files and distinct hashes remain
        # mandatory below. This is only structural validation.
        if manifest.get("in_place_adaptation") is not True:
            errors.append("Identical dataset IDs require an explicit in-place declaration")
        elif not isinstance(manifest.get("run_id"), str) or not re.fullmatch(
            rf"dataset-{re.escape(a)}-[0-9]+", manifest["run_id"]
        ):
            errors.append("In-place adaptation run ID does not match the dataset ID")
    elif manifest.get("in_place_adaptation") is True:
        errors.append("In-place flag conflicts with distinct dataset identifiers")
    if not isinstance(manifest.get("run_id"), str) or not manifest["run_id"].strip():
        errors.append("Missing adaptation run ID")
    if manifest.get("evaluation_provider") != "adaption" or manifest.get("evaluation_status") != "succeeded":
        errors.append("No completed Adaption-native evaluation evidence")
    if not _valid_score(manifest.get("score_before")) or not _valid_score(manifest.get("score_after")):
        errors.append("Before/after Adaption scores are absent or invalid")
    license_value = manifest.get("source_license")
    if not isinstance(license_value, str) or not license_value.strip() or license_value.upper() in {"TBD", "UNKNOWN", "NONE"}:
        errors.append("Source-data licence is not recorded")

    file_hashes = []
    for prefix in ("original", "improved"):
        filename = manifest.get(prefix + "_file")
        expected_hash = manifest.get(prefix + "_sha256")
        if (
            not isinstance(filename, str)
            or not filename.startswith("evidence/")
            or ".." in Path(filename).parts
            or Path(filename).suffix.lower() != ".jsonl"
            or not isinstance(expected_hash, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)
        ):
            errors.append(prefix + " dataset file location or SHA256 is invalid")
            continue
        file_path = (root / filename).resolve()
        if root not in file_path.parents or not file_path.is_file():
            errors.append(prefix + " dataset file does not exist within repository")
            continue
        try:
            contents = file_path.read_bytes()
        except OSError:
            errors.append(prefix + " dataset file unreadable")
            continue
        if not contents or hashlib.sha256(contents).hexdigest() != expected_hash:
            errors.append(prefix + " dataset hash mismatch or empty")
            continue
        try:
            examples = [json.loads(line) for line in contents.splitlines() if line.strip()]
        except (ValueError, UnicodeDecodeError):
            errors.append(prefix + " dataset not valid JSONL")
            continue
        if not examples or any(not isinstance(row, dict) for row in examples):
            errors.append(prefix + " dataset is missing records or has invalid rows")
            continue
        file_hashes.append(expected_hash)

    if len(file_hashes) == 2 and file_hashes[0] == file_hashes[1]:
        errors.append("Original and improved dataset bytes are identical")

    return {
        "structurally_ready": len(errors) == 0,
        "errors": errors,
        "assurance": (
            "STATIC FILE/SHA CHECK ONLY; dataset IDs, native evaluation values "
            "and run provenance must be verified against Adaption separately."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    report = inspect(args.root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["structurally_ready"] else 2


if __name__ == "__main__":
    sys.exit(main())
