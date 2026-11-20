"""Private-in-memory, hash-based cross-dataset prompt overlap.

Exact normalized string matching only: not a semantic-duplicate detector.
Outputs aggregate counts without prompt samples, completion text or hashes.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import re
import unicodedata


def _digest(text: str) -> bytes:
    norm = unicodedata.normalize("NFKC", text).casefold()
    norm = re.sub(r"\s+", " ", norm).strip()
    return hashlib.sha256(norm.encode("utf-8")).digest()


def analyze(datasets: list[list[dict]]) -> dict:
    sets = []
    row_counts = []
    duplicates = []
    missing = []
    for rows in datasets:
        seen = set()
        present = 0
        missing_count = 0
        repeated = 0
        row_counts.append(len(rows))
        for row in rows:
            value = row.get("enhanced_prompt") if isinstance(row, dict) else None
            if not isinstance(value, str) or not value.strip():
                missing_count += 1
                continue
            present += 1
            h = _digest(value)
            if h in seen:
                repeated += 1
            seen.add(h)
        sets.append(seen)
        duplicates.append(repeated)
        missing.append(missing_count)
    count = len(sets)
    matrix = [
        [0 if left == right else len(sets[left].intersection(sets[right]))
         for right in range(count)]
        for left in range(count)
    ]
    all_unique = len(set().union(*sets)) if sets else 0
    return {
        "row_counts": row_counts,
        "within_duplicate_rows": duplicates,
        "missing_prompts": missing,
        "pairwise_shared_unique_prompts": matrix,
        "global_unique_prompts": all_unique,
        "method": "Exact match after Unicode normalization, whitespace collapse and case-folding",
        "limitation": "Different numeric values or paraphrases count as distinct; not a semantic overlap measure",
        "safety": "No prompt text, completion content, identifiers or hashes are emitted",
    }
