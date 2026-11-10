# R274 — original source URL labels versus review-only alias lookup

**2026-11-10 PT | Issue #136; conversion liaison #820 | DRAFT / HARD HOLD, UNPUBLISHED**

## Material defect and correction

R272's `inspect()` incorrectly required `group["url"] == alias(group["url"])`. Five labels in the **frozen authentic crosswalk** end in slashes that the review-only `alias()` normalization strips. Consequently R272 returned `INVALID_HARD_HOLD` for the authentic baseline, blocking R273 and the downstream R220 draft custody pipeline. Praxxis independently documented this defect in the existing handoff. Replacing the historical labels or rewriting source URLs, IDs or citations to placate the gate would destroy provenance.

R274 repairs this without touching the frozen crosswalk or the eight source registers:

1. Keep historical `group["url"]` and `group["canonical_url"]` **exactly as authored**, including terminal slashes.
2. Use separate `lookup_key = alias(url)` only when joining a group to the review grouping index, tracking seen groups, or verifying each original variant's alias. The alias retains the URL query and fragment.
3. Require each group label to appear **verbatim in at least one original source row** within the matched group, so an invented lookalike label is rejected.
4. Count the historical slash variant against the **original frozen label**, preserving the existing single-variant census.
5. Preserve the existing unresolved reviewer and approval flags. Preserve the original 35 article bodies, six tools, 2,000 citation occurrences, all 41 intended export routes, reading-depth annotations, and original R273 reviewer docket.
6. Re-pin R273 to the repaired R272 Git blob, and R220 to both corrected gate Git blobs. Neither gate grants review clearance or publication.

## Verified read-only original-source reconstruction (GitHub-connected, NOT native Python)

Authenticated the exact eight frozen source Git blobs against the crosswalk manifest:

| Origin | Original Git blob |
| --- | --- |
| base | `b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77` |
| food | `a1f73c8170932d6b3192e9cd506686d516d23d30` |
| health | `cc29c439372b9d49debf78e63020ffe4d62baeb8` |
| hist-field | `3dafa9425f3829c0be2e6fea00889aff95124031` |
| hist-food | `d10628342fea5f177a8d1be00dd906d0c9c7850e` |
| hist-home | `8d85fd868508c5caba14a839d119d55f31f14f72` |
| shelter | `2a3f1a7ddeab2782add875be1e0e378513504aa1` |
| start | `96140d6d1872588e5d20d9052445c9157e88934d` |


Result from **actual GitHub source JSON compared against frozen crosswalk and R273 docket**:

- 244 unchanged source rows, 202 exact URLs, 201 review-only URL aliases.
- 32 unresolved shared-URL groups; 15 unresolved duplicate source-ID groups.
- Five slash-ended authentic group labels; all five labels are genuine original source URLs.
- One historical slash-variant reading relative to its group's original label.
- Zero missing group alias keys, zero invented group labels, zero source variant dictionary/provenance mismatches, zero unaccounted groups.
- R273 remains `DRAFT_HARD_HOLD`, with `independent_qd_pass=false`, `medical_safety_verified=false`, `publication_authorized=false`.

This is **connected-data structural verification**, not execution of the native Python validators, build, CMS export, a human claim/safety review, or real browser accessibility.

## Regression and environment

The existing R272 test suite includes synthetic adversarial variants. R274 adds an authentic-eight-origin baseline test (previously missing), two positive slash-ended group-label tests and negative tests for invented labels, changed queries, approval mutations and altered source evidence.

The complete native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, and `python -I -m unittest discover -s preparedness/tests -v` require an authenticated full repository checkout. This local container still reports `Could not resolve host: github.com`. **No native Python/test count or 41-export result is claimed for R274**. Execute these on a full, source-authenticated checkout before considering any merge.

## Strict holds and release controls

Unresolved: 32 URL reading groups, 15 ID collision groups, Article #7's two CDC citations and chemical-contamination guidance, Article #20's Ready.gov claim, Article #15 and Tool #104's child/household privacy and printed-card usability, physical printing, independent qualified reviewer, independent QD, and full native integration. The original source and all manuscript/route/CMS outputs remain unmodified.

No WordPress or public publishing, navigation, CTA activation, merchant testing, social content/posting, measurement script, email, affiliate or spending change. No retired water freebie.

## Conversion-first handoff (#820)

**Single provisional commercial offer:** existing Legacy Triage PDF, not yet approved as a Preparedness upsell. **Audience:** households organizing emergency contacts/reunification. **Free step:** the already public `https://finalvestige.com/preparedness/` (do not send traffic to unpublished guides or prototype cards). Before proposing any paid CTA, founder/commerce must verify full PDF rights, suitability, sensitive-records privacy, merchant delivery, checkout, fees/refunds and relevant product fit. Existing Grok/Praxxis TASK-008 owners must verify an already-published suitable `asset_id`, date, rights, permitted native mobile link and tagged destination; otherwise **NO VERIFIED MATCH**. Payment metrics, attributed confirmed orders and fee/refund-adjusted net revenue are **NOT COMPUTABLE**, not zero.

**Owner sequence:** Preparedness/QA original-source gate → independent editorial/qualified safety review → Grok/Praxxis existing-asset acceptance → Founder/Commerce product and checkout approval → Analytics/Commerce confirmed orders, fees, refunds and 7/30-day cohort net revenue per 1,000 qualified human sessions.

**DRAFT / HARD HOLD; no independent QD PASS.**
