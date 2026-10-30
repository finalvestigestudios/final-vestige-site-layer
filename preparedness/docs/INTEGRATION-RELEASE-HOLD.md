# Preparedness integration: release HOLD and independent QA handoff

**2026-10-30. Draft PR #176** (target: unpublished `feature/preparedness-archive-v1`; no WordPress writes).

## Actual assembled state

- 35/35 complete editorial draft articles from the seven contributor clusters plus six original base drafts, all with `status.publish=draft`; one separate local-only water planner remains draft.
- Full source provenance preserved: 223 input source rows, 208 marked machine-verified, 15 unverified placeholder rows, 186 distinct literal HTTPS URLs, 30 documented duplicate URL groups and 15 repeated source-ID groups. All original fragments retained, 67 full raw rows included in the collision ledger; each shared URL's `review_status` remains pending.
- Read-scope resolution is per article-origin rather than globally inheriting the most conveniently verified source record.
- Independent safety PR #157 wording corrections brought into Start Here; food isolated fixture approach from #169 retained; their original PRs remain untouched.
- Source, editorial, human link, and independent QD release gates now block premature status changes. The builder's report must state HOLD; generated WordPress-compatible markup is **draft-only**.

## What has and has not been checked

**Executed via GitHub connector (static):** Verified exact file-path union from immutable 7 source SHAs; checked 35 readable source bodies against the 1,800-word minimum, each with at least 3 distinct in-body citations that resolve to a verified record in its own origin or the base; all article metadata checked for draft status and unique filename/slug; 223 source rows checked for HTTPS, source kind, verified date syntax and claim supports. Crosswalk generated from actual file bytes, not model memory.

**NOT executed:** native Python `validate.py`, `build.py`, full `unittest` suite, JavaScript water planner tests, CI, browser screenshots, axe, Lighthouse, human PDF full-page checks, human source URL click-through or editorial/safety review. This runtime has **no working git network** to fetch the private repo into a Python executor, and Actions dispatch has been reported unavailable. The addition of 54 tests does not mean those tests have run or passed.

## Required independent command sequence from a trusted exact checkout

1. `python -I preparedness/tools/validate.py`
2. `python -I preparedness/tools/build.py`
3. `python -I -m unittest discover -s preparedness/tests -v`
4. Browser render and accessibility at 360 / 390 / 768 / 1440 / 1920, print and no-JS. Confirm generated site shows **Draft** and **Safety review pending** where appropriate.
5. Audit all 30 shared-source claim scopes with individual source records and checked links, then close the ledger with actual named human reviewer/date/notes per group.
6. Verify clinical/food/water/CO/infant and disability content independently; only after approved evidence, confirm exact SHA, source link scope, WordPress actual preview behavior, and separately authorized launch.

For source validation concerns, see `docs/INTEGRATION-SOURCE-CROSSWALK.md` and the full provenance in `sources/crosswalk.json`.

### Representative unresolved hazards
- Medicine refrigeration in power outages: avoid suggesting unilaterally stopping/discarding essential medicine; pharmacist/prescriber instructions govern.
- Formula preparation and infant dosing; CO generator placement; fire escape and building-specific shelter instructions; pressure-canning and jerky; water advisory and boiling/disinfection limits.
- NCHFP index pages are not tested procedures. LOC collection records do not prove an individual diary's contents. Historic methods do not establish current safety.
