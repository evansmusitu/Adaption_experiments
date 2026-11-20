"""Cost-quotation-only Adaption interface for the approved PROOFBENCH dataset.

No adaptation run or training job is allowed from this module.
"""
def estimate(dataset_id: str, token: str, client_factory=None) -> dict:
    raise NotImplementedError("Add exact estimate-only Adaption SDK call")
