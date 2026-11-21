# MUSITU PROOFBENCH — Verified Financial Reasoning Data

**Adaption Dataset Challenge • November 20–December 6, 2026**

This repository is an isolated public hackathon workspace. Its primary research question is:

> Can targeted, mathematically verifiable, counterfactual financial examples improve AI answer reliability and appropriate abstention more than synthetic data expansion alone?

**Status:** The **Adaption-native 100-row dataset adaptation succeeded (C → A; provider summary 7/10 → 9/10)**. That is verified *dataset quality*, **not** an independently validated improvement in trained-model accuracy. No external model predictions or trained models are included; test-suite correctness is not model accuracy.

## What exists and what it proves

| Component | Status | Evidence |
|---|---|---|
| Original, deterministic synthetic training data | Built by `proofbench.benchmark` | 240 prompt/completion examples |
| Separate adversarial development set | Built | 120 cases (60 paired scenarios) |
| Stress test set | Built | 96 cases (48 paired scenarios) |
| Leakage and mathematical sanity tests | CI-verified | Offline tests |
| Independent re-parsing of generated answers | CI-verified | 456 synthetic answer keys audited |
| Cross-dataset overlap | Read-only Adaption audit succeeded | 3,500 unique normalized prompts, 0 exact overlaps |
| Interactive offline demo | Built | [Open demo source](demo/index.html) |
| 100-row PROOFBENCH adaptation cost quotation | **Verified live** | 1 estimated credit; actual final usage not returned |
| Counterfactual strict-pair scoring | Built and tested | `score_predictions` |
| Paired comparison with grouped bootstrap + exact McNemar | Built and tested | `proofbench.comparison` |
| Secure Adaption upload | **Completed** | 240 original rows, Adaption dataset `eefe77fe-ba8c-4d54-9341-97c327a47fd3` |
| Adaption generated-data workspace | Existing read-only API audits | 3 existing invented datasets; 3,500 rows total |
| PROOFBENCH dataset adapted on Adaption | **Completed** | 100/100 rows processed; provider quality C → A, summary +28.6% |
| Genuine model before/after experiment | **Not yet** | Requires baseline/candidate predictions; provider quality is not model accuracy |
| Human-reviewed independent blind holdout | **Not yet** | Must be collected separately |
| Hackathon submission | **Not yet** | Review/repair of enhanced rows, final evidence and model test still missing; closes Dec 6, 11:59 PM IST |

### Six scenario families

- FX conversion: supplied rate versus missing, dated conversion rate.
- Inventory: feasible stock counts versus impossible negative inventory.
- Receipts: two unique transactions versus a duplicated receipt ID.
- Interest: simple interest versus annual compounding.
- Profit: known delivery overhead versus missing overhead.
- Processing fees: per-item fee versus single flat fee.

Every scenario has two counterfactual variants, with independently computed decimal/integer oracles. Changing a single decisive condition changes the correct answer or whether an exact answer is justified.

## Independently checked original answer keys

The deterministic training generator emits **240 original source pairs**, 40 in each of six financial scenario families. A second [independent Decimal-based oracle](proofbench/oracle_recheck.py), deliberately separate from the generator's answer logic, re-derives all numeric results and missing-data abstentions; all **240/240 source keys** matched in the November 21 check. CI now fails if a release contains wrong arithmetic, duplicate prompts, malformed training columns or incomplete family coverage.

Run after generating the source:

```bash
python3 -m proofbench.benchmark --output generated
python3 -m proofbench.oracle_recheck --train generated/train.jsonl
```

The machine-readable result is packaged as `dataset/source_oracle_audit.json` in the Actions research bundle. **This validates synthetic original answers only**, not the correctness of all Adaption-rewritten outputs or any trained model. Read the [provider content audit](docs/POST_ADAPTATION_CONTENT_AUDIT.md) for observed adaptation errors.

## Reproduce locally

Python 3.10+, **no API key, network, GPU or paid credits required**:

```bash
python3 -m unittest discover -s tests -p 'test_proofbench_contract.py' -v
python3 -m unittest discover -s tests -p 'test_comparison.py' -v
python3 -m unittest discover -s tests -p 'test_adaption_bridge.py' -v
python3 -m unittest discover -s tests -p 'test_independent_audit.py' -v
python3 -m unittest discover -s tests -p 'test_adaption_estimate.py' -v
python3 -m unittest discover -s tests -p 'test_overlap.py' -v
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

## Verified Adaption 100-row pilot — November 21, 2026

The connected Adaption account confirms **100 out of 100 pilot rows succeeded**, with native quality grade **C → A**, provider headline score **7/10 → 9/10**, and reported **+28.6%** summary improvement. It separately reports prompt quality **7.07 → 8.11** and completion quality **5.87 → 9.84**. Raw precision differs (before 6.5; overall raw gain 38.72%); the provider reports both representations, not two independent trials.

The pre-launch quote was **1 credit**; **actual final credit usage has not been independently returned**. A **read-only SDK export of 100 enhanced rows** now exists in the [successful GitHub Actions review artifact](https://github.com/evansmusitu/Adaption_experiments/actions/runs/44938270782). Independent screening flagged **14/100 rows** (4 confirmed numeric/assumption defects and 10 negative-stock rubric mismatches); do **not** infer model accuracy from the native provider quality grade. See [the content audit](docs/POST_ADAPTATION_CONTENT_AUDIT.md), [provider assessment](docs/VERIFIED_ADAPTION_PILOT.md), and [machine-readable observation](evidence/adaption_pilot_observation.json).

## Corrected candidate: private review only

The original provider output is preserved unchanged, but independent review identified 14 flagged rows and one additional prompt-drift case. A separate research candidate therefore restores the exact original source prompt+completion for **15 rows** and retains the provider's output for **85 rows**. An offline, provider-free [candidate provenance verifier](proofbench/candidate_integrity.py) proves that all 100 rows come from one of those two sources and confirms their individual SHA-256 hashes. The [review protocol and hashes](docs/CANDIDATE_PROVENANCE.md) describe the evidence and how to rerun it.

**The corrected candidate is NOT an Adaption Grade A dataset**: the native quality score applies to the raw provider output only. No complete human review, independent model comparison or enhanced-output public redistribution clearance has yet been established. The original and enhanced JSONL files remain private review artifacts rather than committed to this public repository.

## Adaption integration and credit safety

GitHub Actions has successfully authenticated to Adaption via the `ADAPTION_API_KEY` secret, checked the three existing invented datasets, and retrieved native evaluation summaries.

The **manual-only** workflow `.github/workflows/proofbench-upload.yml` prepares an authenticated dataset upload from `generated/train.jsonl`. It requires the exact input `APPROVE PROOFBENCH DATA UPLOAD`, executes only on `main`, and has no adaptation/training calls. The upload changes the Adaption account; **do not repeat it after an uncertain outcome**. It is not a substitute for the separate credit-approved adaptation workflow.

The estimate-only workflow `.github/workflows/proofbench-estimate.yml` remains available for other, separately authorized new source IDs. The completed 100-row pilot was **quoted and launched once through Adaption MCP**; never rerun the source's adaptation to reproduce the observation. The workflow itself does not launch adaptation. The source import uses `processing_mode="adapt"` to prepare for the later adaptation call; the unchanged `train.jsonl` and its SHA-256 manifest in GitHub preserve the original control data. The import workflow itself does not call `datasets.adapt` or train a model. Verify 240 ingested rows and the quoted mapping before approving any credits.

The manual-only `proofbench-adaption-launch.yml` implements a fresh 100-row quote and explicit approval gate for up to 10 **estimated** credits using the exact same configuration as `proofbench-estimate.yml`. **Final provider usage may differ from quoted credits.** The runbook at [docs/ADAPTION_RUNBOOK.md](docs/ADAPTION_RUNBOOK.md) explains the import, compatibility and non-retry rules.

The pre-existing `adaption-launch-proofbench.yml` is a different credit-consuming Invent experiment. Do **not** launch it assuming it adapts this training file; Invent and Adapt are distinct Adaption workflows.

## Demonstration and cross-dataset audit

The mobile-friendly [offline interactive demo](demo/index.html) presents six real fixtures from the deterministic generator. It does **not** claim model improvement or show fake baseline results.

The authenticated overlap audit inspected 500 + 1,000 + 2,000 existing Invent rows, finding 3,500 unique normalized prompts, zero exact normalized duplicates within any dataset, and zero exact shared prompts between datasets. This is a strict text-level result only; it does **not** rule out paraphrase or numeric-template repetition. See the authenticated GitHub Actions run #44738341995.

## Research quality limitations

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
