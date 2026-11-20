"""Single immutable PROOFBENCH pilot recipe for quotation and launch.

Every estimate must price *exactly* these same settings. Do not add
unreviewed data expansion, translation or hidden input fields.
"""
from __future__ import annotations

import re

MAX_ROWS = 100
BLOCKED_INVENT_IDS = frozenset({
    "61d434c2-b617-45b0-82f5-44771db25498",
    "b17502e7-d482-4a5d-bae0-a9ea55b7bfe1",
    "5ef42194-6814-45fb-8841-8116482928fa",
})

def validate_proofbench_source(dataset_id: str) -> None:
    if (
        not isinstance(dataset_id, str)
        or re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            dataset_id,
        ) is None
        or dataset_id in BLOCKED_INVENT_IDS
    ):
        raise ValueError("Expected a newly imported PROOFBENCH dataset UUID")

def pilot_config(dataset_id: str) -> dict:
    validate_proofbench_source(dataset_id)
    return {
        "column_mapping": {"prompt": "prompt", "completion": "completion"},
        "training_type": "instruction_dataset",
        "job_specification": {
            "max_rows": MAX_ROWS,
            "idempotency_key": "musitu-proofbench-v1-" + dataset_id,
        },
        "recipe_specification": {
            "recipes": {
                "prompt_rephrase": True,
                "deduplication": True,
                "reasoning_traces": False,
            },
        },
        "brand_controls": {
            "length": "concise",
            "blueprint": (
                "Maintain correct numerical amounts, units and business constraints. "
                "Do not invent exchange rates, transaction identifiers, fees, taxes "
                "or assumptions. State when the problem lacks essential data. "
                "Preserve the original question's conditional financial meaning."
            ),
        },
    }
