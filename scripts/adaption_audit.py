#!/usr/bin/env python3
"""Read-only Adaption API connectivity/metadata audit.

No dataset rows, request headers, response bodies, credentials, or errors from
the API are printed. Only the official HTTPS API host is contacted.
"""
from __future__ import annotations

import collections
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.prod.adaptionlabs.ai/api/v1"
KNOWN_DATASETS = (
    "61d434c2-b617-45b0-82f5-44771db25498",
    "b17502e7-d482-4a5d-bae0-a9ea55b7bfe1",
    "5ef42194-6814-45fb-8841-8116482928fa",
)


def api_get(resource: str, key: str) -> dict:
    if not resource.startswith("/datasets") or "://" in resource:
        raise ValueError("Only fixed dataset read endpoints are permitted.")
    req = urllib.request.Request(
        BASE + resource,
        headers={
            "Authorization": "Bearer " + key,
            "Accept": "application/json",
            "User-Agent": "musitu-adaption-readonly-audit/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(2_000_001)
    except urllib.error.HTTPError as exc:
        # Never print returned bodies: some providers include sensitive details.
        raise RuntimeError("Adaption HTTP status " + str(exc.code)) from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("Adaption network request failed") from None
    if len(raw) > 2_000_000:
        raise RuntimeError("Adaption response exceeded the read-only limit")
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise RuntimeError("Adaption response was not valid JSON") from None
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected API response structure")
    return payload


def safe_metric(value: object) -> str:
    """Format only bounded numeric metrics, never response bodies."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "unavailable"
    if not (-1_000_000 <= value <= 1_000_000):
        return "unavailable"
    return str(round(float(value), 3))


def audit() -> int:
    key = os.getenv("ADAPTION_API_KEY", "").strip()
    if not key:
        print("ERROR: ADAPTION_API_KEY is unavailable to this workflow.")
        return 2

    try:
        page = api_get("/datasets?limit=100&sort=created_at&sort_direction=desc", key)
    except RuntimeError as exc:
        print("Connection check failed:", str(exc))
        return 1

    rows = page.get("datasets")
    if not isinstance(rows, list):
        print("Connected, but the dataset-list response schema was unexpected.")
        return 1

    statuses = collections.Counter(
        item.get("status", "unknown") if isinstance(item, dict) else "unknown"
        for item in rows
    )
    print("AUTHENTICATED: Adaption API accepted the key.")
    print("Datasets on first page:", len(rows))
    print("First-page status counts:", json.dumps(dict(sorted(statuses.items()))))
    print("More pages available:", bool(page.get("next_cursor")))

    for number, dataset_id in enumerate(KNOWN_DATASETS, start=1):
        try:
            metadata = api_get("/datasets/" + dataset_id, key)
        except RuntimeError as exc:
            print("Existing dataset", number, "metadata unavailable:", str(exc))
            continue
        details = metadata.get("dataset", metadata)
        if not isinstance(details, dict):
            print("Existing dataset", number, "metadata structure unexpected")
            continue
        status = details.get("status")
        row_count = details.get("row_count")
        kind = details.get("kind")
        safe_status = status if status in ("pending", "running", "awaiting_input", "succeeded", "failed") else "unknown"
        safe_kind = kind if kind in ("uploaded", "combined", "invented", "augmented", "translated", "localized") else "unknown"
        safe_count = row_count if type(row_count) is int and row_count >= 0 else "unknown"
        print(f"Existing dataset {number}: status={safe_status}; kind={safe_kind}; row_count={safe_count}")
        summary = details.get("evaluation_summary")
        if isinstance(summary, dict):
            print(
                f"Dataset {number} summary: "
                f"before={safe_metric(summary.get('score_before'))}; "
                f"after={safe_metric(summary.get('score_after'))}; "
                f"improvement_pct={safe_metric(summary.get('improvement_percent'))}"
            )
        else:
            print(f"Dataset {number} has no completed compact evaluation summary")
        try:
            evaluation = api_get("/datasets/" + dataset_id + "/evaluation", key)
        except RuntimeError as exc:
            print(f"Dataset {number} evaluation request unavailable: {exc}")
            continue
        evaluation_status = evaluation.get("status")
        safe_evaluation_status = (
            evaluation_status if evaluation_status in ("pending", "running", "succeeded", "failed", "skipped")
            else "unknown"
        )
        print(f"Dataset {number} evaluation status: {safe_evaluation_status}")
        quality = evaluation.get("quality")
        if isinstance(quality, dict):
            print(
                f"Dataset {number} quality: "
                f"before={safe_metric(quality.get('score_before'))}; "
                f"after={safe_metric(quality.get('score_after'))}; "
                f"improvement_pct={safe_metric(quality.get('improvement_percent'))}; "
                f"percentile_after={safe_metric(quality.get('percentile_after'))}"
            )

    print("Read-only audit completed; no adaptation or training was started.")
    return 0


if __name__ == "__main__":
    sys.exit(audit())
