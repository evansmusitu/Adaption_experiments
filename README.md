# MUSITU PROOFBENCH — Verified Financial Reasoning Data

**Adaption Dataset Challenge • November 20–December 6, 2026**

This repository is an isolated public hackathon workspace. Its primary research question is:

> Can targeted, mathematically verifiable, counterfactual financial examples improve AI answer reliability and appropriate abstention more than synthetic data expansion alone?

**Status:** This is an engineered dataset and evaluation harness, **not yet a validated performance improvement**. No external model predictions or trained models are included. Do not interpret any test-suite 100% correctness as model accuracy.

## What exists and what it proves

| Component | Status | Evidence |
|---|---|---|
| Original, deterministic synthetic training data | Built by `proofbench.benchmark` | 240 prompt/completion examples |
| Separate adversarial development set | Built | 120 cases (60 paired scenarios) |
| Stress test set | Built | 96 cases (48 paired scenarios) |
| Leakage and mathematical sanity tests | CI-verified | Offline tests |\n| Independent re-parsing of generated answers | CI-verified | 456 synthetic answer keys audited |\n| Cross-dataset overlap | Read-only Adaption audit succeeded | 3,500 unique normalized prompts, 0 exact overlaps |\n| Interactive offline demo | Built | [Open demo source](demo/index.html) |\n| 100-row PROOFBENCH adaptation cost estimator | Prepared, not yet run on imported dataset | Manual GitHub Actions quote |
| Counterfactual strict-pair scoring | Built and tested | `score_predictions` |
| Paired comparison with grouped bootstrap + exact McNemar | Built and tested | `proofbench.comparison` |
| Secure Adaption upload | Manual-only workflow prepared | Not launched |
| Adaption generated-data workspace | Existing read-only API audits | 3 existing invented datasets; 3,500 rows total |
| PROOFBENCH dataset adapted on Adaption | **Not yet** | Requires import, quote and approval |
| Genuine model before/after experiment | **Not yet** | Requires baseline/candidate predictions |
| Human-reviewed independent blind holdout | **Not yet** | Must be collected separately |
| Hackathon submission | **Not yet** | Close Dec 6, 11:59 PM IST |

### Six scenario families

- FX conversion: supplied rate versus missing, dated conversion rate.
- Inventory: feasible stock counts versus impossible negative inventory.
- Receipts: two unique transactions versus a duplicated receipt ID.
- Interest: simple interest versus annual compounding.
- Profit: known delivery overhead versus missing overhead.
- Processing fees: per-item fee versus single flat fee.

Every scenario has two counterfactual variants, with independently computed decimal/integer oracles. Changing a single decisive condition changes the correct answer or whether an exact answer is justified.

## Reproduce locally

Python 3.10+, **no API key, network, GPU or paid credits required**:

```bash
python3 -m unittest discover -s tests -p 'test_proofbench_contract.py' -v
python3 -m unittest discover -s tests -p 'test_comparison.py' -v
python3 -m unittest discover -s tests -p 'test_adaption_bridge.py' -v\npython3 -m unittest discover -s tests -p 'test_independent_audit.py' -v\npython3 -m unittest discover -s tests -p 'test_adaption_estimate.py' -v\npython3 -m unittest discover -s tests -p 'test_overlap.py' -v
python3 -m proofbench.benchmark --output generated
```

Outputs are `generated/train.jsonl`, `dev.jsonl`, `stress.jsonl` and `manifest.json` with SHA-256 checksums. The training export contains **only** prompt/completion columns. The other files retain test-case metadata and gold answers. CI also packages these as an artifact. Do not train on development/stress gold answers.

### Score an external model

Have a baseline or adapted model generate **structured predictions** as JSONL:

```json
{"id":"dev-fx_missing-0000-a","kind":"numeric","value":"12.50","unit":"USD"}
{"id":"dev-fx_missing-0000-b","kind":"clarify","value":null,"unit":"USD"}
```

The example values above are only FORMAT EXAMPLES; use the actual case IDs and model predictions.

```bash
python3 -m proofbench.benchmark \
  --cases generated/dev.jsonl --predictions baseline.jsonl

python3 -m proofbench.comparison \
  --cases generated/dev.jsonl \
  --baseline baseline.jsonl \
  --candidate adapted.jsonl \
  --output comparison.json
```

The evaluator enforces full correct pairs, numeric units, precision and abstention. `comparison.py` computes paired-group bootstrap uncertainty and an exact McNemar p-value at the pair level. It **never generates fake model scores**.

## Adaption integration and credit safety

GitHub Actions has successfully authenticated to Adaption via the `ADAPTION_API_KEY` secret, checked the three existing invented datasets, and retrieved native evaluation summaries.

The **manual-only** workflow `.github/workflows/proofbench-upload.yml` prepares an authenticated dataset upload from `generated/train.jsonl`. It requires the exact input `APPROVE PROOFBENCH DATA UPLOAD`, executes only on `main`, and has no adaptation/training calls. The upload changes the Adaption account; **do not repeat it after an uncertain outcome**. It is not a substitute for the separate credit-approved adaptation workflow.

The estimate-only workflow `.github/workflows/proofbench-estimate.yml` is manually dispatched with the new PROOFBENCH dataset UUID. It validates a 100-row pilot quote and cannot launch adaptation. The source import uses `processing_mode="adapt"` to prepare for the later adaptation call; the unchanged `train.jsonl` and its SHA-256 manifest in GitHub preserve the original control data. The import workflow itself does not call `datasets.adapt` or train a model. Verify 240 ingested rows and the quoted mapping before approving any credits.\n\nThe manual-only `proofbench-adaption-launch.yml` implements a fresh 100-row quote and explicit approval gate for up to 10 **estimated** credits using the exact same configuration as `proofbench-estimate.yml`. **Final provider usage may differ from quoted credits.** The runbook at [docs/ADAPTION_RUNBOOK.md](docs/ADAPTION_RUNBOOK.md) explains the import, compatibility and non-retry rules.\n\nThe pre-existing `adaption-launch-proofbench.yml` is a different credit-consuming Invent experiment. Do **not** launch it assuming it adapts this training file; Invent and Adapt are distinct Adaption workflows.

## Demonstration and cross-dataset audit\n\nThe mobile-friendly [offline interactive demo](demo/index.html) presents six real fixtures from the deterministic generator. It does **not** claim model improvement or show fake baseline results.\n\nThe authenticated overlap audit inspected 500 + 1,000 + 2,000 existing Invent rows, finding 3,500 unique normalized prompts, zero exact normalized duplicates within any dataset, and zero exact shared prompts between datasets. This is a strict text-level result only; it does **not** rule out paraphrase or numeric-template repetition. See the authenticated GitHub Actions run #44738341995.\n\n## Research quality limitations

- Data are programmatically synthetic, fictional and not human-reviewed.
- Split groups and lexical templates differ, but all families share generative mechanisms; this is **not a true blinded out-of-distribution benchmark**.
- Exact Oracle scoring measures structured predictions supplied by real models only; no model improvement has been measured yet.
- An Adaption dataset-quality score is not model accuracy.
- A third-party manual review and withheld evaluation set are required before claims of real-world reliability.
- No investment, regulatory or accounting advice should be inferred from these research fixtures.
- No private AXIOM repositories or customer records are copied into this project.

## Before submitting to Hackyard

Follow [the research protocol](docs/PROOFBENCH_PROTOCOL.md) and [submission evidence checklist](docs/HACKATHON_SUBMISSION.md). The challenge requests source and improved datasets, before/after evaluation evidence, a README, license/provenance, and a demo. Submit to only one approved platform by December 6, 2026 at 11:59 PM IST.

### Documentation

- [Adaption Adaptive Data](https://docs.adaptionlabs.ai/adaptive-data/overview)
- [Adaption upload guide](https://docs.adaptionlabs.ai/adaptive-data/create-a-dataset)
- [Adaption evaluation guide](https://docs.adaptionlabs.ai/adaptive-data/evaluate-dataset-quality)
- [Hackyard submission rules](https://hackyard.org/events/adaption-labs/submit)

**Licence notice:** Generated deterministic synthetic rows are marked CC0-1.0 in their manifest. The source-code licence has not yet been selected; publication here is not a blanket permission to reuse private MUSITU AXIOM code. Do not assume provider-generated rows are covered by this release's provenance declaration.
