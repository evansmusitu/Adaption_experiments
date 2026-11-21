# PROOFBENCH: independently verifiable post-adaptation repair candidate

**Status: provenance audited; NOT expert-approved, publicly licensed, provider-graded or model-benchmarked.**

This document records the review-only **local** correction to Adaption dataset
eefe77fe-ba8c-4d54-9341-97c327a47fd3 (100-row adaptation run
dataset-eefe77fe-ba8c-4d54-9341-97c327a47fd3-1795285525492).
Its 7/10 → 9/10 provider quality improvement belongs **only to the untouched
Adaption-enhanced output**, not this repaired candidate.

## Composition and immutable source

The verified review ZIP contains three distinct 100-row files:
- original.jsonl: actual unchanged source prompt/completion pairs.
- raw_adaption_improved.jsonl: actual untouched provider pairs, not certified.
- oracle_restored_candidate.jsonl: 85 byte-for-byte provider rows and 15 exact
  original source pairs where the provider output needed review/restoration.

The restored zero-based indexes are: 7, 10, 13, 26, 38, 44, 45, 48, 61, 76,
81, 83, 95, 96, 99. Index 45 is a prompt drift discovered beyond the
14 originally flagged cases. All three files are **kept out of the public
repository** pending rights, privacy and expert accuracy review.

SHA-256 values verified for the existing artifact:
- Original export: 46f3ddb18efa5869b8dcd0b01839d1056397b3f14f690779c2faa1562a2a0c6b
- Raw provider output: 7127b6f681392ed43e63093ec371254c486c4e442f62d918d20944669dbeadb1
- Oracle-restored candidate: c84938d5febad9131c0dba3a2fa6938f5f56abce7e3009f8d3ee56e01a3dbc0a

For the exact source, see the public reproducible dataset/train.jsonl release.
The review ZIP includes a candidate_manifest.json with these same checksums.

## Independently rerun static provenance verification (no API or credits)

From the root of a cloned repository, place your **private** review artifacts in
a folder named review_only (never stage that folder in a public git commit), then:

    python3 -m proofbench.candidate_integrity \
      --review review_only \
      --training dataset/train.jsonl

This checks every row against the 240-row training release, the 15 authorized
restoration positions, all three SHA-256 hashes, and the declared quality
and expert-review limitations. The tool will fail closed when tampered with.
It intentionally does not certify the quality or copyright status of the
remaining 85 provider replies.

An additional private offline HTML reviewer desk was generated in the local
conversation artifact, NOT committed publicly. It presents all three versions
side-by-side, records human decisions, and exports a separate review JSON/CSV.

## Submission readiness

The challenge requires original and improved datasets, before/after evaluation,
README, demo, and the source licence/provenance. The provider-native C→A result
is genuine, but it is not an external model score; 4 obvious provider defects,
10 negative-stock rubric mismatches and one additional prompt drift have been
preserved in the review history rather than hidden.

Before publishing a final entry:
1. Complete detailed correctness, safety and privacy review of all 100 rows.
2. Verify Adaption's applicable reuse/public redistribution permissions for
   the improved outputs; CC0 for original synthetic data is not automatic.
3. Decide transparently whether submitting untouched Adaption output with
   flaws disclosed, or a derived correction candidate without claiming its
   provider quality grade; preserve both versions for audit.
4. Prepare a public demo using validated examples; add independent model
   predictions only if genuinely measured.
5. Finish the evidence manifest and final submission once, retaining a receipt.

**This step executed no Adaption training, adaptation or credit-consuming call.**
