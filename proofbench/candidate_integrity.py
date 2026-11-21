"""Static provenance verification for the private PROOFBENCH review candidate.

No provider calls, credit consumption, or false model-accuracy attestations.
Use only against the extracted, privately held original/provider/candidate files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DATASET_ID = "eefe77fe-ba8c-4d54-9341-97c327a47fd3"
RUN_ID = "dataset-eefe77fe-ba8c-4d54-9341-97c327a47fd3-1795285525492"
FLAGGED = frozenset({7, 10, 13, 26, 38, 44, 48, 61, 76, 81, 83, 95, 96, 99})
DRIFT = frozenset({45})
RESTORED = FLAGGED | DRIFT
FILES = {
    "original.jsonl": "source_original_sha256",
    "raw_adaption_improved.jsonl": "raw_provider_sha256",
    "oracle_restored_candidate.jsonl": "candidate_sha256",
}


def _rows(raw: bytes, name: str, expected_count: int) -> list[dict]:
    if len(raw) > 3_000_000 or not raw:
        raise ValueError(f"Unexpected data length: {name}")
    try:
        values = [json.loads(line) for line in raw.splitlines() if line.strip()]
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"Invalid JSONL: {name}") from exc
    if len(values) != expected_count or any(
        not isinstance(x, dict)
        or set(x) != {"prompt", "completion"}
        or any(not isinstance(x[k], str) or not x[k].strip() for k in ("prompt", "completion"))
        for x in values
    ):
        raise ValueError(f"Invalid JSONL row schema/count: {name}")
    return values


def verify_bundle(review_directory, source_training_jsonl) -> dict:
    """Validate every row in the repaired candidate against its actual source."""
    review_directory = Path(review_directory)
    source_training_jsonl = Path(source_training_jsonl)
    manifest = json.loads((review_directory / "candidate_manifest.json").read_text("utf-8"))
    if (
        manifest.get("label") != "ORACLE_RESTORED_REVIEW_CANDIDATE_NOT_NATIVE_ADAPTION_OUTPUT"
        or manifest.get("dataset_id") != DATASET_ID
        or manifest.get("provider_run_id") != RUN_ID
    ):
        raise ValueError("Unexpected research provenance / dataset ID")
    if manifest.get("provider_quality_grade_for_candidate") is not None:
        raise ValueError("No provider quality grade exists for this corrected candidate")
    if manifest.get("provider_native_quality_score_applies_only_to_raw_provider_output") is not True:
        raise ValueError("Provider score attribution guard is missing")
    if manifest.get("independent_expert_review_completed") is not False:
        raise ValueError("Expert review remains a separate manual process")
    if manifest.get("real_model_comparison_completed") is not False:
        raise ValueError("No real model comparison has occurred")
    if (
        manifest.get("confirmed_or_mismatched_enhanced_outputs_restored") != sorted(FLAGGED)
        or manifest.get("additional_prompt_drift_restored") != sorted(DRIFT)
    ):
        raise ValueError("Unapproved restoration indices in manifest")
    if (
        manifest.get("rows") != 100
        or manifest.get("provider_rows_unmodified") != 85
        or manifest.get("original_oracle_restored_rows") != 15
    ):
        raise ValueError("Provenance count mismatch")

    output_rows = {}
    for filename, sha_key in FILES.items():
        payload = (review_directory / filename).read_bytes()
        if hashlib.sha256(payload).hexdigest() != manifest.get(sha_key):
            raise ValueError(f"SHA-256 mismatch for {filename}")
        output_rows[filename] = _rows(payload, filename, 100)

    original, improved, candidate = (
        output_rows["original.jsonl"],
        output_rows["raw_adaption_improved.jsonl"],
        output_rows["oracle_restored_candidate.jsonl"],
    )
    train_rows = _rows(source_training_jsonl.read_bytes(), "original synthetic train", 240)
    train_by_prompt = {r["prompt"]: r for r in train_rows}
    if len(train_by_prompt) != len(train_rows):
        raise ValueError("duplicate source training prompts")
    if len({r["prompt"] for r in original}) != len(original):
        raise ValueError("duplicate original exported prompts")
    for i, (a, b, c) in enumerate(zip(original, improved, candidate)):
        if train_by_prompt.get(a["prompt"]) != a:
            raise ValueError(f"Original exported row {i} not present in training source")
        if i in RESTORED and c != a:
            raise ValueError(f"Restored case {i} must be exactly original")
        if i not in RESTORED and c != b:
            raise ValueError(f"Unmodified case {i} must be exactly provider output")
        if i in RESTORED and b == a:
            raise ValueError(f"Case {i} marked restored but original and provider equal")

    return {
        "dataset_id": DATASET_ID,
        "rows": 100,
        "retained_provider_rows": 85,
        "restored_original_rows": 15,
        "restored_indices": sorted(RESTORED),
        "source_matches_original_240_row_release": True,
        "all_candidate_rows_exactly_traced": True,
        "sha256_verified": True,
        "provider_quality_grade_for_corrected_candidate": None,
        "cleared_for_public_release": False,
        "independent_model_accuracy_proven": False,
        "assurance": "Static provenance only; no provider-authenticated signature or full human review",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, help="Unpacked private review directory")
    parser.add_argument("--training", required=True, help="Reproducible original train.jsonl")
    args = parser.parse_args()
    try:
        report = verify_bundle(args.review, args.training)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"verified": False, "error": str(exc)}))
        return 2
    print(json.dumps({"verified": True, **report}, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
