# R89 — Complete claim-block / exact source-variant human-review dossiers — PRIVATE HOLD

Issue #136. Base: draft R88 PR #740 at immutable commit a397024314e04af86401aa3499d23c387a5f01e5.

## Integration lift

The R88 reviewer queue connects every citation and literal source-variant identity, but the flat review export does not contain complete cited claim passages. R89 creates a second evidence-preserving, deterministic review view:

1. A packet for every original draft document, preserving all complete DOM blocks, including uncited blocks, exact text, original reading order and citation ordinals.
2. One complete claim-context row per original citation ordinal, preserving unabridged original DOM block text and SHA-256, literal source ID, all separate source-variant keys, and full historical before/after claim-container context where available.
3. A reverse-impact dossier for every origin-scoped exact source variant (origin, literal ID, complete-reading SHA-256, literal URL) with every citation use and complete associated claim passage. Same URL is not source equivalence, and citation reuse is not claim support.
4. Lexical triage for added/removed caution words (including never, not, unless) across historical before/after containers; missing literal citation-token visibility; and number/quantity-bearing cited passages. Matching words cannot establish modern medical safety, veracity, or equivalence of differently worded claims.
5. A conservative private route collision gate identifies case, percent-decoding and Unicode collision candidates, without rewriting or publishing URLs. A duplicate private destination fails closed.

Every source relationship is verified independently from R88 and complete original passages. Parent R88/R87/R86/R80 evidence remains unabridged by reference, including the 244 source readings, seven contributor clusters, 35 article drafts plus six tools, and 11 unmatched historical reviews. No source citation or safety state is upgraded.

## Mandatory safety HOLD

All source review, human claim-support validation, qualified medical/emergency review, independent QD, live WordPress/browser accessibility QA and founder publication authorization remain outstanding. R89 neither link-checks URLs nor asserts source reliability. Lexical flags are review cues, NOT assessments that advice is safe, unsafe, supported or factually wrong.

## Private execution

From repository root run:

1. python -I preparedness/tools/r89_full_claim_block_source_dossiers.py
2. python -I -m unittest discover -s preparedness/tests -p test_r89_full_claim_block_source_dossiers.py -v
3. python -I preparedness/tools/validate.py
4. python -I preparedness/tools/build.py (offline WordPress-ready PRIVATE drafts)
5. python -I -m unittest discover -s preparedness/tests -v

Optional private reviewer exports: --private-csv-stdout (formula-quarantined metadata only), or --private-jsonl-stdout (complete original passage contexts; never put in public logs). Redirect exports to runner-private temp storage and delete them immediately. Neither format is an approval intake.

This draft PR workflow is diagnostic-only. The separate mandatory 13-stage release-integrity workflow must pass independently.

## Exact-ref coordination and noninterference

Independent QA PR #157 was inspected at 7d1ae6b8ef93d10cfb6810987672360885e9c1aa (Start Here safety wording; draft). Synthetic-fixture PR #169 was inspected at e9cd7766dac59d47ab467d8945269b9146c2aef5 (draft): its remaining test_register_fragments_cannot_duplicate_ids still writes sources/fragments/_dup_test.json into the shared worktree. Owner should isolate that test before integration. Seven Claude contributor refs and separate RC pinned by workflow; five historical contributor parity differences remain unresolved. Homepage PR #49 at 10495883299d53596992c26a8987f629b2904670 and flagship PR #604 at bdf01b4a3e13fd6179ae9e847c9d4429bbe16176 remain untouched.

Previously identified independent blockers include 30 source URL collision groups awaiting human source-scope verification, 15 safety exceptions, 22 editorial decisions, qualified emergency-guidance review, original claim/source/link verification, live browser/assistive tech QA, independent QD and founder authorization. Never treat stale counts as a fresh safety verdict.

NO merges, CMS/WordPress writes, public navigation, public publishing, manufactured QD PASS or unreviewed medical-safety declarations.
