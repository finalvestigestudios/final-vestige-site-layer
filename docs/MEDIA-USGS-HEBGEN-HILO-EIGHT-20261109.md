# USGS Hebgen / Hilo source-integrity recovery — November 9, 2026

**Status: DRAFT, READ-ONLY.** No source image binary downloads, cached media, WordPress writes, Gutenberg block rewrites, homepage visual changes, licensing approvals, merges or spend. Site QA #154 owns logged-out Chrome collection.

## Evidence batch

Eight **new** upstream USGS S3 slots from the immutable Oct 30 288-external-origin census (blob `92a904c8da1ace1f972b2f00adf1a4847dde2b99`): published post 407 positions **0, 2, 3, 4, 5, 6, 7** plus post 418 position **5**. All eight literal stored URLs matched the frozen census. Full per-slot exact URLs and independent viewer references are in [machine-readable audit](../qa/media-recovery/usgs_407_418_eight_20261109.json).

**Independent source-viewer results:** **7 rendered actual images; 1 inaccessible through the viewer** (post `407:3`, `EarthquakeLake3.jpg`). These are **not** HTTP status codes, genuine visitor-browser tests, or evidence of original-host outages. Actual HTTP, `naturalWidth/naturalHeight`, cold transferred bytes and confirmed-broken flags remain null for **all eight**.

## Source/rights mapping and visual warnings

| Slot | Source observation | Authoritative catalog/context and action |
|---|---|---|
| 407:0 | Flooded home and damaged roadway; rendered | [USGS 1959 earthquake damage](https://www.usgs.gov/media/images/earthquake-damage-1959-hebgen-lake-event-yellowstone-plateau); likely related subject, NOT proven exact photo. |
| 407:2 | Monochrome Madison Slide; rendered | [USGS Aug 21 1959 landslide](https://www.usgs.gov/media/images/view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake), credited to **William B. Hall**; archival visual context, binary/crop unknown. |
| 407:3 | Tool inaccessible | [USGS 1959 slide history](https://www.usgs.gov/observatories/yvo/news/1959-madison-slide-part-1-a-deadly-consequence-hebgen-lake-earthquake); not a drop-in replacement; needs actual guest browser test. |
| 407:4 | Canyon debris road; rendered | [USGS aftermath/remediation history](https://www.usgs.gov/observatories/yvo/news/1959-madison-slide-part-2-recovery-and-remediation); exact item identity and rights unknown. |
| 407:5 | Large geothermal geyser; rendered | [USGS Old Faithful](https://www.usgs.gov/media/images/old-faithful-eruption) is **context**, not evidence of 1959 quake damage; image match unknown. |
| 407:6 | Another hydrothermal geyser; rendered | [USGS Yellowstone geyser image](https://www.usgs.gov/media/images/old-faithful-geyser-eruption-yellowstone-national-park) is context only; image match unknown. |
| 407:7 | 2023 Earthquake Lake view; rendered | [USGS gallery](https://www.usgs.gov/media/images/earthquake-lake-and-madison-slide) specifically credits **Mike Poland, June 27, 2023** (Public Domain catalog). Mark as a present-day retrospective, not 1959 eyewitness image. |
| 418:5 | 1946 damaged shops and vehicle in **Hilo, Hawaiʻi**; rendered | [USGS Hilo tsunami image](https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946) says creator/source unknown (Public Domain catalog). Distinguish Hilo damage from **Scotch Cap Lighthouse in Alaska**. |

**Rights gate:** An official USGS webpage marking its catalog photo Public Domain supports research but does **not** establish that any particular embedded derivative/crop is identical or contains no third-party contributions. Every proposed replacement requires item identity check, photographer/source credit, individual rights determination, scene/date accuracy and editorial visual review. All `rights_approved`, exact-match and production release flags remain `false`.

**960px rule:** No original intrinsic dimensions have been verified. Every `native_width/native_height/output_width/output_height` field remains `null`. Once native sizes are established, propose proportional derivatives capped at **960px** with no upscaling; preserve labels, archival borders, original image composition and legibility. No assets created.

## Performance method / QA handoff

The 61-post / 355-reference historical cohort and 66-post / 361-reference later snapshot must **not** be mixed in before/after measurement. The documented 15 WordPress originals >1,500,000 decimal bytes total **47,096,779 stored bytes**, not network bytes. The historical **76% site-wide transferred-image reduction is an unverified claim**, not a measured outcome. Compare paired guest cold-cache image **body transfer bytes** over the same pages, source slots, viewport/connection profile, device, lazy-load/full-scroll procedure and content versions; separately guard image decode, LCP/CLS and full-width+mobile screenshots. Do not count HEAD content length, disk cache, tool-renderer wrappers or media-library sizes as cold network transfer.

**Browser queue:** Site QA #154's **six P0** slots remain first (`285:5, 285:2, 287:5, 418:1, 418:2, 407:1`). Next verify `407:3` with its **existing** collector, not a duplicate. If accessible, review `407:5/6` geothermal captions, `407:7` 2023 date and `418:5` Hilo geography for on-page integrity.

**Regression validation:** `node qa/media-recovery/validate_usgs_407_418_eight_20261109.cjs qa/media-recovery/usgs_407_418_eight_20261109.json` and `node qa/media-recovery/test_usgs_407_418_eight_20261109.cjs`; **27/27 isolated V8 control/mutation checks passed** against the same audit/validation logic before commit. Native Node CI and actual guest Chromium have **not** run. No deployment authorization is implied.
