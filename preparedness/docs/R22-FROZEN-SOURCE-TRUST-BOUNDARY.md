# R22 — Frozen Source Trust Boundary (Issue #136)

**Status: DRAFT / RELEASE HOLD.** This is machine provenance control, **not** independent source verification, consequential-emergency/medical approval, publication authority, or QD PASS.

## Previously unclosed failure mode

R21's structural audit compared each physical source file with a Git blob SHA *stored in the same mutable crosswalk*. A coordinated edit to the crosswalk and its source inventory could preserve counts (224 rows, 186 distinct literal URLs, 30 shared groups, 15 repeated IDs) while changing evidence. Likewise, a contributor head other than food or an article's original contributor attribution could be rewritten without a standalone R21 rejection.

R22 makes `preparedness/tools/source_group_review_gate.py`'s **native CLI** refuse any change to ten independently frozen Git-object identities: the crosswalk, 35-item taxonomy (including its 36 article/tool source origins, publication safety booleans and URLs), baseline register, and seven original contributor fragments. It also checks the original eight contributor/base commit identities; the food source-head alias to the separate synthetic-fixture PR #169 is explicitly allowed only as **unresolved provenance**, never as proof of independent author review.

The 224-row / 30-group R21 structural analysis still runs *after* the ten immutable SHA assertions. Results always say `HOLD`, `may_publish=false`, `independent_qd_pass=false`, `medical_safety_approved=false`, `human_source_review_complete=false`.

If an editor legitimately updates a source record, taxonomy gate, original reading-scope note, or contributor attribution, the existing reviewed fingerprints must be deliberately re-established with a new independently reviewed evidence record. R22 does not auto-rewrite sources to make them pass.

## Confirmed actual data on 2026-10-31

Authenticated GitHub fetches at R22 code HEAD independently verified **10/10 frozen Git blobs** and saw 35 taxonomy rows, 30 source-review groups, and 224 source rows across eight original inventories (34 + 27 + 31 + 30 + 21 + 28 + 27 + 26). All seven Claude contributor live HEAD refs were checked against their original 40-character SHAs and were unchanged.

The QA repair PR #157 (`7d1ae6b8ef93d10cfb6810987672360885e9c1aa`) remains separate, older than integrated safety text. Synthetic-fixture PR #169 (`e9cd7766dac59d47ab467d8945269b9146c2aef5`) remains an isolated draft. Neither may be merged unchanged without current integration review. Homepage PRs #49 and #254 remain untouched.

## Executed Python checks

- **97** collected native R21/R22 tests: **96 PASS + one explicitly SKIPPED real-source test** because the local reconstruction lacks a trusted full Git checkout.
- **746** reconstructed available R12–R22 tests: **745 PASS + the same real-source SKIP** (not a complete repo-wide test run; missing R8–R11 implementations/corpus in this reconstruction).
- The real source test is **not** a silent pass: it runs `audit_frozen(repo_root)` automatically under the existing R18 native unittest-discovery step *when* executed inside a full Git checkout. It rejects changed or symlinked source files and false review states. Standalone CLI: `python -I -B preparedness/tools/source_group_review_gate.py --root preparedness`.
- New production and test Python files were independently verified Git-blob-identical to those exercised locally.

## Outstanding release barriers

The real native validator, WordPress draft build, 11-stage R18 preflight, and full review of 1,959 citation occurrences **have not run** against an exact complete checkout. The known GitHub Actions run #41200742724 failed without a runner assignment or executed steps; the private checkout is unavailable in the isolated local environment. No human reconciliation of 30 shared URL groups, qualified high-consequence safety review, source-link/claim checks, or independent QD clearance has been established.

No original article bodies, water-tool files, source records, taxonomy, homepage or navigation were edited. No WordPress, CMS, publishing, merge, or public actions were taken.

**Do not interpret source-blob parity, synthetic test passes, or the inherited `safety-approved-draft` status string as a verified safety determination.**