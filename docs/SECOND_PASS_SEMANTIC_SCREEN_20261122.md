# PROOFBENCH — second-pass semantic screen (November 22, 2026)

**Status:** A private, rule-based review aid. NOT a complete correctness audit, expert attestation, licensing clearance, trained-model evaluation or release approval.

## Authentic provider and source provenance

The underlying native Adaptive Data pilot, dataset `eefe77fe-ba8c-4d54-9341-97c327a47fd3`, processed 100/100 selected rows. Provider run: `dataset-eefe77fe-ba8c-4d54-9341-97c327a47fd3-1795285525492`.

The complete original, raw-enhanced and repaired JSONL datasets are retained separately in the private review package; **none are added to this public repository by this report**. Checksums:
- Original 100-row export: `46f3ddb18efa5869b8dcd0b01839d1056397b3f14f690779c2faa1562a2a0c6b`
- Untouched raw Adaption output: `7127b6f681392ed43e63093ec371254c486c4e442f62d918d20944669dbeadb1`
- Derived oracle-restored candidate: `c84938d5febad9131c0dba3a2fa6938f5f56abce7e3009f8d3ee56e01a3dbc0a`

The source 240-row training set was independently rechecked with Decimal arithmetic in [`proofbench/oracle_recheck.py`](../proofbench/oracle_recheck.py). That source check establishes neither the adapted-data accuracy nor any model improvement.

## Targeted content check

A second offline program inspected **100/100 original/enhanced/candidate rows** against the known source values and conditions, including 72 numeric source answers and 28 cases requiring clarification or reconciliation. It inspected final-answer numeric presence, input-value preservation, fee basis, receipts, interest, missing costs and exchange rates, and candidate provenance. This check incorporates previously documented manual findings; it is **not a blind independent replication**.

| Version | Targeted review flags | Interpretation |
|---|---:|---|
| Raw Adaption output | **15 distinct cases** | 14 original audit issues plus one extra rewritten-prompt drift |
| Separate 85/15 correction candidate | **0 targeted rule alerts** | Does **not** mean certified accurate; 85 provider records are retained unchanged and 15 original oracle pairs restored |
| Independent human review | **0 of 100 cases signed off** | Remains open |

Flagged original provider cases, **one-based**:
- Clear numeric or unsupported-assumption defects: #8, #49, #96, #97.
- Negative-stock final-result/reconciliation rubric conflicts: #11, #14, #27, #39, #45, #62, #77, #82, #84, #100.
- Rephrased-prompt drift introducing unauthorized zero-delivery hypothetical: #46.

The raw output's Adaption-native grade **C→A**, rounded score **7/10→9/10** and summary **+28.6%** belong exclusively to the **raw provider dataset**, **not** the oracle-restored derivative or a trained AI model. See [native pilot evidence](VERIFIED_ADAPTION_PILOT.md), [original content audit](POST_ADAPTATION_CONTENT_AUDIT.md), and [candidate provenance](CANDIDATE_PROVENANCE.md).

## What remains blocked

1. **Expert review of all 100 pairs:** The private, owner-only Google Sheet stores case classifications and reviewer statuses; no fictitious human verdicts are recorded.
2. **Rights to redistribute generated text:** Synthetic source data are CC0-1.0, but those rights cannot automatically be imputed to provider-generated output. An Adaption permissions inquiry has been prepared, but a written answer has not yet been received.
3. **Public release and final evidence:** Preserve the genuine raw export and disclose failures. Do not publish it as certified financial advice or misattribute the provider-native grade to the derived candidate.
4. **Account verification:** Attach a genuine Adaption account screenshot to the separate Hackyard verification PDF and submit it once.
5. **Challenge submission:** One final link containing permitted original/improved data, before/after evaluation, README and demo; save a single verified submission receipt.

A private offline rerunnable screening script, seven contract tests and a case-by-case JSON decision aid are available in the current ChatGPT review bundle. **No additional Adaption run or credits were used** for this audit.
