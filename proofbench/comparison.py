"""Paired baseline-vs-adapted model comparison; implemented test-first."""

def compare(cases: list[dict], baseline: list[dict], candidate: list[dict], *, resamples: int = 2000) -> dict:
    raise NotImplementedError("Compare matched predictions with pair bootstrap and exact McNemar test")
