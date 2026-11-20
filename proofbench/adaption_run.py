"""Credit-capped, manual-only Adaption 100-row pilot.

This API performs a live estimate and, only after explicit authorization and
an acceptable quote, submits at most one idempotent adaptation request.
"""
def launch_pilot(dataset_id, api_key, approval, git_ref, client_factory=None):
    raise NotImplementedError("Implement credit and idempotency gates")
