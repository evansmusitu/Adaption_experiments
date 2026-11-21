# Submission evidence register — Adaption Dataset Challenge

**Due:** December 6, 2026 at 11:59 PM India Standard Time (20:29 Zimbabwe time).
**Submission:** One project link, through **one** of Unstop or Hackyard. Do not double-submit.

## Required artifacts and status

| Evidence | Status at 2026-11-21 | Where to obtain |
|---|---|---|
| Original source dataset (licence/provenance) | 240 original rows imported and verified; reproducible GitHub source retained | GitHub Actions artifact `train.jsonl`; `manifest.json` |
| Dataset generated/improved **on Adaption** | PROOFBENCH 100-row adaptation succeeded; actual improved-row export still missing | Adaption account dataset IDs in previous account audit |
| Before/after native Adaption quality scores | PROOFBENCH provider grade C→A, summary 7→9 (+28.6%); three older Invent results unrelated | Existing audited Adaption evaluations; label separately from PROOFBENCH |
| PROOFBENCH before/after adapted dataset | Provider pilot complete; improved-row export and hashes still missing | See verified pilot report |
| Independent model benchmark | Evaluator works; **real predictions not yet collected** | `proofbench/benchmark.py` + `comparison.py` |
| README and runnable instructions | Prepared | Repo README |
| Human evaluation and blind set | Not yet | Follow research protocol |
| Demo video or interactive assistant | Not yet | Prepare recorded demonstration from genuine results |
| Team's Adaption account verification PDF | Verify separately | Official Google verification form |
| Final submission receipt | Not submitted | Hackyard/Unstop |

## Completed PROOFBENCH adaptation (provider-verified)

- **Dataset ID:** `eefe77fe-ba8c-4d54-9341-97c327a47fd3`; **run ID:** `dataset-eefe77fe-ba8c-4d54-9341-97c327a47fd3-1795285525492`.
- **Original seed:** 240 rows; **one approved adapted pilot:** 100 rows processed, provider status `succeeded`.
- **Native quality evaluation:** C → A, provider summary 7/10 → 9/10 (+28.6%); raw evaluation includes finer-precision values and a separate 38.72% gain.
- **Credit estimate:** 1; **actual charge:** not returned.
- **Improved export:** still unavailable from linked tools; original/improved file hashes not yet produced. This remains the blocking gate before claiming a complete downloadable adaptation artifact.
- **Model improvement:** **not demonstrated**; requires real predictions and independent scoring.

See [the authenticated pilot evidence](VERIFIED_ADAPTION_PILOT.md). Preserve numeric caveats and abstention behavior when reviewing any improved output.

## Verified existing Adaption assets

These are owned in the user's Adaption account. They were generated before the new PROOFBENCH benchmark; do not misrepresent them as training data specifically adapted by this repository.

- Dataset `61d434c2-b617-45b0-82f5-44771db25498`: 500 rows, native quality 9.0 to 9.2.
- Dataset `b17502e7-d482-4a5d-bae0-a9ea55b7bfe1`: 1000 rows, native quality 9.0 to 9.4.
- Dataset `5ef42194-6814-45fb-8841-8116482928fa`: 2000 rows, native quality 9.0 to 9.3.

All three datasets were authenticated and inspected by read-only GitHub Actions. Published outputs from these datasets must undergo data-rights and privacy review before being committed to a public repo.

## Execution sequence

1. Review the PR and merge only after checks are green.
2. Inspect the generated train/dev/stress artifacts. Review synthetic labels and add independently written cases.
3. **Complete:** Original 240-row source was imported once; Adaption dataset ID recorded above. Do **not** reimport or re-adapt merely to check status.
4. **Complete:** Real live estimate of 1 Adaption credit and explicit pilot approval were recorded; actual billed credit usage remains unknown.
5. **Complete except exports:** One 100-row adaptation succeeded; run ID recorded above. Obtain actual improved rows and their hashes before claiming downloadable deliverables.
6. **Complete for native quality only:** Adaption returned a successful C→A evaluation; independent model predictions and human review remain outstanding.
7. Produce README evidence table and truthful three-minute video; include negative results and failure analysis.
8. Complete one account verification PDF (separate submission) and submit the project exactly once. Save timestamp and receipt.

## Demo storyboard (3 minutes)

- **0:00–0:25** Why financial AI mistakes and missing data matter in underserved markets.
- **0:25–0:55** Same base scenario, two counterfactual variants; correct response changes.
- **0:55–1:25** Provenance, training schema, separate holdout and independent mathematical oracle.
- **1:25–2:05** Actual Adaption run configuration and native before/after evaluation (only after verified).
- **2:05–2:40** Actual baseline/candidate predictions, paired accuracy and failures (only after measured).
- **2:40–3:00** Reproduce results from GitHub, limitations and business relevance.

Do not substitute invented demo metrics for actual results. Optional model training is not required by current competition rules.

## Official resources

- [Hackyard main event and deliverables](https://hackyard.org/events/adaption-labs)
- [Hackyard deadline and verification](https://hackyard.org/events/adaption-labs/schedule)
- [Hackyard submission instructions](https://hackyard.org/events/adaption-labs/submit)
- [Official Hackyard team page](https://app.hackyard.org/e/adaption-labs)
- [Account verification form](https://docs.google.com/forms/d/e/1FAIpQLSeQeCQYvvjB2QQA8E_vvboWg324g53gXtK6dekXWaM4QbjfnQ/viewform)
