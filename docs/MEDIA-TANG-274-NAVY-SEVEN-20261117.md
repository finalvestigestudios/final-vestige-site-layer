# USS Tang image recovery — seven exact published source paths (2026-11-17, 23:30 PST)

**Read-only, draft, isolated.** Post [274](https://finalvestige.com/2026/08/19/twenty-four-feet-from-air-uss-tang/), seven image slots, all third-party origins per authenticated November 17 WordPress VIEW slice 5 (Git blob `c0d54c30769b0276a143c2f77b897202d818105f`). No live browser, WordPress writes, replacement downloads, caching, homepage edits, deployment, spending or post-block rewrites.

## Source status (public retriever, not guest Chromium)

| Slot | Original source | Public tool observation | Primary-source match | Identity level |
|---|---|---|---|---|
| 274:0 | Wikimedia thumbnail | Rendered binary; numeric HTTP not reported | Navy NH 42273 | Exact accession in file name; visual/binary still unverified |
| 274:1 | NHHC historical page image | Tool gateway 502 | Navy 80-G-227987 | Subject/caption match only |
| 274:2 | NHHC torpedoes page image | Tool gateway 502 | Navy NH 84498 | Subject match only |
| 274:3 | Warfare History Network Momsen lung | Tool internal error | None | Rights and image identity HOLD |
| 274:4 | NHHC imageDownload | Tool gateway 502 | Navy 80-G-344565 | Accession in imageDownload TIFF path |
| 274:5 | Wikimedia thumbnail | Rendered binary; numeric HTTP not reported | Navy 80-G-227991 | Exact accession in file name; visual/binary still unverified |
| 274:6 | War History Online 640×432 JPG | **Public retriever 404** on exact original URL | Navy 80-G-227989 | Same event/subject, **not confirmed same frame** |

**Critical:** 502 is from the retrieval gateway, not a demonstrated publisher response. The one original 404 does not demonstrate a failure of the Jetpack URL in a visitor's browser. No guest HTTP status, decoded dimensions or cold bytes are known for any slot. The other two original images rendered in the public retriever; neither numeric status was provided. The full unmodified URLs, original alt, and evidentiary classifications are in [the JSON](../qa/media-recovery/tang274_navy_seven_20261117_2330pt.json).

## Official sources and rights

Catalogs: [NH 42273](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-42000/nh-42273-uss-tang--ss-306-.html), [80-G-227987](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-g-227987-uss-tang--ss-306-.html), [NH 84498](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-84000/NH-84498.html), [80-G-344565](https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/wwii/wwii-pacific/japanese-surrender/allied-prisoners-of-war/80-g-344565.html), [80-G-227991](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227991.html), [80-G-227989](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227989.html). NHHC [photo policy](https://www.history.navy.mil/our-collections/photography.html): most items are public domain, except where noted; item-level rights/copyright section controls. Credit NHHC for NH accession, National Archives when stated for 80-G photographs; do not imply Navy endorsement. No third-party publisher copy authorized for mirroring. Official 80-G-344565 says image was **released** September 24 1945, not independently proven taken on that date.

## Sizing and safely cached WordPress plan

- Two already-published Commons source thumbnails have catalog previews at **960×587** (slot 0) and **960×703** (slot 5); master dimensions and full-media SHA-256 not independently verified. These are geometry *candidates*, not generated derivatives. The published slot 6 original names a **640×432** thumbnail; do not upscale it. All other target heights remain unknown until the actual authorized source binary is decoded. Never exceed 960 encoded raster pixels in width; preserve aspect ratio and any smaller original resolution.
- Stage ONLY after item-specific rights, exact-picture identity, lawful source delivery, master SHA-256, decoded dimensions, approved caption/alt and credits, visual comparison and verified user-visible failure/need. Generate <=960-width AVIF/WebP or fallback without mutating picture content. Create an unpublished WordPress media item in an authorized staging environment, record attachment ID, filename, responsive srcset/sizes, cache headers, rollback URL and prior block identity; do not rewrite live raw Gutenberg markup.
- Site QA #154 must use its **existing** logged-out Chromium collector at desktop/mobile: record post/slot, actual `currentSrc`, unique network request ID, redirects, complete HTTP response, MIME, decoded raster and natural dimensions, transfer bytes, screenshot and LCP/CLS before any remediation claim. Compare *the same* visitor configuration before/after. The 76% reduction is **not measured**; 20 oversized original files totaling 64,385,752 stored bytes are not browser transfer measurements.

**QA:** `node --test qa/media-recovery/test_tang274_20261117.cjs` and `node qa/media-recovery/validate_tang274_20261117.cjs qa/media-recovery/tang274_navy_seven_20261117_2330pt.json qa/media-recovery/live_66_view_slice_5_20261117.json`. Fail closed; no network calls.
