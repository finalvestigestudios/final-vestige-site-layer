# R48 / R49 reconciliation report (what was integrated, conflicts, what is still outstanding)

**Method.** `docs/rc/integrate_contributors.py` (reproducible; actions in `INTEGRATION-ACTIONS-2026-11-01.json`) applies each contributor's changes since its **frozen pin** to the current tree: take the newest copy when the current copy equals the pin; do a real 3-way merge (base = pin) when the current copy differs; report conflicts; never discard. CRLF text was normalized to LF (the chain is LF and byte-pinned).

## 1. Finding that changed the plan
My earlier "R49" reconciliation (branch `review/preparedness-r49-shelter-continuation-reconcile-20261101`) was based on the R48 head. **The chain had meanwhile advanced to R61 (#559, 13 stacked draft PRs by other agents)** and treats contributor drift through read-only dossiers (R60, R61), not by merging. The candidate was therefore rebuilt on the R61 tip. The old R49 branch is superseded.

## 2. R48 incorporation
The tip already carried R48 up to `dbd53411` and a copy (via R52) of the first rendered-QA commit `4fe053c4`. Missing from the tip: `4fe053c4`'s later siblings and the **QA-F1 phone-layout fix `23544eae`**. Merged the R48 head into the candidate: 2 conflicts, both docs identical to `4fe053c4`; `build.py` and `preparedness.css` merged cleanly. R52 pins the first versions of `RENDERED-QA-REPORT` and `ARTICLE-READINESS-MATRIX`, so those two files were restored to the pinned bytes and the updated versions saved beside them (`*.F1-UPDATE.*`).

## 3. Conflicts and how they were resolved (against actual content)
| Conflict | Resolution |
|---|---|
| 10 shelter add/add conflicts (articles, `CLUSTER-shelter.md`, `shelter.json`) in the earlier R49 attempt | Not conflicts in the new method: chain copies equal pin `5daeaf2d`, so the continuation applies |
| **Slug collision**: shelter and Start Here each built a different tool named `reunification-plan` (Start Here: household plan builder; shelter: wallet-card generator) plus competing `taxonomy.json` rows | Shelter's card renamed `family-reunification-card` (files, generator, tests, links in four shelter articles, taxonomy row); Start Here keeps `reunification-plan`. Both contributors' work preserved (S-6) |
| `taxonomy.json` three-way conflict (tool rows) | Union of both clusters' rows (5 tool rows), all gated |
| `tests/test_preparedness.py`: food's and hist-food's fixture rewrites vs the chain's isolated-fixture tests | Kept the chain's (more robust: sandbox copy, in-memory fixtures); the rewrites are redundant |
| hist-food source-ID retarget `hist-food-nchfp-jerky` -> `nchfp-jerky` (library refuses an undocumented duplicate id) | **Not integrated**; decision S-7 |
| Raw URL in a shelter source note widened two pages by 14 px at 320 px (caught by shelter's own browser tests after integration) | CSS: `.pa-sources li span { overflow-wrap: anywhere; }` |

## 4. Defects found in the contributor work and corrected on the candidate
1. **Medicine guard dropped by the Start Here RC.** QD review 1 required "Do not stop, throw away or ration a medicine you depend on because of anything on this page..."; the RC's `three-day-kit` quoted FEMA's "discard" wording without it. Restored verbatim (still pending human review).
2. **Founder-approval attribution.** `making-water-safer` and `salt-beef-salt-pork-age-of-sail` named "Bryan Rhodes (founder)", a name taken from the About page. Name removed; records now say they hold only a one-word chat reply, no checklist review, unconfirmed scope, and "safety review NOT COMPLETE for release purposes". Also fixed in `SAFETY-REVIEW-CHECKLIST.md`. The `approved` state itself is left for the founder (X-2).
3. **1796 vs 1798 cookbook.** Verified, no code change needed: the integrated `pickling-fermentation-old-recipes` and source records state that only the 1796 **catalogue record** was read and the text read is the **1798** printing (Hartford: printed for Simeon Butler, Northampton, 1798; MSU Feeding America transcription at `https://d.lib.msu.edu/fa/1`, described there as "First edition, second printing", Jan Longone Wine and Food Library). Edition metadata and the MSU quote were re-read on 2026-11-02. The **passage-level claims** (potatoes, parsnips, May butter, parsley, pickling) rest on the contributor's read of the MSU full-text download (about 82,000 characters), which this session did **not** re-verify. The Library of Congress record page returned HTTP 403 to a script. MSU's note says the 1798 printing "follows word for word the text of the first printing"; the article correctly does not rely on that.

## 5. Where the candidate stands against the chain's guards
- `validate.py`: the repository tree fails closed (`ValueError: duplicate source id 'fsis-power-failure' is not documented in source crosswalk`), because the shelter follow-up adds a third variant of a shared source and new groups. With the crosswalk and lock regenerated **in a copy** (`simulate_custody_update.py`), validate = 0 errors, 1 warning; build exit 0; 50 pages.
- Full native suite on the simulated copy in place: 4,924 tests, 87 failing, 2 skipped. 46 are the known Windows environment classes (24 symlink privilege, 10 nondeterministic Errno 22, 12 fixture newline). The R61 tip's own run: 4,874 tests, 55 failing. Of the candidate's 41 non-environment failures, 30 do not fail on the tip and are **all freeze/inventory gate assertions** (R23 81-file, R49 186 claim blocks, R51, R53-R59 "frozen 35 articles plus 1 planner", R31 224 rows, source crosswalk 30 groups, `test_start_latest_reconciliation` counts 27 sources etc., integration audit 36 items). Two are content-phrase guards: `the two fema sources differ` (RC reworded; meaning preserved and more precise) and the medicine guard (fixed). The medicine guard test passes after the restore; the food phrase test fails on wording only.
- Nothing in these failures indicates a broken page; but they are the machinery that proves custody and they stay red until a reviewed re-baseline (X-1).

## 6. Outstanding
Re-baseline (X-1); human decisions X-2, X-3, S-1..S-7, H-1..H-10; independent QD on the exact head; human safety review of 29 articles + 6 tools; human link check (0 of 244 rows); 9 unread cited sources; shared-source scope review of 32 groups; live-theme render; screen-reader pass; Linux/CI run.
