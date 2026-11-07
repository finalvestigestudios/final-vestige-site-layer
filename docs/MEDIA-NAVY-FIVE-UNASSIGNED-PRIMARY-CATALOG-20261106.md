# Five unresolved U.S. Navy source photographs — catalog gap closure (November 6, 2026)

Scope: This batch is a **five-slot follow-up** to the already committed 15-image Navy ledger, **not five additional distinct images**. It is separate from Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) and Media Recovery [#1228](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1228). It changes no posts, media assets, theme, homepage, or affiliate creatives.

## Identity adjudication

| Slot | Source article | Official catalog candidate | Provisional preview, from archival master only | Gate |
|---|---|---|---|---|
| 274:1 | USS Tang | [80-G-227987](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-g-227987-uss-tang--ss-306-.html) | 960 × 1163 | Published binary/crop unknown |
| 274:2 | USS Tang | [NH 84498](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-84000/NH-84498.html) | 960 × 753 | Photo shows **two** torpedoes; ALT only refers to Mark 18-2 |
| 280:1 | USS Pueblo | [NH 75559](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75559.html) | HOLD — catalog '1280×1280' is rendition label, not true native geometry | Do not generate square crop |
| 280:4 | USS Banner | **No exact match.** [NH 68705](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-68000/NH-68705.html) and [NH 68710-KN](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-68000/NH-68710-KN.html) are subject-only 12 May 1969 alternatives | HOLD | Neither 1969 photo identified as the embedded original; do not imply 1968 scene |
| 288:2 | Honda Point radio context | [UG 21-01.02](https://www.history.navy.mil/our-collections/photography/technology/communications/radio/ug-21--us-naval-california-radio-station-collection/mare-island-naval-radio-station/ug-21-01-02-mare-island-naval-radio.html) | 960 × 1212 | Glass-negative collection provenance; equipment is not direct evidence of 1923 DF event |

The 960-pixel sizes are **mathematical projections from catalog high-master dimensions**, not decoded pixels for the embedded WordPress images and not generated or approved files. Exact source URLs and existing ALT preserved in the [machine audit](../qa/media-recovery/navy_five_gap_closure_20261106.json). There are **four subject/catalog candidates, zero exact published binary matches, and one unresolved original (Banner)**. The original 15-image ledger remains the source of the five published src URLs; frozen blob SHA `fda8819e86771cfd03a55a9ff252618127b0e420`.

## Reuse rights / authorization

NHHC [photo policy](https://www.history.navy.mil/our-collections/photography.html) notes most images in its archive are public domain **but each image's use and attribution remain the researcher's responsibility**. The Tang image is an official U.S. Navy photograph in National Archives custody; USS Banner archival photographs are noted 'Courtesy of USS Banner'; UG 21 is a found-in-collection glass negative. **All five stay ITEM-LEVEL RIGHTS HOLD**. Preserve official catalog credit, original ALT and historical date. Do not mirror third-party images, automate downloads, change WordPress blocks or assume the binary at the current source URL matches the catalog file.

## Site QA and restoration sequence

Site QA #154 already owns the logged-out Chromium/CDP collector; **do not duplicate it**. Keep P0 failures at 285:5, 285:2, 287:5, 418:1, 418:2, 407:1 ahead of this P2 catalog cleanup. When one of these Navy sources is actually broken in a guest browser, collect the actual runtime currentSrc, request-id/response status, MIME, naturalWidth/height, redirection, cached flags and cold encodedDataLength. Confirm the original archival image subject/crop visually before asking for item-level rights review. Only then propose a copyright-cleared, aspect-safe, no-upscale 960px maximum candidate in a nonproduction staging WordPress media object; verify caption, ALT, screenshot, responsive layout, performance pair and rollback. **No production WordPress writes are authorized.**

## What the results do not establish

No origin or guest-browser HTTP codes, bytes, actual visitor failures or bandwidth reduction were measured. The historical **42 broken-image report is unconfirmed**, and the **76% image transfer saving is unmeasured**. The prior 61-post/355-slot snapshot is superseded for current article coverage by 66 published posts/361 stored inline slots; these are source counts, not browser-transfer figures. Thirteen WordPress originals >1.5 MiB / 43,522,829 bytes refer to **stored originals**, not visitor wire bytes.

## Reproducibility

Run `node qa/media-recovery/validate_navy_five_gap_closure_20261106.cjs` and `node --test qa/media-recovery/test_navy_five_gap_closure_20261106.cjs`. The suite contains 21 fail-closed scenarios with deliberately corrupted rights, HTTP and source data. Independent catalog verification performed against official Navy records; network image bytes not copied.
