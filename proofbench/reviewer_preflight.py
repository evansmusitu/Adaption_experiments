"""Review-desk decision completeness checker; NEVER grants publication permission.

This validates the exact browser-exported 100-case decision schema against
the known review-candidate manifest. It does not authenticate who clicked
"approved", establish copyright permissions, or validate response accuracy.
No network, provider API, credentials, or chargeable operations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

DATASET_ID = "eefe77fe-ba8c-4d54-9341-97c327a47fd3"
RESTORED = frozenset({7, 10, 13, 26, 38, 44, 45, 48, 61, 76, 81, 83, 95, 96, 99})
EXPECTED_LABEL = "ORACLE_RESTORED_REVIEW_CANDIDATE_NOT_NATIVE_ADAPTION_OUTPUT"
DIGEST_MAP = {
    "source_sha256": "source_original_sha256",
    "provider_sha256": "raw_provider_sha256",
    "candidate_sha256": "candidate_sha256",
}
VERDICTS = {"approved", "unreviewed", "needs_fix"}


def inspect_review(review_document: dict, candidate_manifest: dict) -> dict:
    """Return *structural* completion status, never authorization to release."""
    if not isinstance(review_document, dict) or not isinstance(candidate_manifest, dict):
        raise ValueError("review and manifest must be JSON objects")
    m = candidate_manifest
    r = review_document
    if (m.get("label") != EXPECTED_LABEL or m.get("dataset_id") != DATASET_ID
            or r.get("dataset_id") != DATASET_ID
            or m.get("rows") != 100 or m.get("provider_rows_unmodified") != 85
            or m.get("original_oracle_restored_rows") != 15
            or m.get("provider_quality_grade_for_candidate") is not None):
        raise ValueError("candidate identity and provenance metadata mismatch")
    for field, expected_field in DIGEST_MAP.items():
        digest = r.get(field)
        if (not isinstance(digest, str) or not re.fullmatch("[0-9a-f]{64}", digest)
                or digest != m.get(expected_field)):
            raise ValueError(f"review/manifest hash digest mismatch: {field}")
    if r.get("manual_review") is not True:
        raise ValueError("invalid review export format")
    if not isinstance(r.get("reviewed_on"), str) or not r["reviewed_on"].strip():
        raise ValueError("missing review timestamp")
    cases = r.get("cases")
    if not isinstance(cases, list) or len(cases) != 100:
        raise ValueError("expected 100 review cases")
    seen = set()
    counts = {"approved": 0, "unreviewed": 0, "needs_fix": 0}
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("invalid case record")
        index, number, source = (case.get("index_zero_based"),
                                 case.get("case_number"), case.get("source"))
        if (type(index) is not int or index < 0 or index >= 100
                or type(number) is not int or number != index + 1
                or index in seen):
            raise ValueError("duplicate or inconsistent case numbering")
        seen.add(index)
        if source != ("restored_original" if index in RESTORED else "raw_provider"):
            raise ValueError(f"case {number}: source provenance mismatch")
        verdict = case.get("verdict")
        if verdict not in VERDICTS:
            raise ValueError(f"case {number}: invalid reviewer verdict")
        if not isinstance(case.get("notes"), str) or len(case["notes"]) > 20000:
            raise ValueError(f"case {number}: invalid reviewer notes")
        counts[verdict] += 1
    if seen != set(range(100)):
        raise ValueError("review case set not complete")
    complete = counts["approved"] == 100
    return {
        "dataset_id": DATASET_ID,
        "case_count": 100,
        **counts,
        "structurally_complete": complete,
        "reviewer_identity_verified": False,
        "output_redistribution_cleared": False,
        "ready_for_public_release": False,
        "assurance": (
            "Browser-exported decisions only; no authenticated reviewer identity, "
            "verified response correctness, signed rights grant, or release authorization"
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-decisions", required=True)
    parser.add_argument("--candidate-manifest", required=True)
    args = parser.parse_args(argv)
    try:
        decision = json.loads(Path(args.review_decisions).read_text("utf-8"))
        manifest = json.loads(Path(args.candidate_manifest).read_text("utf-8"))
        report = inspect_review(decision, manifest)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"structurally_complete": False, "error": str(exc)}))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["structurally_complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
