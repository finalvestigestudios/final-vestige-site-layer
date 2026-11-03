# R90 — Historical claim-scope and quantity-sequence safety-review gate — PRIVATE HOLD

**Issue #136** · branch \`review/preparedness-r90-claim-scope-quantity-sequence-hold-20261103\` · immutable R89 base \`182b6ee5ce6ee620557eace324f5b4a968a21dce\` · **NOT a publication candidate.**

## Why this review gate matters

R89 preserves complete original claim blocks, historical before/after containers, literal URLs and every origin-scoped source variant. Its qualifier review identifies additions/removals of words such as *never*, *unless*, and *not*. It cannot always detect **unchanged words moved to different instructions**. Likewise, unchanged source IDs and reused citations cannot prove that revised quantities, ranges, conditions or units remain supported.

R90 adds a conservative, deterministic **historical before/after reviewer queue**. It tracks ordered quantities and units, positive/negative qualifiers and modal language, complete relevant clause context with SHA-256 receipts, literal inline citation-token sequences, and literal link sequences. It detects review candidates where quantities change or move, qualifiers change order or shift to a different sentence while retaining the same vocabulary, citations move, or source links change. All are **textual review cues only**, not medical, food-preservation, water-treatment or other safety verdicts.

R90 independently checks the unabridged original DOM blocks, full citation identity/rank, 41-document census, 2,173 citation occurrences, 2,359 source edges and all distinct source-variant reverse-impact dossiers. It retains the **entire immutable R89 parent**, including earlier R88/R87/R86/R80 records and all 11 unmatched historical reviews. The 244 complete original source readings are carried upstream; R90 does not replace or truncate them.

All source citations, original URLs, reading depth, safety gates and original routes are untouched. No automatic URL normalization, source substitution, changed dosage recommendation, source verification, human review approval, QD PASS or release-state transition is permitted. Numeric and lexical differences must never be called factual errors or evidence of safety without external expert review.

## Reviewer handoff

The output's \`all_original_citation_claim_scope_review_rows_NOT_APPROVED\` is indexed by original \`(kind, slug, citation_ordinal)\`. Each row retains the original block SHA and exact distinct source-variant keys and contains the comparison's complete relevant clauses, ordered quantities/units, qualifier-token sequences, citation/link sequences and evidence hashes. Every comparison has explicit \`human_claim_support=NOT_REVIEWED\`, \`qualified_safety_review=NOT_REVIEWED\`, \`independent_QD_review=NOT_REVIEWED\`, \`may_publish=false\`.

Use these records to direct human source/claim reviewers back to the fully preserved R89 dossier. Do not import edited CSVs as approvals. The optional \`--private-csv-stdout\` export contains **only metadata**, is spreadsheet-formula quarantined, and must be redirected to private short-lived runner temp files, never published or uploaded.

## Commands (trusted exact checkout; offline)

\`\`\`bash
python -I preparedness/tools/r90_historical_claim_scope_quantity_sequence.py
python -I -m unittest discover -s preparedness/tests -p test_r90_historical_claim_scope_quantity_sequence.py -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
\`\`\`

These are diagnostics, **NOT** the mandatory 13-stage release-integrity workflow and **NOT** independent QD or qualified health/emergency safety review.

## Coordination and blocking gates

Check actual current refs and SHA before acting: all seven Claude contributor clusters, RC \`integration/preparedness-release-candidate-20261101\`, independent QA #157, synthetic-fixture QA #169, custody-repair and Hastings correction refs, homepage #49 and flagship #604. Independent QA #157 remains isolated. #169 still writes one temporary \`sources/fragments/_dup_test.json\` in the shared worktree and must be fixed independently before its merge. Do not edit or merge either QA PR as part of R90.

Five contributor heads differ from frozen historical baselines (explicit provenance disposition required), 30 source-URL collision groups, 15 safety exceptions, 22 editorial decisions, actual outbound source/claim checks, qualified emergency-guidance assessment, rendered WordPress accessibility/browser QA, mandatory 13-stage integrity pass, independent QD PASS and founder-specific publication authorization remain outstanding.

**HARD HOLD**: Draft PR only; no merges, public publishing, WordPress/CMS writes, navigation changes, homepage changes, or claims of medically safe unreviewed advice.
