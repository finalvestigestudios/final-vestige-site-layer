# Deterministic cross-cluster source audit — HOLD

**Snapshot:** 2026-10-30. **Integration:** draft PR #176, base `feature/preparedness-archive-v1` at `ee591e2df5de08aea7603fc4cbf3c5249361e119`.

This registry enumerates **all 223 original source rows** in the base + seven source fragments. It records 186 exact unique URLs, **30 duplicate URL groups** and **15 repeated source-ID groups**. The JSON contains every original source row for each collided URL, including the exact title, kind, date, `supports`, `notes` (reading depth), and human-link-check flag, plus the Git blob SHA for each source file. All original source fragments remain in Git, unaltered. No rows are deleted or silently upgraded.

## Rules
1. A repeated URL does **not** make the underlying *claim scopes* identical. For example, multiple articles cite the same LOC collection landing page with different depths of reading; a catalogue record cannot automatically substantiate a quotation from an underlying diary.
2. A repeated source ID with one unverified placeholder and one verified row can be a legitimate, strictly same-URL upgrade, but **a second independently verified row is a separate provenance event** and may contain a narrower or broader claim scope. Record both.
3. Source selection in the combined builder must be article-origin-scoped. A historical-field article citing `loc-pioneer-diaries` must not silently receive the deeper historical-food interpretation (or vice versa).
4. Source groups are **unresolved by default**. They can be made review-complete only by a human reading the relevant pages, specifying the supported claims and recording reviewer/date/notes in a separately reviewed change. A build success is not permission to publish.
5. Never infer a human link verification from `verified_on`: every `human_link_check:false` remains false. Do not invent primary-record checks or medical/food/water safety approval.
6. Validation should fail on an unrecorded duplicate URL, mismatched source row (including `supports` or `notes`), stale crosswalk, changed URL under the same source ID, or an attempt to publish a draft citing unresolved shared-source groups.

## Explicit known high-consequence review queues

- **Start Here PR #157:** retained its repaired copy rather than uncorrected cluster text. Medicine, infant-feeding, CO and shelter advice still awaits independent human safety review.
- **Food PR #169:** retains synthetic isolated fixture test, but no current verified food-safety review is implied. NCHFP/USDA interpretations must be checked against their own tested procedures, not paraphrased into new recipes.
- **LOC records:** `loc-prairie-traveler` and `loc-pioneer-diaries` differ in how much original text authors actually read. Keep the individual notes intact. The presence of a digitized *collection* is not proof that all diaries were read.
- **FEMA outage fact sheet:** branch notes disagree about page count and extraction method. Check the actual current PDF, all relevant pages and its dates before treating it as verified by a human.
- **NCHFP homepage:** an index/catalogue page cannot validate an individual canning/jerky procedure.
- **CDC/EPA water boiling elevations:** retain the separately approved draft's explicit discrepancy and recheck official text; no silent agency harmonization.

## Build, QA and publication boundaries

All **35 article slugs** and the local-only water-planner are represented by an explicit origin map. Every article stays **draft**; front-end appearance has not been verified. The raw fragments remain independent, and the integration branch targets the unpublished base branch. Do not merge the pending independent #157/#169 review work in place. Never modify WordPress, homepage, Focus Fieldbook or navigation from this lane.

To verify from an exact checkout when available: `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v`. Those commands have NOT been executed in this connector-only sprint; local GitHub access in this runtime is blocked, and CI runners have previously not dispatched.
