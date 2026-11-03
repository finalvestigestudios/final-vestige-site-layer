# Stage 3 ledger: pinned constants moved, and not moved (2026-11-03)

Branch `integration/preparedness-custody-repair-20261103`. Frozen PR #584 head `ddb3528b` is untouched. Everything here is **git-input identity and inventory accounting only**. Nothing is a source check, a safety review or permission to publish. `release_state` stays `HOLD`, `may_publish` stays `false`, and every `safety_review` state is unchanged (35 pending, 4 not-required, 2 approved, 41 drafts; the five new tools are `pending`).

Results below are **local** (Windows, Python 3.13). Hosted CI is blocked by the billing restriction (`GITHUB_ACTIONS_BLOCKER.md`).

## 1. Data re-frozen (stage 3a, commit `71354b7b`)

| File | Change | Why |
|---|---|---|
| `sources/article-evidence-lock.json` | 24 locked paths re-frozen (23 equal the blob in frozen PR #584; `pioneer-supply-chains-failed.body.html` carries the reviewed Hastings correction); 5 tool records added (`family-reunification-card`, `home-fire-escape-worksheet`, `power-outage-planner` from `shelter`; `kit-builder`, `reunification-plan` from `start`); `local_tool_count` 1 to 6; `longform_article_count` stays 35 | the lock described the 2026-10-30 tree. `evidence_freeze.py` has no write mode (it only verifies), so the lock is hand-maintained; it was updated by a script that touches only rows whose current blob differs and cross-checks every hash against `git rev-parse HEAD:<path>` |
| `sources/crosswalk.json` `source_files` | `git_blob_sha` and `count` for `start` (27 to 29), `shelter` (31 to 45), `hist-home` (27 to 29), `hist-field` (26 to 28) | the four fragments changed; 3 of 4 equal the #584 blob, `hist-field.json` carries the Hastings correction |

`validate.py`: 59 errors to 0 (one by-design warning: 32 shared-source groups not yet human-reviewed). Round trip of both JSON files is byte exact, so the diffs contain only the intended lines.

A worktree artifact was also fixed without changing any commit: two `eol=lf` files (`navigation-before-gps.body.html`, `pioneer-supply-chains-failed.meta.json`) were CRLF on disk although LF in git (global `core.autocrlf=true`); they were re-materialized from HEAD so that the validator, which hashes working-tree bytes, sees the committed blobs.

## 2. Gate constants moved (stage 3b)

| File | Constant | Old | New | Why |
|---|---|---|---|---|
| `tools/source_group_review_gate.py` | `FROZEN_BLOBS[sources/crosswalk.json]` | `1d907264dd58…` | `da823671f06e…` | stage 1 declared 20 new rows and 2 groups; stage 3a re-froze `source_files` |
| | `FROZEN_BLOBS[taxonomy.json]` | `eea601e53e16…` | `15c547bb3018…` | integration added 3 tools and upgraded 2 (`not-started` to `drafted-pending-safety-review`, `gate: true`); slate untouched; change is additive and stricter, identical to #584 |
| | `FROZEN_BLOBS[fragments/start.json]` | `29574c328cbab…` | `96140d6d1872…` | 27 to 29 rows |
| | `FROZEN_BLOBS[fragments/shelter.json]` | `d9eeb4546e58…` | `2a3f1a7ddeab…` | 31 to 45 rows |
| | `FROZEN_BLOBS[fragments/hist-home.json]` | `6460d4b07349…` | `8d85fd868508…` | 27 to 29 rows |
| | `FROZEN_BLOBS[fragments/hist-field.json]` | `4f369122cc0e…` | `88d4face1385…` | 26 to 28 rows; Hastings correction |
| | row, URL, group, id-group counts | 224 / 186 / 30 / 15 | defaults kept; live path passes `INTEGRATED_COUNTS` = 244 / 202 / 32 / 15 | the original values stay the default so every synthetic-fixture test is untouched; only `main()` (and the real-checkout test) use the integrated values |
| | tool set | `{water-planner}` | defaults kept; live path passes `INTEGRATED_TOOLS` (6 built tools, each must be `gate: true` in the taxonomy) | the five tools exist in `article_origins`; the new check fails if any lost its gate |
| `tools/source_crosswalk_truth_gate.py` | `EXPECTED` | 224 / 186 / 30 / 15 / 15 | 244 / 202 / 32 / 15 / 15 | measured: 244 rows, 202 URLs, 32 groups, 15 duplicate ids; the 20 added rows are all read rows, so unread placeholders stay 15 |

### Test pins moved with them (assertions only; no test logic changed)

| Test | Old | New |
|---|---|---|
| `test_evidence_freeze` | 36 records, 1 tool | 41, 6 |
| `test_integration_audit` | 1 tool, 36 drafts, 224 rows, 209 machine-verified, 30 groups | 6, 41, 244, 229, 32 |
| `test_source_crosswalk` | tools `{water-planner}`, 224 rows, 30 groups, 186 URLs | 6 tools, 244, 32, 202 |
| `test_source_review_queue_corpus` | 36 items, 224 rows, 186 URLs, 30 groups, 209 verified, 224 link checks pending, 36 drafts, 30 pending safety, 367 pairs | 41, 244, 202, 32, 229, 244, 41, 35, 452 |
| `test_start_latest_reconciliation` | 27 start rows, 224/186/30, 1 tool, 30 groups pending | 29, 244/202/32, 6, 32 |
| `test_source_group_frozen_custody` (real checkout only) | `audit_frozen(root)`, 30 groups | `audit_frozen(root, counts=INTEGRATED_COUNTS, tools=INTEGRATED_TOOLS)`, 32 |

Independent checks behind the numbers: 452 article-to-source pairs was recomputed from `{{cite:}}` tokens (452 over 41 items); safety states recomputed from the metadata (35 pending, 4 not-required, 2 approved, all `draft`; original 30/4/2).

## 3. Deliberately NOT moved, and why

| Item | Root cause | What a decision would have to say |
|---|---|---|
| About 25 whole-corpus census gates (`claim_occurrence_audit.BASELINE` 36/367/224/30/1959; the `EXPECTED = (35, 1, 1959, 367, 43, 30)` tuple in `citation_fallback_review_gate`, `article_review_dossier_gate`, `citation_occurrence_priority_gate`, `citation_review_batch_gate`, `citation_review_handoff_gate`, `reviewer_*` gates, `global_shared_source_review_gate`, R53 to R59; `claim_corpus_release_gate.EXPECTED_TOOLS`) | they pin the *original* 35-article + 1-tool census (1,959 occurrences, 367 pairs, 43 base fallbacks, 779, and so on), and each fingerprint chains into the next. Moving them means re-deriving a new census over 15 changed articles and 5 new safety-gated tools, which is new frozen evidence, not a constant | whether to write a successor "integrated candidate census" generation, rather than retrofitting the original gates. Not done here |
| R48 claim rows / figure triage (`docs/r48/*`), R49, R51 | frozen evidence derived from rendered-browser QA of the original article blocks; "R48 claim rows no longer match original article blocks: re-triage required". Cannot be regenerated without a rendered QA pass, and must not be rewritten | re-triage of the changed and new blocks |
| R23 81-file archive freeze (`R20-REMOTE-GIT-OBJECT-CUSTODY-HOLD.json`, `R23_MANIFEST_BLOB`) | it freezes exactly 81 original paths and rejects any other corpus item; the integrated tree has 91. The manifest is frozen evidence | a successor manifest for the integrated corpus |
| `qa_current_copy_concordance.py` (`GUARDS`, `ARTICLES`, `KEY`) | pins the *start* contributor's `three-day-kit` and `household-emergency-plan` text and the medication-safety phrases. The RC rewrote that passage. Moving the pin would accept changed medication wording | a qualified reviewer's decision on the medication copy (see section 4) |
| `test_r31_unread_base_register_custody` "all 224 original rows" | by name an original-corpus test | a successor test, not an edit |
| R14 manifest for `start`, `shelter`, `hist-field`, `hist-food` | see stage 4 notes | see stage 4 notes |

## 4. Findings for a human reviewer (not changed)

1. **Two tests contradict each other on the same safety sentence.** `test_start_here.test_removed_wording_stays_removed` bans `Do not stop, throw away or ration` in `three-day-kit`; `test_start_latest_reconciliation` requires `do not stop`, and commit `d44fc2c5` restored that sentence at QD review 1's request. Separately, the RC rewrote the FEMA-disagreement passage and removed the phrase `the two FEMA sources differ` that `test_start_latest_reconciliation` still requires, and changed the medication alert title and body. These are conflicts on **medication wording**; they were not edited around.
2. **Start and shelter integrated files do not equal any contributor head.** The 10 shelter paths were first created in the RC integration commit `da334241`; the start paths come from the "Start Here release candidate" line (`242c440d`, `e9bd2d8c`, `92a2eb9d`, `d44fc2c5`). The R14 premise ("only the seven contributors' own articles") does not hold for these two clusters.
3. Remaining local failures are otherwise Windows-environment artifacts (symlink privilege, `Errno 22`, `write_text` newline translation, git identity in temp repos) that fail identically at frozen #584.
