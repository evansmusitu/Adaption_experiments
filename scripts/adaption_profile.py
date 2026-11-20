#!/usr/bin/env python3
"""Private-in-memory Adaption dataset analysis with aggregate-only public CI logs.

Only three approved dataset IDs are queried. The downloaded JSONL bytes and
individual prompts/completions are never saved, printed, or uploaded as artifacts.
No network requests other than fixed GET endpoints are allowed.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

HOST = "https://api.prod.adaptionlabs.ai"
PREFIX = "/api/v1/datasets/"
DATASETS = (
    "61d434c2-b617-45b0-82f5-44771db25498",
    "b17502e7-d482-4a5d-bae0-a9ea55b7bfe1",
    "5ef42194-6814-45fb-8841-8116482928fa",
)
MAX_DOWNLOAD_BYTES = 30_000_000

CATEGORIES = {
    "finance": (
        "finance", "financial", "profit", "revenue", "cash flow", "cashflow",
        "investment", "net present value", "npv", "interest", "loan",
        "accounting", "balance sheet", "inventory", "currency", "exchange rate",
        "market", "portfolio", "invoice", "tax", "gross margin", "budget",
        "zig", "ecocash", "paynow", "usd", "dollar", "shilling",
    ),
    "math_optimization": (
        "optimization", "optimisation", "linear program", "constraint",
        "maximise", "maximize", "minimise", "minimize", "equation",
        "probability", "statistics", "statistical", "matrix", "calculus",
        "solve for", "calculate", "percentage", "algebra",
    ),
    "software_ai": (
        "python", "javascript", "typescript", "machine learning",
        "artificial intelligence", "algorithm", "coding", "programming",
        "api", "json", "database", "neural network", "function",
    ),
    "science": (
        "physics", "chemistry", "biology", "circuit", "voltage",
        "electron", "molecule", "reaction", "thermodynamics",
        "temperature", "robotics", "sensor",
    ),
    "language": (
        "shona", "ndebele", "swahili", "translate", "translation",
        "language learning", "grammar", "vocabulary", "linguistic",
    ),
}

def get_bytes(path: str, api_key: str, max_bytes: int) -> bytes:
    if not any(
        path == PREFIX + dataset_id
        or path == PREFIX + dataset_id + "/evaluation"
        or path == PREFIX + dataset_id + "/download?fileFormat=jsonl"
        for dataset_id in DATASETS
    ):
        raise ValueError("Endpoint not on the read-only allowlist")
    req = urllib.request.Request(
        HOST + path,
        headers={
            "Authorization": "Bearer " + api_key,
            "Accept": "application/json",
            "User-Agent": "musitu-adaption-aggregate-profiler/1",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            data = response.read(max_bytes + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("HTTP " + str(exc.code)) from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("Network error") from None
    if len(data) > max_bytes:
        raise RuntimeError("Data limit exceeded")
    return data

def get_json(path: str, key: str) -> dict:
    try:
        payload = json.loads(get_bytes(path, key, 1_000_000))
        if isinstance(payload, dict):
            return payload
    except (ValueError, UnicodeDecodeError):
        pass
    raise RuntimeError("Unexpected JSON response")

def prompt_from_row(row: dict) -> str:
    """Find primary instructions, else use bounded text across unknown schemas.

    Invented datasets may export `enhanced_prompt` or nested content rather
    than the uploaded-dataset `original_prompt` column. No text is ever logged.
    """
    primary = (
        "original_prompt", "enhanced_prompt", "generated_prompt", "prompt",
        "instruction", "question", "query", "input", "text",
    )
    for field in primary:
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value[:6000]

    # Fallback: compile readable text from arbitrary export schemas without
    # exposing any individual row. Keep conversation depth and bytes bounded.
    excluded = {
        "id", "dataset_id", "row_id", "run_id", "source_dataset_id",
        "created_at", "updated_at", "url", "source_url", "metadata",
    }
    parts = []
    def collect(value, depth):
        if depth > 2 or sum(map(len, parts)) >= 6000:
            return
        if isinstance(value, str) and len(value.strip()) >= 15:
            parts.append(value[:2500])
        elif isinstance(value, list):
            for item in value[:8]:
                collect(item, depth + 1)
        elif isinstance(value, dict):
            for key, item in list(value.items())[:15]:
                if key not in excluded:
                    collect(item, depth + 1)
    for key, value in list(row.items())[:30]:
        if key not in excluded:
            collect(value, 0)
    return " ".join(parts)[:6000]

def aggregate_jsonl(raw: bytes) -> dict:
    counts = collections.Counter()
    hashes = set()
    total = 0
    missing = 0
    dupe = 0
    lengths = 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except (UnicodeDecodeError, ValueError):
            counts["malformed"] += 1
            continue
        if not isinstance(row, dict):
            counts["malformed"] += 1
            continue
        total += 1
        prompt = prompt_from_row(row)
        if not prompt.strip():
            missing += 1
            continue
        norm = re.sub(r"\s+", " ", prompt.casefold()).strip()
        digest = hashlib.sha256(norm.encode("utf-8")).digest()
        if digest in hashes:
            dupe += 1
        hashes.add(digest)
        lengths += len(prompt)
        # A category counts at most once per prompt; categories can overlap.
        for category, words in CATEGORIES.items():
            if any(re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", norm) for w in words):
                counts[category] += 1
    return {
        "rows_checked": total,
        "unreadable_rows": counts["malformed"],
        "rows_without_extractable_text": missing,
        "exact_duplicate_extracted_text": dupe,
        "average_prompt_length": round(lengths / max(1, total - missing)),
        "topic_heuristics": {key: counts[key] for key in CATEGORIES},
    }

def scalar(value):
    # Strictly constrain the shape of values emitted into *public* logs.
    if value is None:
        return None
    if type(value) is bool:
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if abs(value) <= 100_000:
            return round(value, 3)
    return None

def main() -> int:
    key = os.getenv("ADAPTION_API_KEY", "").strip()
    if not key:
        print("ERROR: GitHub Actions secret ADAPTION_API_KEY is unavailable")
        return 2
    for position, dataset_id in enumerate(DATASETS, 1):
        print("Dataset", position)
        base = PREFIX + dataset_id
        try:
            record = get_json(base, key)
            detail = record.get("dataset", record)
            kind = detail.get("kind") if isinstance(detail, dict) else None
            if kind not in {"uploaded", "combined", "invented", "augmented", "translated", "localized"}:
                kind = "unknown"
            mapping = detail.get("configured_column_mapping") if isinstance(detail, dict) else None
            print("  origin:", kind)
            print("  has_column_mapping:", isinstance(mapping, dict))
            quality = detail.get("evaluation_summary") if isinstance(detail, dict) else None
            print("  native_evaluation_summary_available:", isinstance(quality, dict))
            try:
                evaluation = get_json(base + "/evaluation", key)
                status = evaluation.get("status", "unknown")
                if status not in {"pending", "running", "succeeded", "failed", "skipped"}:
                    status = "unknown"
                print("  native_evaluation_status:", status)
                metrics = evaluation.get("quality")
                if isinstance(metrics, dict):
                    print("  native_quality_scores:", json.dumps({
                        "before": scalar(metrics.get("score_before")),
                        "after": scalar(metrics.get("score_after")),
                        "improvement_percent": scalar(metrics.get("improvement_percent")),
                    }, sort_keys=True))
            except RuntimeError as exc:
                print("  native_evaluation_not_available:", str(exc))
            try:
                data = get_bytes(base + "/download?fileFormat=jsonl", key, MAX_DOWNLOAD_BYTES)
                print("  aggregate_profile:", json.dumps(aggregate_jsonl(data), sort_keys=True))
            except RuntimeError as exc:
                print("  aggregate_profile_unavailable:", str(exc))
        except RuntimeError as exc:
            print("  metadata_unavailable:", str(exc))
            return 1
    print("Read-only analysis finished. No dataset rows or responses were logged or retained.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
