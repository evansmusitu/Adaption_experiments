"""Adversarial financial-reasoning benchmark (implementation follows tests)."""
from __future__ import annotations

def make_cases(split: str, pairs_per_family: int = 10, seed: int = 20261120) -> list[dict]:
    raise NotImplementedError("Implement deterministic scenario generation")

def validate_splits(parts: dict[str, list[dict]]) -> None:
    raise NotImplementedError("Implement pair and split leakage checks")

def score_predictions(cases: list[dict], predictions: list[dict]) -> dict:
    raise NotImplementedError("Implement independent scoring")

def write_release(output_dir, *, seed: int = 20261120) -> dict:
    raise NotImplementedError("Implement reproducible exports and SHA256 manifest")
