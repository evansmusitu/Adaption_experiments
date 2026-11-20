# MUSITU PROOFBENCH — Adaption Competition Research Protocol

Status: **Research preparation, not a verified model-training result**. Date: 2026-11-20.

## Research question

Can verified quantitative examples with explicit unknown-input handling improve an AI model's numerical correctness and abstention behavior on realistic small-business financial questions, compared with otherwise similar synthetic training data?

## Existing Adaption workspace inventory

Read-only GitHub Actions audits authenticated to Adaption via `ADAPTION_API_KEY` and returned:

| Dataset | Kind | Rows | Native quality before → after | Native relative change | After percentile |
| --- | --- | ---: | ---: | ---: | ---: |
| #1 | Invented | 500 | 9.0 → 9.2 | +2.2% | 33.0 |
| #2 | Invented | 1,000 | 9.0 → 9.4 | +4.4% | 57.7 |
| #3 | Invented | 2,000 | 9.0 → 9.3 | +3.3% | 33.0 |

Dataset identifiers stay within the private-in-memory scripts, not embedded in published benchmark rows. The provider's quality scores reflect **dataset quality**, not external model accuracy.

The aggregate profiler inspected all 3,500 exported rows in memory; it printed only counters:

- #1: 318 finance-keyword prompts, 78 math/optimization prompts, 0 exact duplicate prompts
- #2: 727 finance, 296 math/optimization, 0 exact duplicate prompts
- #3: 1,693 finance, 933 math/optimization, 0 exact duplicate prompts

Keywords overlap, do not prove domain competence, and may miss equivalent terminology. No user data, individual dataset rows, or responses were retained in public CI logs.

## Candidate and controls

Use dataset #3 as the primary domain candidate and dataset #2 as a quality-score comparison. Do **not** treat either as proven training data: carry out sample-based human review, deterministic answer validation, rights checks and distribution analysis first.

After that review, define three arms:

1. **A — Baseline:** same base model, prompts and train/test split; train only on approved unaltered examples.
2. **B — Adaption:** apply a prespecified Adaption recipe to the same approved set, then train/evaluate identically.
3. **C — Adaption + verification:** retain only adapted rows that pass deterministic numeric and missing-input checks, then train/evaluate identically.

Keep model architecture, train steps, sample budget, inference settings, evaluation task mix, and seed constant across arms. Run repeated seeds if budget allows. A paired comparison with exact case-level predictions is required.

## Challenge tests

Create **at least 100 independent, human-authored or human-reviewed blind prompts**, not public and not templated from the training generator. Cover:

- Profit vs cash flow; gross/net margins; break-even quantities
- Duplicate payment identifiers and conflicting source records
- Stated vs unstated ZiG/USD exchange rates (never infer a live rate)
- Simple vs compound interest, with conditions and rounding
- NPV and cash-flow timing; bounded integer optimization
- Missing tax or fee rate; insufficient-input abstention

Include contrastive pairs differing in one necessary fact: rate absent/present, contradictory/consistent inventory, same/different payment IDs, etc.

Use exact Decimal-based oracles where possible. Separate categorical 'needs_clarification' from exact numeric answers. Avoid ambiguous prompts without a human adjudication protocol.

## Evaluation and reporting

- **Numeric accuracy:** proportion of numeric-answerable cases matching the oracle within a predeclared tolerance.
- **Abstention precision / recall:** correct behavior when essential inputs are missing.
- **Paired consistency:** both sides of each contrastive pair handled correctly.
- **Hallucinated-assumption rate:** fraction introducing an unstated exchange rate, tax rate or other invented fact.
- **Completeness:** number of valid output parses, failures and excluded examples.
- **Statistical reporting:** per-category counts, Wilson or bootstrap confidence intervals, paired significance only when appropriate.
- **Provider quality metrics:** separately report native grade, score, percentile and relative improvement; never conflate them with model accuracy.

Pre-register primary metric before viewing blind results. Audit exact and semantic duplicates between train and blind sets. Report failures, not only successes.

## Budget and external actions

- Adaption read-only auditing completed using GET requests; no credits spent.
- The API confirmed a 100-row **Invent estimate-only** request would cost approximately 10 promotional credits and that available credits could cover it.
- This quote **did not create or adapt any dataset**; no training job launched.
- Two attempts to estimate re-adaptation of an existing Invent dataset returned HTTP 400, including one with export-column mapping. Neither started a run.
- Do not retry credit-spending operations or reconfigure existing dataset mappings without verifying compatibility. Cost-estimate calls may persist mapping changes.
- Future runs require an exact cost quote, bounded `max_rows`, an idempotency key, no blind-data upload, and clear budget/approval.

## Publication and security

The repository is **public**. Do not publish API keys, business/customer source records, private AXIOM implementation, owner contact information or blind benchmark rows. Use fictional cases or properly licensed source material. Publish a data card, rights statement, reproducibility instructions, aggregate results and a truthful three-minute demo. Keep the blind test sealed until all model versions are frozen.

## Reproducibility evidence

- Authenticated read-only audit run: https://github.com/evansmusitu/Adaption_experiments/actions/runs/44709740361
- Native evaluation audit run: https://github.com/evansmusitu/Adaption_experiments/actions/runs/44709740361
- Aggregate dataset profile run: https://github.com/evansmusitu/Adaption_experiments/actions/runs/44710607185
- Confirmed 100-row Invent estimate: https://github.com/evansmusitu/Adaption_experiments/actions/runs/44711086080

Official documentation:
- https://docs.adaptionlabs.ai/api/resources/datasets/methods/list
- https://docs.adaptionlabs.ai/api/resources/datasets/methods/get_evaluation
- https://docs.adaptionlabs.ai/api/resources/datasets/methods/adapt
- https://docs.adaptionlabs.ai/adaptive-data/invent-a-dataset
