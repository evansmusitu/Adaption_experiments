# Adaption pilot operator runbook

**State:** Workflow prepared; no PROOFBENCH dataset import/adaptation launch is claimed by this document.

This project separates **dataset import**, **cost quotation**, and **credit-consuming adaptation**. Do not confuse an initial Adaption Invent experiment with improving this verified training seed.

## Prerequisites

- Authorized GitHub repository: `evansmusitu/Adaption_experiments`.
- Repository Actions secret `ADAPTION_API_KEY` already verified through the read-only audit. Never paste it in Issues, ChatGPT messages, logs, or source code.
- A clean release of the deterministic `generated/train.jsonl` source data with matching `manifest.json` SHA-256.
- All main-branch CI checks pass.
- Only the owner may authorize an upload or credit-consuming run.

## Step 1 — Create unadapted control on Adaption (manual)

Run [Import PROOFBENCH 240-row training data](../.github/workflows/proofbench-upload.yml) from the **main** branch, with exact input:

```text
APPROVE PROOFBENCH DATA UPLOAD
```

The SDK uses `processing_mode="raw"` and `column_mapping={"prompt":"prompt","completion":"completion"}`. This is an upload operation, **not** a model-training or adaptation launch. Record the resulting dataset UUID and verify the returned dataset row count in Adaption.

**Do not repeat a failed/uncertain upload before checking the Adaption account for an already-created dataset.** File upload may not be idempotent.

## Step 2 — Quote a 100-row financial adaptation (manual, estimate only)

Open [Quote PROOFBENCH adaptation](../.github/workflows/proofbench-estimate.yml), choose `main`, and enter the new PROOFBENCH dataset UUID. The quote uses:
- Source columns: `prompt` and `completion`
- Maximum 100 rows
- Explicitly fixed prompt rephrasing/deduplication, **no reasoning-traces generation**
- A domain blueprint against invented exchange rates, fees and transaction details
- A fixed client idempotency key tied to this new dataset UUID

The action uses `estimate=True`. As documented by Adaption, estimating may **save the submitted column mapping** on the dataset but does not launch a run or reserve adaptation credits.

The standalone estimate can return a price higher than 10 credits; do not launch in that case. The separate guarded-launch script repeats the quote immediately before any start, with the **same exact configuration**, and aborts above 10 estimated credits.

**Important platform compatibility gate:** The uploaded `raw` dataset may already be marked processed and Adaption could reject an adaptation of that dataset with HTTP 400. If the quote fails, do **not** launch and do not keep retrying. We must first verify with Adaption whether a separate adaptation-ready import is required. The current scripts do not assume raw-to-adapt conversion is supported.

## Step 3 — Launch only with explicit approval (optional, credit-consuming)

After a successful estimate and source-dataset compatibility check, the owner may use [PROOFBENCH credit-capped adaptation](../.github/workflows/proofbench-adaption-launch.yml) on `main`.

Inputs:
- `dataset_id`: exact new imported PROOFBENCH UUID
- `approval`:

```text
I APPROVE UP TO 10 ADAPTION CREDITS
```

The script first validates the approval, branch and dataset identifier. It obtains an updated estimate, aborts if it is missing or exceeds **10 estimated credits**, then issues exactly **one** Adaption adaptation request with a fixed idempotency key.

**The 10-credit guard applies to the estimate, not a guaranteed upper bound on final provider charges.** Adaption notes usage may vary from the quote. Owner must accept that residual risk before launching. If network outcome is uncertain, do not submit a second request until checking Adaption's run history.

## Step 4 — Preserve evidence

After a genuine Adaption run finishes:
- Record dataset UUID, run ID, configuration, actual credits, completion status and timestamp.
- Export **original and improved** datasets; compute SHA-256 hashes.
- Retrieve the Adaption-native `score_before`, `score_after`, `improvement_percent` and status. Never conflate them with model benchmark accuracy.
- If evaluating model performance, retain raw model generations plus exactly one structured prediction per test ID, then use `proofbench.comparison`.
- Fill `evidence/manifest.json` only with **genuine** provider values. The static submission-gate checker must pass; then verify the source values manually against Adaption.
- Publish the demo and limitations honestly.

## Step 5 — Deadline

Official Adaption Dataset Challenge submission deadline: **December 6, 2026, 11:59 PM India Standard Time (8:29 PM Zimbabwe)**. Use one approved submission platform and separately complete team account verification. Model training remains optional under the current main event instructions.

## Current unresolved gates

1. PR for guarded workflow must be merged into `main`.
2. Original 240-row seed has not yet been confirmed imported into Adaption.
3. Provider raw-to-adaptation compatibility is not yet known.
4. No real PROOFBENCH adaptation cost or completion evidence exists.
5. No human-blind evaluation or genuine trained-model improvement is established.

### Authoritative references

- https://docs.adaptionlabs.ai/adaptive-data/create-a-dataset/
- https://docs.adaptionlabs.ai/autoscientist/run-on-non-adapted-data
- https://docs.adaptionlabs.ai/api/python/resources/datasets/methods/adapt/
- https://hackyard.org/events/adaption-labs
