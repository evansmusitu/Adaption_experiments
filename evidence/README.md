# Evidence directory — do not publish fabricated results

This directory now contains an **authenticated observation of a completed Adaption 100-row pilot** in `adaption_pilot_observation.json`. That observation contains provider-native metrics but **does not replace the required original/improved exported dataset files**. Final submission is still blocked until genuine improved output is obtained, hashed and reviewed.

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
  "in_place_adaptation": false,
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

**In-place Adaption adaptation:** The completed PROOFBENCH pilot returned the same dataset ID as its imported source. When the provider confirms the adapted output is in-place, set `in_place_adaptation: true` and use the same authentic dataset UUID for both ID fields **only after retrieving different real original and improved JSONL files**. The run ID must match `dataset-<dataset-uuid>-<numeric-run-suffix>`. The static integrity gate retains SHA-256 checks for each physical dataset file. Do not use the observation JSON as a surrogate for an improved export.

Current verified pilot data and its evidence limitations: [`docs/VERIFIED_ADAPTION_PILOT.md`](../docs/VERIFIED_ADAPTION_PILOT.md).

**Actual exports now exist as temporary review-only files**, not public `evidence/` release files: see [the successful read-only export workflow](https://github.com/evansmusitu/Adaption_experiments/actions/runs/44938270782) and [the 100-row content audit](../docs/POST_ADAPTATION_CONTENT_AUDIT.md). Original SHA-256: `46f3ddb18efa5869b8dcd0b01839d1056397b3f14f690779c2faa1562a2a0c6b`; enhanced SHA-256: `7127b6f681392ed43e63093ec371254c486c4e442f62d918d20944669dbeadb1`. The enhanced data **failed quality screening in 14 flagged cases**, so do not promote it to the final released files until issues and rights are reviewed. The manifest gate remains intentionally closed.

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
