# R108 — Exact-Git source/citation change impact review (Issue #136)

**PRIVATE WORKORDER ONLY • RELEASE HOLD • NO ARTICLE IMPORT • NO HUMAN SAFETY, SOURCE, FACTUAL OR QD APPROVAL.**

## Scope and trust boundary

R107 proved that five of the seven Claude contributor branches advanced, changing 23 tracked paths (seven bodies, six metadata files, three source fragments, five research notes and two tests). It did **not** determine whether updated claims, quoted research, modern emergency advice, or source-use descriptions are supported. The original R14 metadata exception stays open. Original R15 parity **must continue to fail closed** on moved historical branch refs, even if R108 succeeds.

R108 adds a **read-only second layer**: reconstruct the original R107 exact-head review queue; for each changed path read the frozen and current Git objects by exact commit and path; verify both against their Git blob object IDs; and generate a deterministic private impact dossier that never contains article paragraphs or source notes. Reported hashes are *not* signatures or factual validation. An attacker with repository write permissions is outside this control's threat model.

The new indicators distinguish content loss or alteration from mechanical identity:

* **Article bodies:** exact added/removed citation occurrences (not merely citation IDs), estimated word/heading depth, and diminished on-page safety-label markers. Stable citation counts do **not** prove claim accuracy.
* **Article metadata:** source-use key additions/removals and changed reading descriptions, canonical slug drift, publication/status changes, and safety-review state/scope/date differences. Even a purported contributor 'approved' status cannot grant qualified safety approval.
* **Source fragments:** exact source-ID churn, literal source-URL changes, support/reading-scope changes under the **same** URL, human-link-check and verification-date modifications. URL equality never collapses author-specific reading scopes.
* **Research logs and tests:** preserve explicit provenance-path reviewer entries. All altered files require human review, including two tests outside the original 72-path author evidence scope.

The output intentionally does **not** propose automatic merges, altered article URLs, changed citations, an updated frozen manifest, CMS writes, or a new medical/safety verdict. It shows only **changed contributor paths**, not all 35 articles' factual validity. The native 35-draft validator and private build remain separate mandatory checks.

## Commands — trusted isolated full-fetch checkout only

```bash
python -I -m unittest discover -s preparedness/tests -p 'test_r108_*.py' -v
python -I preparedness/tools/r107_exact_branch_progression_adjudication.py --repo-root .
python -I preparedness/tools/r108_source_citation_change_impact_crosswalk.py --repo-root .
python -I preparedness/tools/r108_source_citation_change_impact_crosswalk.py --repo-root . --json > "$RUNNER_TEMP/r108-private-review.json"
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The output is printed to stdout only. Keep the detailed JSON private; no artifact publishing and no direct WordPress or site access.

## External coordination / status checked November 3, 2026

All seven Claude contributor heads and the distinct release-candidate head were checked against their exact prior verified Git identifiers. Independent Start Here safety PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` remains DRAFT and unmerged. Food fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` remains DRAFT and unmerged: its former `_upgrade_test.json` write is corrected, but `test_register_fragments_cannot_duplicate_ids` still writes `_dup_test.json` under the shared source tree. Move this case into a temporary copied repository root before independent QA/merge. Homepage PR #49 `10495883299d53596992c26a8987f629b2904670` and flagship PR #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` are read-only coordination references.

## Release criteria remain outside R108

Human review of 30 shared-source URL groups, five changed contributor branch histories, the original R14 exception, 15 safety exceptions, 22 editorial decisions, five unfinished tools, external source/claim checks, qualified emergency/medical review, browser/print review, independent QD, and the **entire** 13-stage mandatory integrity suite remain gating work. R108's tests and any diagnostics success do not discharge these. No WordPress CMS, navigation, publication or source-content changes are authorized.
