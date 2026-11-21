# PROOFBENCH — real Adaption export and adversarial content audit

**Observed:** November 21, 2026. This document reports genuine exported rows and negative findings; it does **not** certify model accuracy or guarantee that every enhanced answer is mathematically valid.

- Dataset: `eefe77fe-ba8c-4d54-9341-97c327a47fd3`
- Run: `dataset-eefe77fe-ba8c-4d54-9341-97c327a47fd3-1795285525492`
- [Verified read-only export workflow](https://github.com/evansmusitu/Adaption_experiments/actions/runs/44938270782)
- Review-only Actions artifact: `proofbench-adaption-review-only` (original.jsonl, improved.jsonl, review_manifest.json), retained temporarily by GitHub Actions; **the improved file is not yet approved for publication in this repository**.
- 100 enhanced rows verified; each source prompt+answer matched the deterministic 240-row original training release.
- Original 100-row SHA-256: `46f3ddb18efa5869b8dcd0b01839d1056397b3f14f690779c2faa1562a2a0c6b`.
- Improved 100-row SHA-256: `7127b6f681392ed43e63093ec371254c486c4e442f62d918d20944669dbeadb1`.

## What the provider evaluation really measures

Adaption reported **native dataset quality grade C → A**, rounded provider score **7/10 → 9/10**, and provider summary **+28.6%**. Finer-grain reported quality scores were message 7.07 → 8.11 and completion 5.87 → 9.84. The separate raw evaluator reports a before quality of 6.5 and overall gain of 38.72% due to differing precision/representations. **None of these are trained-model accuracy results.**

## Independent screen of all 100 downloaded enhanced answers

| Result | Count | Interpretation |
|---|---:|---|
| Numerically scored scenarios | 72 | 70 contain the expected source value near the final portion of the enhanced answer; this is a **screen**, not a correctness certification |
| Scenarios demanding clarification/reconciliation | 28 | Strict scenario-level abstention criteria apply |
| **Unambiguously wrong numbers or unsupported assumptions** | **4** | Cases 7, 48, 95, 96 (zero-based indices) |
| **Negative stock presented as final stock** | **10** | Cases 10, 13, 26, 38, 44, 61, 76, 81, 83, 99; rubric conflicts, even when discrepancy is noted |
| **Total distinct cases flagged** | **14/100** | All remaining answers still need full expert/human review |

### Four confirmed defects

1. **Case 7 — invented delivery expense:** The original asks for net profit after delivery, but delivery costs are unknown. The enhanced prompt adds a zero-cost assumption and the answer uses **USD 0.00** to assert USD 819.42 instead of abstaining.
2. **Case 48 — incorrect rounding:** 5,365 ZiG ÷ 32.17 ZiG per USD ≈ **166.770282… USD**, which rounds to **166.77 USD**. Enhanced answer reports **166.76 USD**.
3. **Case 95 — invented delivery expense:** The rewritten prompt authorizes treating unknown delivery expense as zero; the enhanced answer subtracts USD 0 and calls USD 890.53 its provisional calculated profit, despite admitting actual net profit is unknown.
4. **Case 96 — duplicated receipt counted twice:** Opening USD 511 + legitimate USD 100 receipt − USD 19 payment = **USD 592**. Two lines share the same receipt ID R1. Enhanced answer counts both and reports **USD 692**.

### Rewritten-prompt integrity

The original numeric tokens remain represented in all 100 rewritten questions, but this **does not establish semantic equivalence**. For example, rephrased prompts at indices 7, 45 and 95 introduce a delivery-cost-zero hypothetical not present in the source. Only indices 7 and 95 use it as an unwarranted final-profit computation.

## Submission and safety gates

- Keep the untouched Adaption export and provenance. A corrected version would be a **separately labeled derived artifact**, not the raw provider output.
- **Do not publish these 100 enhanced rows as verified financial advice or as a 100% accurate dataset.**
- Before public release, complete arithmetic, missing-information abstention, rewritten-prompt semantics, copyright/rights and privacy reviews; preserve failures and corrective test cases.
- Source code and dataset license rights remain separate. CC0 status of our synthetic original does not automatically apply to provider outputs.
- Real baseline/candidate model predictions and paired statistical comparison are still **not done**.
- The static `evidence/manifest.json` submission gate remains intentionally closed until exported evidence is reviewed, relocated and hashed with accurate provenance. The direct read-only download provided files, but **does not prove that a separate output dataset ID exists**.
- The original pilot was authorized for a 1-credit estimate; **actual final billed credits remain unverified**. No further paid Adaption run is authorized by this audit.
