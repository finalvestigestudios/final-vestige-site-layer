# R79 — Uncited Consequential Passage Context Work Orders (PRIVATE / HOLD)

Issue #136. This is **one-way, read-only reviewer triage**, not emergency guidance clearance, independent QD approval, source validation or publication authorization.

## Why this is necessary

R78 assembled all 35 original article drafts, six tool drafts, 244 complete origin-scoped source readings, 2,173 citation occurrences (with 2,359 separate source-variant relationships), and 4,070 unabridged article/tool DOM text blocks in their original reading order. Its lexical action/quantity review queue has 1,068 passages, including **347** with no citation within that same text block. Their absence is **not** a finding that a claim is unsupported. A nearby citation is **not** proof that a passage is substantiated, and nearby safety language is **not** proof that emergency guidance is safe.

R79 turns precisely those 347 candidates into individual, deterministic, source-custody-preserving human review orders. Each order includes the complete passage, original 1-based document position, the two preceding and two following unabridged blocks when present, *all* citations embedded in those neighbors with all distinct original research/source origins retained, plus the nearest earlier and later cited block anywhere in the same draft. Each neighboring source retains its exact URL, source origin, source ID and complete reading fingerprint. Citation distance is an editorial locator, not a safety or credibility score. No citation is silently assigned to the consequential passage.

The entire original R78 source-to-document-to-citation evidence tree is retained verbatim inside the new sealed report. R79 **independently reconstructs R78 from its complete R77 parent** before creating any derived task, rather than trusting an easily edited/re-sealed candidate list. Private CSV export is spreadsheet-formula-neutralized and **one way only**: no results or approvals can be uploaded/imported to clear a gate. No exact URL rewriting, source ID aliasing, source-date auto-correction, original article editing, summary shortening, or WordPress/CMS writes.

## Invariants (must be verified on exact head)

| Item | Expected |
|---|---:|
| Complete original article + tool drafts | 35 + 6 |
| Origin-scoped full source readings | 244 |
| Individual citation occurrences | 2,173 |
| Citation to source-variant edges | 2,359 |
| Original unabridged DOM text blocks | 4,070 |
| Shared exact-URL identity groups | 32 |
| Repeated source-ID groups | 15 |
| Lexical action/quantity review candidates | 1,068 |
| Consequential blocks without local citations | 347 |
| Human source-link checks, claim-support reviews, qualified safety and independent QD approvals | **0** |

No one should interpret **347** as 347 errors, medically dangerous passages, or automatically unsupported claims. The search for neighboring citations is *inside the draft only* and cannot establish external source reliability. It intentionally does not normalize or combine evidence from shared URLs.

## Reproducible, offline-only commands

Run from an exact R79 branch checkout; do not execute the generated HTML in a public CMS.

```sh
python -I -m unittest discover -s preparedness/tests -p test_r79_consequential_context_review.py -v
python -I preparedness/tools/r79_consequential_context_review.py
python -I preparedness/tools/r79_consequential_context_review.py --private-review-csv-stdout > /tmp/r79-private-review.csv
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

R79 adds **109 individually named tests** (41 document-specific and 68 custody/synthetic checks). Their inclusion in a draft is not evidence of execution; report the exact Actions run/head status, including failures. New branch is stacked on R78 exact immutable head `7b25206767793753860dc4165d7e89f00a105afe` and changes only the four new R79 tool/test/doc/workflow files.

## Coordination snapshot, November 2, 2026

GitHub API checks confirmed current contributor heads: Start `2122d856fce9f64887c16df3d52e64be9f59a55b`, Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`, Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`, Historical food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`, Historical home `7504a5f099594d635e3dd7332a33a2e1346c43a2`, Historical field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`. Separate original RC draft PR #584 remains `ddb3528ba6494dada1fa1c3a142ce746e3a67706`.

Independent Start Here QA PR #157 is OPEN/DRAFT at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; Food synthetic-fixture PR #169 is OPEN/DRAFT at `e9cd7766dac59d47ab467d8945269b9146c2aef5`. The latter still retains a separate `test_register_fragments_cannot_duplicate_ids` test that writes `_dup_test.json` to the shared working tree. This owner-specific concurrency issue remains unresolved; R79 does not touch the other PR branch. Homepage #49 at `10495883299d53596992c26a8987f629b2904670` and Experience 2.0 flagship #604 at **`bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`** were checked read-only; no homepage changes made.

## Mandatory release HOLD, irrespective of a green engineering workflow

The separate 13-stage mandatory release-integrity workflow previously **FAILED** at `seven_cluster_git_parity`, reflecting five historical contributor-branch/frozen-provenance mismatches. A passing R79 private test suite would **not** fix or bypass that gate. The actual final R79 run status must be recorded separately if available.

Outstanding: frozen-vs-current contributor provenance reconciliation with explicit human decisions; 206 historical source-link duties and 0/244 candidate human checks; 30 original / 32 candidate shared-URL scopes; 43 fallback relationships; 15 safety exceptions; 22 release-candidate editorial decisions; qualified expert review of consequential emergency water/food/medical/fire/CO instructions; real WordPress/mobile/print/assistive QA; and independent exact-head QD. No public publication, navigation, CMS/WordPress edits, source advice approval, or branch merges. **Release state: HOLD.**
