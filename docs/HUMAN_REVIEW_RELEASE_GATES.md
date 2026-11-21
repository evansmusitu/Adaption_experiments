# Private review-to-submission handoff (no automatic publication)

The 100-row Adaption pilot succeeded, but its raw enhanced dataset had 14
flagged outputs. A separate private candidate kept 85 provider answers and
restored 15 unchanged original answers, including one additional prompt drift.
Neither the provider grade nor the source oracle certifies the corrected
candidate, and the untouched raw provider export must remain available.

The private offline HTML reviewer dashboard ships in the conversation's review
ZIP, NOT in this public GitHub repository. It displays all 100
original/provider/candidate comparisons. Mark each case approved or needs_fix,
and click Export review JSON to create proofbench_human_review.json.

To check the exported decisions offline, unpack the private review ZIP
containing candidate_manifest.json, then run:

    python3 -m proofbench.reviewer_preflight \
      --review-decisions /path/to/proofbench_human_review.json \
      --candidate-manifest /path/to/candidate_manifest.json

The checker requires exactly one decision for every case 1–100, matching hashes
and source classification. Status is *structurally complete* only when all 100
decisions are approved. Unreviewed and needs_fix decisions fail the preflight;
changed digests, duplicate case numbers and incorrectly labelled restored rows
are rejected.

**Even a complete decision export does NOT clear data for publication.**
The dashboard is a local, unauthenticated reviewer tool; its JSON can be
edited. A human must independently assess the rows and reviewer identity. The
rights to redistribute Adaption-generated text are not yet confirmed; source
CC0 status alone is insufficient. Public release requires a separate verified
rights decision and explicit owner approval.

Final gates: all input hashes independently checked; all 100 candidate rows
reviewed for arithmetic, missing information, semantics, safety and
hallucinations; documented redistribution clearance; raw provider output kept
unaltered; native C-to-A provider grade attributed ONLY to that raw output;
real dataset links and demo confirmed; team account screenshot PDF uploaded
to the SEPARATE verification form; one final submission with receipt.

No adaptation, training, publishing or API operation is executed by preflight.
