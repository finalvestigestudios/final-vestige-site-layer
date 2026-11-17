# Okeechobee 432: seven-source archival recovery and canonical-host transport audit — 2026-11-04

**Branch:** `qa/media-recovery-reviewed-20261030-1158` (draft PR #183); **scope:** media engineering, not homepage design or Site QA PR #154. **Production changes: ZERO.** All seven direct images are recorded in the Oct 30 frozen WordPress-source inventory, `qa/media-recovery/parts/01.json` Git blob `948bc1b65b42799aa40cfdb810ddf6ffd80886b6`. The published post was **not** freshly fetched from WordPress on this pass; runtime Jetpack rewriting may differ.

## Specific, replicable finding: seven of seven `www` origins redirect to apex in a text retriever

The exact archived published image URLs all use `https://www.floridamemory.com/fpc/...`. On **2026-11-04**, independent `web.open` requests for **all seven** reported a **tool-level 500** because the URL redirected to `https://floridamemory.com/fpc/...`, which the retriever could not access. Directly probing the seven apex URLs also returned "URL ... not accessible via this tool." **No verified numeric origin GET/HEAD status; no confirmed image decode or browser failure.** This is a real, *observed host-migration transport dependency*, not proof of seven broken photographs or an HTTP 500 at Florida Memory.

| Slot | Exact archived origin path (prepend `https://www.floridamemory.com`) | Authoritative item | Date | Editorial / visual check |
|---|---|---|---|---|
| 432:0 | `/fpc/prints/pr04493.jpg` | [PR04493](https://floridamemory.com/items/show/4144) | 1928 | Woodlawn Cemetery funeral service; archive metadata supports description. |
| 432:1 | `/fpc/reference/rc17068.jpg` | [RC17068](https://floridamemory.com/items/show/38362) | September 1928 | **New precision candidate:** archive specifies **Avenue A in Belle Glade**, omitted from broad ALT. |
| 432:2 | `/fpc/reference/rc10673.jpg` | [RC10673](https://floridamemory.com/items/show/33289) | 1928 | Automotive garage destroyed in Belle Glade. |
| 432:3 | `/fpc/general/n031889.jpg` | [N031889](https://floridamemory.com/items/show/141398) | 1928 | **Unsupported chronology:** archive identifies State Board of Health headquarters and personnel, not "disaster-response headquarters *after* the hurricane". |
| 432:4 | `/fpc/reference/rc04344.jpg` | [RC04344](https://floridamemory.com/items/show/27848) | 1928 | Coffins along a Belle Glade canal; retain sensitive but factual depiction. |
| 432:5 | `/fpc/reference/rc07668.jpg` | [RC07668](https://floridamemory.com/items/show/30741) | 1928 | West Palm Beach burial; exact archive item confirmed. |
| 432:6 | `/fpc/msf/MSF-PB11548-001.jpg` | [MSF-PB11548-001](https://floridamemory.com/items/show/340182) | **2001** | Modern documentation of a 1928 mass burial site; **not** a 1928 eyewitness photograph. Make the 2001 capture explicit in caption/alt review. |

**Matching strength:** Each archival *item page* supplies the same exact `/fpc/...` image path and identifier as the stored source. This does NOT prove that redirected binaries decode in Chrome, that a CDN serves identical pixels, or that the site's current live HTML still uses the Oct 30 source.

## Copyright, captions, and derivative sizing — ALL HOLD

Florida Memory's [copyright/disclaimer](https://floridamemory.com/learn/about/disclaimer.php) expressly places responsibility for use on researchers. The State Archives' [ordering guidance](https://floridamemory.com/discover/photographs/refpricelist.php) requires proper citations in reproduced publications. Its [digitization guidelines](https://floridamemory.com/learn/about/guidelines.php) describe ownership-transfer prerequisites for digitization, but are **not a license grant to this website**. The collections include both state and private records; **no blanket public-domain or commercial rehosting claim** is entered. Individual clearance and precise State Archives/Florida Memory item attribution remain required before caching or WordPress uploads.

Intrinsic JPEG pixel dimensions have **not** been retrieved or decoded for these seven photos. Each conditional candidate is therefore **`max_width_px: 960, height_px: null, no_upscale: true`**. Do not turn physical print/negative sizes (inches) into guessed pixel dimensions. Do not download third-party images, request paid reprints, or generate substituted art.

For approved source binaries only, suggested **staging workflow**: freeze old `currentSrc` and ALT/caption; get rightsholder permission or satisfactory item-specific rights evidence; obtain source without scraping/prohibited access; calculate SHA-256; decode native width/height; derive proportional <=960px responsive version (smaller native widths stay native); preserve meaningful cropping, chronological notes, original archivist credit, and layout dimensions; compare screenshots and actual CDP image-transfer bytes under matched desktop/mobile cohorts; get a separate deployment authorization. No risky block rewrites.

## Handoff without duplicate QA

Site QA PR #154 retains its established P0 queue **285:5/285:2 → 287:5 → 418:1–2 → 407:1**. After those, add post **432** as a **single-host 7/7 fanout scenario**. Test one original `www` image and its apex target, then all seven if failure reproduces; capture logged-out Chrome final request chain/status/MIME, `img.currentSrc`, `naturalWidth/Height`, `decode()`, pixel/crop comparison, screenshots, and cold transferred encoded bytes. **An archive catalog that loads does not prove that its image direct URL loads.** Escalate only browser-confirmed failures.

## Regression evidence

- [Seven-item machine ledger](../qa/media-recovery/okeechobee_432_canonical_redirect_20261104.json) records every original and redirected URL, archival catalog, original ALT, item date, explicit **null** HTTP/MIME/dimension/byte observations, rights hold and conditional sizing.
- [Fail-closed offline validator](../qa/media-recovery/validate_okeechobee_432_20261104.cjs) pins source URLs, catalog items, counts and transport semantics and prevents passing invented browser status, image dimensions, transfer bytes, copyright clearance or WP writes.
- [23-case positive/adversarial test suite](../qa/media-recovery/test_okeechobee_432_20261104.cjs): **23/23 PASS against exact committed GitHub files in isolated V8 CommonJS-compatible runner**; native Node CI and guest Chromium remain unexecuted.
- Baseline remains **61 investigations / 355 source references / 288 external original references / 13 oversized WordPress originals**, not newly recounted. The reported **42 broken** is not visitor-browser validated; **76% real transfer savings is unmeasured**. **Production repairs: 0.**

No external image binary downloads, WordPress writes, homepage visual changes, changes to #154 scripts or subscription charges occurred.
