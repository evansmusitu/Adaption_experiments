# MUSITU PROOFBENCH — Verifiable AI for Quantitative Business Decisions

**Adaption AI Dataset Challenge · 2026**  
**Status:** Experimental infrastructure and reproducible development evaluator implemented. **No trained-model improvement or hackathon submission claimed.**

## Research question

Can training-data adaptation plus independent numerical verification improve model accuracy and appropriate abstention on small-business financial problems, versus synthetic data quality improvements alone?

The target applications include realistic Zimbabwean business finance, cash-flow questions, inventory reconciliation, missing currency conversion rates, duplicate receipts and numerical optimization. We use synthetic data and never infer live foreign-exchange rates.

## Evidence collected remotely

GitHub Actions uses the official Adaption API with `ADAPTION_API_KEY` stored in GitHub Actions Secrets. Individual proprietary data rows and raw API responses are **not** logged.

| Adaption dataset | Origin | Rows | Native score before → after | Native improvement |
| --- | --- | ---: | ---: | ---: |
| #1 | Invented | 500 | 9.0 → 9.2 | 2.2% |
| #2 | Invented | 1,000 | 9.0 → 9.4 | 4.4% |
| #3 | Invented | 2,000 | 9.0 → 9.3 | 3.3% |

These are **Adaption dataset quality metrics, not model accuracy**. All three exported prompt sets were inspected in memory for narrow lexical topic coverage and exact duplicates. Results and limitations: [research protocol](docs/experiment_protocol.md).

## Reproducible development evaluation

The public benchmark generator is deterministic and uses Python's `Decimal` arithmetic. It covers 100 development examples across five task families: profit, missing FX rate, explicit FX rate, duplicate receipts, and simple interest. Twenty missing/present exchange-rate pairs are tested for paired correctness.

Run locally:

```bash
python3 evaluation/proofbench_dev.py --self-test
python3 evaluation/proofbench_dev.py --write data/dev_cases.jsonl
python3 evaluation/proofbench_dev.py --predictions model_predictions.jsonl
```

Prediction JSONL records require an `id`, numeric `prediction_value` (or `null`), and `needs_clarification` boolean. The scorer requires exactly one prediction per case and reports exact numerical correctness (within USD 0.01), missing-input precision/recall and both-correct counterfactual pairs.

**This benchmark is template-generated and is for development only.** A true blind, independently phrased benchmark must be held back before generalization claims. An oracle self-test is not a model evaluation.

## Remote control

- `.github/workflows/adaption-audit.yml`: authenticated GET-only listing, metadata, export-header check and official evaluation metrics.
- `.github/workflows/adaption-profile.yml`: in-memory analysis of three approved datasets with aggregate-only output.
- `.github/workflows/adaption-estimate.yml`: official Invent `estimate=true` request for a hypothetical 100-row dataset, with **no generation or credit charge**.
- `.github/workflows/proofbench-tests.yml`: syntax checks and scorer/generator regression verification, no Adaption key required.

**Verified quote:** a new 100-row Invent pilot would require 10 promotional credits; account credits cover this amount. No new dataset has been created from that quote. Cost estimates for re-adapting already invented datasets failed HTTP 400; do not launch that pathway until its preconditions have been investigated.

## Next research gates

1. Human review and validate a sample of the 2,000-row candidate's mathematical ground truth; compare against the 1,000-row candidate.
2. Create a sealed, human-authored blind evaluation set with disjoint scenarios.
3. Identify or import a valid source dataset for an Adaption transformation; request an exact estimate before processing.
4. Compare baseline, Adaption-only, and verification-filtered arms under the same model/training/evaluation conditions.
5. Publish the data card, license, honest ablation results, and a three-minute demonstration.

## Security and reproducibility

Public repository: **never commit API keys, customer financial records, private AXIOM source, confidential prompts, or blind benchmark answers.** Adaption API keys belong in the `ADAPTION_API_KEY` repository secret, only for trusted workflows. Credit-consuming launches require their own guarded workflow and an approved limit.

## Verified workflow records

- [Adaption authentication and dataset inventory](https://github.com/evansmusitu/Adaption_experiments/actions/runs/44697656462)
- [Native Adaption quality scores](https://github.com/evansmusitu/Adaption_experiments/actions/runs/44709740361)
- [Corrected aggregate domain profile](https://github.com/evansmusitu/Adaption_experiments/actions/runs/44710607185)
- [Official 100-row, estimate-only credit quote](https://github.com/evansmusitu/Adaption_experiments/actions/runs/44711086080)
- [PROOFBENCH benchmark tests](https://github.com/evansmusitu/Adaption_experiments/actions/runs/44711695445)

Official API docs: https://docs.adaptionlabs.ai/
