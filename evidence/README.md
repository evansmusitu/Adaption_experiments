# Evidence directory — do not publish fabricated results

This directory intentionally contains **no final results yet**. Files are added
only after genuine Adaption processing and human evidence review.

## Required public release files

- `evidence/original.jsonl` — actual original/source dataset export.
- `evidence/improved.jsonl` — actual Adaption-improved export.
- `evidence/manifest.json` — metadata, file hashes and native evaluation.

The local structural gate is:

```bash
python3 -m proofbench.submission_gate --root .
```

It must **fail** while evidence is missing. Once a genuine run completes,
populate the following manifest *with real provider values*:

```json
{
  "original_dataset_id": "REPLACE-WITH-REAL-UUID",
  "improved_dataset_id": "REPLACE-WITH-REAL-UUID",
  "run_id": "REPLACE-WITH-REAL-ADAPTION-RUN-ID",
  "evaluation_provider": "adaption",
  "evaluation_status": "succeeded",
  "score_before": null,
  "score_after": null,
  "original_file": "evidence/original.jsonl",
  "improved_file": "evidence/improved.jsonl",
  "original_sha256": "REPLACE-WITH-SHA256",
  "improved_sha256": "REPLACE-WITH-SHA256",
  "source_license": "CC0-1.0"
}
```

This template is documentation, **not** valid result evidence.

Generate the hashes using `sha256sum evidence/*.jsonl` on Linux or an
equivalent secure local hashing tool. Confirm the imported source and adapted
output identifiers, evaluation status and scores against the Adaption platform.

Passing the local checker proves only **file integrity and manifest shape**.
It does NOT authenticate the provider data, demonstrate statistical significance
or prove that independent model accuracy improved. Preserve original Adaption
screenshots, timestamps and run records for independent reviewer verification.

## Required review before public release

Inspect the dataset rows for privacy, confidential records, secrets,
copyright restrictions and unsafe financial claims. Our own deterministic
generated seed fixtures were marked CC0-1.0; that designation does not
automatically extend to externally sourced or provider-generated datasets.
