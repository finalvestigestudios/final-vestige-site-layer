# Media Recovery: Baltimore 1904 / LOC six-image exact-source custody

**Review:** 2026-11-01. **Post:** [190 — The Hoses That Wouldn't Fit](https://finalvestige.com/2026/08/18/the-hoses-that-wouldnt-fit/). **Scope:** Image provenance and conditional recovery, NOT homepage design or Site QA PR #154.

## Fresh CMS readback / evidence threshold

Authenticated, read-only WordPress `posts.get(context=edit)` returned published post 190, modified **2026-10-29T14:46:47**. Exactly **6/6 stored image `src` values and 6/6 full `alt` descriptions matched** frozen source census `qa/media-recovery/parts/06.json` (Git blob `0f3dfe398a76838049cebba7cb773d5c5a0c8c69`). All are external LOC image paths. This proves **only source identity**, not live visitor rendering.

| Slot | Original exact-source digital ID | LOC catalog LCCN | Editorial/rights caveat |
| --- | --- | --- | --- |
| 190:0 | LC-DIG-npcc-18735 | [2016826957](https://www.loc.gov/item/2016826957/) | National Photo Company glass negative; LOC original negative-sleeve title unverified. |
| 190:1 | LC-DIG-stereo-1s46043 | [2022653666](https://www.loc.gov/item/2022653666/) | Rau stereograph; LOC says **Engine 15 deserted during Hurst Building collapse**. Copyrighted 1904 by publisher William H. Rau. |
| 190:2 | LC-DIG-npcc-18713 | [2016844556](https://www.loc.gov/item/2016844556/) | B&O train; catalog mentions thirty-one-minute trip, which remains a historical caption claim, not independently timed. |
| 190:3 | LC-DIG-npcc-18729 | [2016844568](https://www.loc.gov/item/2016844568/) | National Photo Company image of Chief Belt, Marshall Bieber and D.C. firefighters. |
| 190:4 | LC-DIG-npcc-18712 | [2016844555](https://www.loc.gov/item/2016844555/) | National Photo Company, Jones Falls. Caption comes from unverified original sleeve. |
| 190:5 | pan 6a05834 | [2007662234](https://www.loc.gov/item/2007662234/) | Frederick W. Mueller panoramic print; 1904 copyright deposit documented. Panoramic crop must preserve geographic context and detail. |

**Record-identity strength:** The six exact LOC digital IDs occur in the existing original CDN paths and correspond to the official catalog resource IDs. That is a strong archival record-to-URL mapping, **not** cryptographic proof of matching image binaries or a license to republish.

**Rights:** LOC says **“No known restrictions on publication”** for these catalog records, but states it cannot grant publication rights and places independent rights diligence on the user. The 1904 Rau copyright claim and Mueller copyright deposit are historic provenance, not evidence of a currently active copyright. Before localizing, assess the exact chosen derivative, source credit and any third-party restrictions. Individual rights reviews remain **HOLD**.

## High-value visual-integrity finding

Current image **190:1** ALT says “Engine 15 near the Hurst Building at the beginning of the Great Baltimore Fire.” LOC's more specific original label identifies the engine as **deserted during collapse of the Hurst Building**. A conservative proposed ALT for editorial review only: *“Engine 15 deserted during the collapse of the Hurst Building at the start of the 1904 Baltimore fire.”* Do not edit the published post without separate approval.

The existing six sources appear to use LOC's small-view `v.jpg` images for five slots and an `r.jpg` panoramic derivative for the sixth. **Do not assume** these already-small JPEGs have a worthwhile 76% reduction available; published LOC catalog JPEG size figures are not actual visitor transfer. Aggressive resizing may degrade legibility, especially the panorama.

## Exact-source browser evidence and staging plan

1. Site QA #154: logged-out Chrome/mobile Image-type requests for each of **190:0–190:5**, with rendered `currentSrc`, redirected final request URL, actual HTTP status/MIME, encoded transfer bytes, `naturalWidth`/`naturalHeight`, and screenshot. Host/CDN viewer errors without Chrome evidence remain inconclusive.
2. Media Recovery: for **confirmed visibly failed** slot, validate the exact LOC original and crop against the published ALT/caption, record item rights/credit, inspect original pixel dimensions, fetch only approved source under permitted terms, hash the master, produce a **width ≤960px** no-upscale image preserving aspect ratio and legibility. A 960px canvas is a ceiling, **not** a mandate to upscale small originals.
3. Stage only as a separately reviewed WordPress Media Library proposal: file naming, credit/caption, master SHA-256, derivative bytes, width/height, thumbnail/responsive variant checks, cache-control and visual before/after. Do **not** rewrite Gutenberg blocks or replace `src` on production without explicit approval.
4. Re-measure same-page mobile before/after image encoded bytes and page LCP/CLS. Until identical baseline vs changed-page captured, claimed **76% reduction remains unverified**. The **42 reported broken** original images are likewise unverified. The **13 WordPress originals >1.5 MiB** concern separate local media files, not these six offsite LOC derivatives.

**Observed this run:** official LOC search/catalog record text and current WordPress source URL/ALT; binary image retriever could not inspect six requested JPGs. **Zero visitor-browser HTTP statuses, zero confirmed broken images, zero actual browser image weights, zero assets downloaded, zero WordPress production edits or expenses.**

**Artifacts:** `qa/media-recovery/baltimore_190_loc_20261101.json`; `validate_baltimore_190.cjs`; `test_baltimore_190.cjs`. Tests enforce exact source/census/catalog IDs, item-level rights holds, unknown live browser status, and ≤960px/no upscaling. **Verification:** 41/41 exact committed-source isolated V8 tests pass, including malformed-URL defensive handling. Native Node CI and actual Chrome acceptance still required.
