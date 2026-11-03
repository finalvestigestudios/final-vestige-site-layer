# R86 — Full 41-Document to Four-Snapshot Citation Bridge (PRIVATE DRAFT / HOLD)

**Issue #136. No merge, deployment, publication, source approvals, medical-safety verdicts, navigation changes, or WordPress/CMS writes.** This draft extends the R85 evidence custody chain, not the public website.

## Why this bridge exists

R80 preserves the complete release-candidate document reading room: **35 article drafts, six tool drafts, 244 separate full source readings, 2,173 citation occurrences, 2,359 origin-scoped source edges, and 4,070 unabridged DOM text blocks**. R85 separately preserves **29 contributor-authored articles and 1,768 current-to-release-candidate citation-rank comparisons** across frozen, integrated, current, and RC snapshots. Those are distinct scopes and should never be confused.

R86 adds a deterministic, **one-way review-only bridge**. It walks all R80 documents in original reading order. Every literal citation occurrence retains its original source-ID, distinct origin-scoped source variants, exact source URL and reading fingerprint. For the 29 historically reconstructed articles, it connects the occurrence's within-source-ID rank to the complete R85 changed-source/changed-claim review row, including unchanged citations. It explicitly preserves any historical comparison left unmatched (including removals) instead of hiding them. Six other articles and six tools remain clearly marked **outside the historical four-snapshot scope**, not incorrectly described as uncited or unsafe.

Cross-archive differences in literal source URL, origin, source reading, historical occurrence, or current claim context become **human-review cues**, not automatic source substitutions, evidence equivalence decisions, assertions of claim support, confirmed errors, or safety clearance. Even an empty review-cue list never means an article has been medically or factually approved.

## Release-candidate guardrails

The R86 module runs without network calls or write functions. It separately reconstructs and verifies the existing R79/R80 complete-slate evidence and R82–R85 historical provenance evidence; each of those parents already checks its own original content and hold statuses. R86 verifies exact originals again, rejects forged release and approval fields, enforces all complete-slate cardinalities, and fails closed if one of the 29 historical authored slugs cannot be found in the 35-article RC. No original content, taxonomies, safety states, URLs, source registers, or historical research is edited.

The optional private CSV contains only identifiers, ordinals, review-cue names and explicit NOT_REVIEWED states. It is **never an approval intake**, website asset, GitHub attachment, publishing queue or email export. Its job is to direct a qualified human reviewer to the original sealed evidence. Any CSV created in CI must be under the private runner temp directory and removed.

## Exact coordination refs checked 2026-11-02 (Pacific)

- Start: `claude/prep-start-bbfeb8` → `2122d856fce9f64887c16df3d52e64be9f59a55b`.
- Shelter: `claude/prep-shelter-5e1e0e` → `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`.
- Food: `claude/prep-food-ccdc55` → `f911ff7a655de8d81535ea86ec3d65a49ee76648`.
- Health: `claude/prep-health-837444` → `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`.
- Historical food: `claude/prep-hist-food-b81f19` → `67e116e536c7410bed30f8f3b1bb8c166f3c223d`.
- Historical home: `claude/prep-hist-home-0e0e38` → `7504a5f099594d635e3dd7332a33a2e1346c43a2`.
- Historical field: `claude/prep-hist-field-9db767` → `4e5caf812727953aa45e3bda2d382f2c67b6a09c`.
- Preparedness RC #584: `ddb3528ba6494dada1fa1c3a142ce746e3a67706` (draft HOLD).
- QA #157: `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (draft unmerged).
- Synthetic-fixture QA #169: `e9cd7766dac59d47ab467d8945269b9146c2aef5` (draft unmerged); its remaining `_dup_test.json` test still mutates the shared source fragments directory; not isolated or signed off by R86.
- Home PR #49: `10495883299d53596992c26a8987f629b2904670`; flagship PR #604: `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`. Neither touched.
- Separate integration repair branch `integration/preparedness-custody-repair-20261103` → `30101ba5e96a2b814ed7919a0f6d0c7bf0704f4b`, inspected for coordination but not incorporated without independent QA.
- R85 immutable parent: `7f29bedb594ec6690a445d59b239914c16013926`.

## Required diagnostics for this exact PR head

The private workflow rejects any R85-base mismatch or a change outside **four strictly added files**. It compiles source/test Python, runs the R86 synthetic and adversarial suite, verifies all seven pinned contributor origins and the RC against Git, reconstructs the full joint crosswalk, checks a temporary metadata-only review CSV, and then separately runs original `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, and the complete original `python -I -m unittest discover -s preparedness/tests -v` regression suite.

These are **engineering diagnostics only**. They do not waive or replace the independent mandatory 13-stage release integrity, historical five-branch parity gate, qualified source and emergency-guidance reviews, 15 outstanding safety exceptions, 22 editorial decisions, live-link and shared-URL decisions, real WordPress/browser/accessibility QA, independent QD PASS, or founder authorization. An Actions run that has not completed at the final HEAD is **NOT A PASS**.

**Permanent status: HOLD, may_publish=false, medical_safety_approved=false, human review/qualified safety/QD approvals all zero.**
