"""Independent text-based audit of generated quantitative labels.

Does not import the original benchmark generator's answer-producing functions.
A separate parser reconstructs expected answers directly from prompt text.
"""
def verify_case(row: dict) -> bool:
    raise NotImplementedError("Independent arithmetic parser not implemented")

def audit_cases(rows: list[dict]) -> dict:
    raise NotImplementedError("Independent oracle audit not implemented")
