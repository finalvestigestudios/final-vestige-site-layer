# R49: shelter continuation reconciliation: content merges cleanly, the custody freeze blocks it (HOLD)

**Date:** 2026-11-01. **State: HOLD.** This branch is a trial reconciliation of draft PR #521 (`claude/prep-shelter-continuation`, `ac8625fa`) onto the R48 head (`23544eae`). It is **not** an integration candidate. Nothing is published, no QD PASS or human safety review is claimed, and no frozen baseline or gate was edited.

## What was found
1. **The 10 conflicts were add/add artefacts, not real disagreements.** The R2 to R48 chain's copy of the four shelter articles, `CLUSTER-shelter.md` and `shelter.json` is byte-identical to the shelter review candidate `5daeaf2` (`git diff 5daeaf2d R48 -- <file>` is empty for all 10). The chain never edited them. With `5daeaf2` as the merge base, the continuation applies with no conflicts; I took the continuation's version of each of the 10 files.
2. **The continuation was committed with CRLF line endings** (18 text files, including all 4 articles). The chain is LF throughout and its custody gates are byte-pinned, so I converted exactly those 18 files to LF (content identical modulo CR; verified per file against the shelter branch). The continuation's author should commit with LF in future.
3. **The merged tree fails closed, by design.** `validate.py` reports **29 errors** and `build.py` refuses to write output ("PREPAREDNESS BUILD HOLD"). The full native run is 3,734 tests with 71 failures. 21 of them did not fail in the R48 run: 17 freeze, inventory, crosswalk and origin gate tests, and 4 `setUpClass` errors that follow from the blocked build (the shelter tool tests, the browser tests, the build tests and the integration report cannot start). The remaining failures are the known Windows environment categories (symlink privilege, fixture newlines, export bytes, nondeterministic Errno 22), whose count varies from run to run.

## Why the gates fire (none of this is a content defect)
The chain freezes the original 35-article archive (R22/R23: article and metadata bytes and lengths, raw source bytes, the 72-input/81-file manifests, the 224/234 raw source rows, the unique-URL and collision counts, the 35+1 inventory, the crosswalk article-origin map). The R23 hold records the rule: *"No legitimate editorial updates are automatically approved. Changed material must receive a separate, reviewed baseline/evidence record; the machine must fail closed rather than update the frozen author record itself."* The continuation legitimately changes frozen things:

| Gate | Fired because |
|---|---|
| article body/metadata bytes and lengths (4 articles x 2, 8 errors) | the continuation rewrote `family-communication-plan`, `home-fire-escape-plan`, `outage-heat-cold-generators`, `shelter-or-evacuate` |
| article inventory, tool count, untracked inputs | 3 new tool pages (`home-fire-escape-worksheet`, `power-outage-planner`, `reunification-plan`) |
| raw source bytes and row count (`shelter.json`) | 10 sources added (41 total) |
| crosswalk: raw row count (234), unique URL count, collision count, article-origin map | new sources and tool pages |
| `register: duplicate url without source crosswalk: https://www.weather.gov/safety/winter-during` | the new source `shelter-nws-winter-during` repeats a URL already in the register: a **new shared-source group** that needs a human source-scope decision |
| 3 x "source was not checked by its own cluster or the base archive" (`shelter-fema-power-outage-sheet`, `shelter-fcc-comms`, `shelter-nfpa-escape`) | the new tool pages cite shelter sources but have no cluster-origin entry |

## What I did not do, and why
I did **not** re-baseline. Editing the frozen constants, the crosswalk or the expected counts to make these gates pass would be the machine updating its own author record, which the R23 rule forbids, and would effectively accept 4 rewritten safety-relevant articles, 3 tools and 10 sources into custody without a QD or human review. That is a custody decision for the user and the QD reviewer.

## What a reviewed re-baseline would need (proposal, not applied)
1. QD and the human safety reviewer read the shelter packet (`SHELTER-QD-PACKET.md`) and decide the open items there; until then the pages remain draft and `safety_review: pending`.
2. A separate baseline/evidence record that pins the new article, tool and fragment blobs (old and new Git blob IDs per file) and the new crosswalk counts, plus a crosswalk entry and source-scope review for the `weather.gov/safety/winter-during` collision.
3. Cluster-origin entries for the three new tool pages.
4. Updated freeze tests (35+1 inventory, 72-input, 81-file, 224/234 rows) that state what was added and why, rather than loosening them.
5. A re-run of validate, build and the full suite on the result (the shelter tool and browser tests have not run on this merged tree; they pass on the shelter branch alone: 64 tests).

## Alternative
Keep `5daeaf2` as the shelter content in the chain and treat the continuation as a separate, later change (as it is today in PR #521) until review is complete.

## Follow-up: re-baseline attempted, scoped, and deliberately not applied (user said "yes" to authorizing it)
On inspection the re-baseline is not a data refresh. `docs/r49/propose_rebaseline.py` (read-only) shows what would change: 4 modified articles, 3 added tool pages, `shelter.json` (and the register) re-pinned, raw rows 224 to 234, unique URLs 186 to 195, shared-URL groups 30 to 31 (new: `https://www.weather.gov/safety/winter-during`, needing a human scope review), tools 1 to 4, and 3 missing article-origin entries. The mutable records (`article-evidence-lock.json`, `crosswalk.json`) are easy to regenerate, but the same numbers are also **hard-coded as independent pins in code and tests**: 16 files mention the 224-row baseline, 14 the 35+1 / 72-file inventory, 10 the 186-URL count, 8 the 81-file manifest, and 3 carry `FROZEN_BLOBS`. `source_group_review_gate.py` states that a mutable manifest "cannot authorize changes to itself" and pins the original taxonomy and source blobs outside it. Editing those pins myself would turn independent pins into self-pins, and they cascade (changing a gate's own bytes changes what later gates pin).

Two further reasons to wait: (1) any QD or human-safety edit to the shelter articles will change their bytes again and invalidate a pin taken now; (2) the Start Here release candidate needs the same kind of re-baseline, and two separate rewrites of the same pins would conflict. **Recommendation:** after the review decisions are made, do one re-baseline for all clusters, reviewed by QD, using `propose_rebaseline.py` output (`REBASELINE-PROPOSAL-SHELTER-2026-11-01.json`) as the starting delta. If you want me to apply it now anyway, as an explicitly self-pinned DRAFT that QD must re-pin independently, say so and I will; that is a larger change touching the gate code and about 20 tests.
