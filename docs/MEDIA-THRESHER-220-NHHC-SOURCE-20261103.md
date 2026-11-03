# USS Thresher / post 220: seven exact source URLs, Navy archival custody and safe restoration hold

**Evidence timestamp:** 2026-11-03. **Isolation:** Media Recovery draft PR #183, not Site QA #154 or homepage. **Original WordPress snapshot:** frozen 2026-10-30 `qa/media-recovery/parts/05.json` Git blob `9b16b828342a9ac338f3e65610fd3d8d508355e9`; post 220 modified 2026-10-29T18:25:46 at snapshot. **This was not a fresh authenticated WordPress read.**

## Retrieval findings (not a claim of visitor failure)

Every one of the **seven exact published** `commons.wikimedia.org/wiki/Special:Redirect/file/...` URLs returned an *internal error / unavailable response through the independent web.open retrieval wrapper*. **No origin numeric HTTP code was returned**, and no logged-out Chromium image GET, DOM `currentSrc`, `naturalWidth`, `decode()`, MIME, encodedDataLength, redirect-chain or screenshot has been obtained. All seven **separate Commons catalog HTML pages were accessible**, with original image dimensions and custody descriptions. A catalog page loading does not prove that the `Special:Redirect` image stream or the FV page loads. The alleged 42 site-wide broken images remain unverified; **do not add seven** to that count.

**Full immutable seven-row audit:** [thresher_220_navy_custody_20261103.json](../qa/media-recovery/thresher_220_navy_custody_20261103.json), which reproduces exact frozen URLs and ALT texts, explicit null browser/HTTP fields, links to primary Navy provenance, proposed no-upscale dimensions and HOLD controls.

## Historical-source and image-truth map

| Slot | Primary custody / Commons image relationship | Commons original | Conditional web derivative | Important qualification |
|---|---|---:|---:|---|
| 220:0 | [NH 97545](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97545.html) official bow-on photograph, July 24 1961 | 4918×6136 | **960×1198** | Published redirect requests 1280px; target dimensions reduce pixels, not verified transfer bytes. Vertical aspect must not be distorted. |
| 220:1 | [NH 97552](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97552.html), July 9 1960 launch | 740×574 | **740×574** | No upscaling; larger Navy high rendition does not prove same crop. |
| 220:2 | [NH 97310](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97310.html), USS Skylark halftone | 578×737 | **578×737** | Late-1950s/1960s promotional image, not known to be photographed on April 10 1963; item belongs to Christopher P. Cavas collection. |
| 220:3 | [NH 97567](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97567.html), August 24 1963 Trieste seafloor watertight door | 740×532 | **740×532** | A contemporaneous wreck-survey scene, not a photo of the initial sinking. |
| 220:4 | Commons [Trieste II mid-1964](https://commons.wikimedia.org/wiki/File:Bathyscaphe_Trieste2_2.jpg); related [USN 1084706](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/USN-1084000/USN-1084706.html) is **different image** | 1700×1349 | **960×762** | Commons image derives from NavSource and describes reconfigured mid-1964 Trieste II; official Navy USN 1084706 shows a January 16 1964 crane/commissioning scene. These are not interchangeable. Also not the original 1963 Trieste. |
| 220:5 | [NH 97570](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97570.html), brass pipe recovered by Trieste | 739×574 | **739×574** | Navy source dates original release to September 13 1963; include hull inscription only as caption-supported. |
| 220:6 | [NH 97557](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97557.html), upper rudder on seabed | 740×576 | **740×576** | Dated **October 1964**; Navy site's high TIFF label **4870×6084** is portrait while Commons derivative is landscape; do not assume full-resolution exact crop or same orientation without inspecting both. |

**Image rights are not resolved by archive custody alone.** Commons calls these Navy public-domain items, and [NHHC Photo Archives](https://www.history.navy.mil/our-collections/photography.html) says *most*, not all, images are public domain. Navy items 220:0/1/3/5/6 have strong item-level official-photo provenance; 220:2 needs attention to the donor halftone and 220:4 to the NavSource origin. Appropriate item credit, derivative policy and the difference between a photo and a reproduced/modified version must be reviewed. `rights.item_specific_signoff=false`, `copy_allowed=false`, `credits_reviewed=false` deliberately remain closed in every ledger row.

## Staging-only WordPress media/caching plan (no approval to execute)

1. Site QA #154 should **preserve its existing P0 queue** (285:5, 287:5, 418:1–2, 407:1). After that, run a logged-out Chrome guest pass on 220:0–6. Scroll each image into view; capture the exact original `img.src` and final `currentSrc`, Image request ID, redirect chain, final status/MIME, decoding and natural dimensions, cache/service-worker flags, CDP bytes, and a screenshot. A Commons file-description response must not be accepted as an image.
2. If an actual failure is verified, inspect the authoritative Navy image and the Commons exact source **visually**; determine whether 220:6's orientation discrepancy reflects catalog metadata or materially different imagery, and whether 220:4 is the right later-survey scene. Never silently replace with an approximate Naval archive alternative.
3. Independently approve rights and credit **per file**. Download **only authorized** source binaries, in a controlled nonproduction workflow; retain SHA-256, source URL, access date, original dimensions, rights decision and crop description. Do not scrape mirrors.
4. Test conditional 960px/no-upscale derivatives at **960×1198 for the tall bow photo** and **960×762 for Trieste II**; retain smaller originals' pixel sizes. Evaluate WebP/AVIF *only with* JPEG fallback, perceived fidelity and true encoded transfer measurements. Do not claim 76% download savings based on area or archival TIFF masters.
5. Stage in WordPress Media Library or approved first-party cache/CDN with `srcset`, `sizes`, stable dimensions, lazy loading below the fold, preserved caption/ALT and explicit credit. Record 200/image MIME and `decode()` after final origin/CDN URL, visually compare on mobile/desktop, and keep the exact prior external URL for rollback.
6. **No production WordPress writes, remote-image copying, automatic block rewrites, homepage design changes or spending** under this sprint.

## QA engineering evidence

- [Validator](../qa/media-recovery/validate_thresher_220_20261103.cjs) pins all seven source URLs/ALTs to the frozen archive and each primary catalog ID and source-image dimension. It fails closed on fabricated HTTP values, browser bytes, 42/76% claims, fake rights clearance, nonidentical Navy/Commons swaps, incorrect geometry and premature WordPress approval.
- [Regression suite](../qa/media-recovery/test_thresher_220_20261103.cjs) has **28 assertions** (baseline plus 27 adversarial mutations). It passed replayed from the **exact GitHub-committed sources** using an isolated V8 CommonJS shim. Native Node CI and guest Chrome **not executed**.
- Claimed site-wide reference baseline remains **61 posts / 355 slots / 288 external-origin / 13 originals >1.5MiB**, with **0** confirmed production image repairs and **0** measured site-wide 76% savings.

**Action priority:** This is a *P1 archive-source and visual-integrity readiness batch*, not proof of another seven outages. Keep P0 visitor-facing missing images first.
