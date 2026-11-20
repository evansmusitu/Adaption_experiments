"""Manual-only Adaption dataset upload of generated training examples."""

def validate_training_export(folder):
    raise NotImplementedError("Validate exact content hash and training-only columns")

def upload_once(folder, *, approval: str, git_ref: str, api_key: str, uploader=None):
    raise NotImplementedError("Verify manual approval before one provider upload")
