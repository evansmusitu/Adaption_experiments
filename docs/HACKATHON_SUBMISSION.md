# Submission evidence register — Adaption Dataset Challenge

**Due:** December 6, 2026 at 11:59 PM India Standard Time (20:29 Zimbabwe time).
**Submission:** One project link, through **one** of Unstop or Hackyard. Do not double-submit.

## Required artifacts and status

| Evidence | Status at 2026-11-20 | Where to obtain |
|---|---|---|
| Original source dataset (licence/provenance) | Built synthetic seed; provider import not yet executed | GitHub Actions artifact `train.jsonl`; `manifest.json` |
| Dataset generated/improved **on Adaption** | Existing 3 invented datasets already verified through API, but no PROOFBENCH-specific adapted export yet | Adaption account dataset IDs in previous account audit |
| Before/after native Adaption quality scores | Existing unrelated invented datasets: 9.0→9.2, 9.0→9.4, 9.0→9.3 | Existing audited Adaption evaluations; label separately from PROOFBENCH |
| PROOFBENCH before/after adapted dataset | Not yet | Requires upload, actual cost quote and consent to adapt |
| Independent model benchmark | Evaluator works; **real predictions not yet collected** | `proofbench/benchmark.py` + `comparison.py` |
| README and runnable instructions | Prepared | Repo README |
| Human evaluation and blind set | Not yet | Follow research protocol |
| Demo video or interactive assistant | Not yet | Prepare recorded demonstration from genuine results |
| Team's Adaption account verification PDF | Verify separately | Official Google verification form |
| Final submission receipt | Not submitted | Hackyard/Unstop |

## Verified existing Adaption assets

These are owned in the user's Adaption account. They were generated before the new PROOFBENCH benchmark; do not misrepresent them as training data specifically adapted by this repository.

- Dataset `61d434c2-b617-45b0-82f5-44771db25498`: 500 rows, native quality 9.0 to 9.2.
- Dataset `b17502e7-d482-4a5d-bae0-a9ea55b7bfe1`: 1000 rows, native quality 9.0 to 9.4.
- Dataset `5ef42194-6814-45fb-8841-8116482928fa`: 2000 rows, native quality 9.0 to 9.3.

All three datasets were authenticated and inspected by read-only GitHub Actions. Published outputs from these datasets must undergo data-rights and privacy review before being committed to a public repo.

## Execution sequence

1. Review the PR and merge only after checks are green.
2. Inspect the generated train/dev/stress artifacts. Review synthetic labels and add independently written cases.
3. If authorized, manually run the **upload-only** GitHub workflow on main. Save the returned Adaption dataset ID. Do not rerun after an uncertain outcome.
4. Query Adaption's actual adaptation cost for that imported dataset, choose recipes and budget. Owner must approve any credits separately.
5. Run adaptation exactly once; record job ID, dataset ID, run status, cost and exported file hashes. Preserve unchanged original dataset.
6. Retrieve the native Adaption quality evaluation with confirmed status, separately measure model predictions if practical.
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
