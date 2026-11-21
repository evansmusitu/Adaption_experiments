# PROOFBENCH — authenticated Adaption pilot evidence

**Status:** The original 240-row synthetic financial-reasoning dataset was uploaded to Adaption, and its **100-row adaptation pilot completed successfully** on November 21, 2026. This is an observed provider dataset-quality result, **not** an independent evaluation of an AI model.

## Directly observed provider records

| Field | Observed result |
|---|---|
| Source dataset | `zimbabwe_business_math` |
| Dataset ID | `eefe77fe-ba8c-4d54-9341-97c327a47fd3` |
| Run ID | `dataset-eefe77fe-ba8c-4d54-9341-97c327a47fd3-1795285525492` |
| Input rows | 240 |
| Pilot cap / processed rows | 100 / 100 |
| Final processing state | `succeeded`, 100% |
| Evaluation state | `succeeded` |
| Evaluation timestamp | 2026-11-21 18:34:15 UTC |
| Quality grades | **C → A** |
| Provider summary quality | **7/10 → 9/10** |
| Provider summary change | **+28.6%** |
| Pre-launch estimate | **1 Adaption credit** |
| Final credit usage | **Not independently returned** |
| Export URLs | None returned by read-only `get_dataset_export_links` as of this observation |

These values were retrieved from the authenticated **Adaption MCP** `get_dataset_status`, `get_dataset_evaluation`, `get_dataset`, and `get_dataset_export_links` calls. The compact machine-readable transcription is in [`evidence/adaption_pilot_observation.json`](../evidence/adaption_pilot_observation.json). This repository note is an observation, **not a digitally signed Adaption audit record**.

### Additional Adaption evaluator details

| Metric | Before | After | Provider-reported gain |
|---|---:|---:|---:|
| Average message/prompt quality | 7.07 | 8.11 | 14.7% |
| Average completion quality | 5.87 | 9.84 | 67.6% |

**Precision caveat:** The provider's separate raw `quality_percentile_before.quality_score` is **6.5**, after is **9**, and its raw `overall_percentage_gain` is **38.72%**. These differ from the **rounded headline summary** (7 → 9, 28.6%). Report these as two distinct representations of the provider's evaluation; do **not** silently substitute one for the other or claim they are independent replications.

## Run configuration

- Instruction dataset with `prompt` and `completion` columns.
- `max_rows: 100` against the imported 240-row source.
- `prompt_rephrase: true`, `deduplication: true`, `reasoning_traces: false`.
- Concise responses and a blueprint requiring preservation of numbers, units and business constraints, and discouraging invented exchange rates, transaction IDs, fees or assumptions.
- Idempotency key `musitu-proofbench-v1-eefe77fe-ba8c-4d54-9341-97c327a47fd3`.
- Exactly one authorized provider adaptation launch accepted. **Do not retry or launch an extra run as a means of checking this result.**

## Scientific and submission limitations

1. Adaption's quality scores are **provider-native dataset assessments**; they do not establish that a model trained on the data is more accurate. No before/after model predictions, paired bootstrap confidence intervals or McNemar comparison have yet been measured.
2. The generated 240-row original is reproducible through the checked-in generator, including the original SHA-256 manifest. However, the **actual Adaption-improved 100-row export** has not been downloaded or row-by-row audited. The provider's `get_dataset_export_links` currently returned null for Hugging Face, Kaggle and Google Sheets.
3. `evidence/manifest.json`, `evidence/original.jsonl`, `evidence/improved.jsonl` therefore **must not** be fabricated to satisfy the static submission gate. That gate intentionally remains **not ready** until both actual artifacts and their hashes are available, and its existing separate-ID assumption should be reconciled with the provider's observed in-place dataset ID.
4. Numeric correctness, privacy, copyrights and dataset licence for generated **improved** rows still require review. The source's CC0-1.0 provenance cannot automatically license the provider-generated output.
5. Final actual credit usage is not provided by the read-only tools checked and must not be represented as a verified 1-credit charge.

## Remaining execution work

- Obtain Adaption's **actual improved dataset export**, inspect the 100 improved prompt/completion pairs, and verify arithmetic, missing-information abstentions, source rights and privacy.
- Preserve the source and improved JSONL with SHA-256 hashes and original/adapted run provenance; update the evidence manifest only when complete and correct.
- Collect real baseline/candidate model responses for `dev.jsonl` and `stress.jsonl`, then run paired scoring and confidence intervals. If model comparison is not feasible, state it as absent.
- Verify team/account submission requirements, publish an accurate demo and submit once with a receipt before the event deadline.
