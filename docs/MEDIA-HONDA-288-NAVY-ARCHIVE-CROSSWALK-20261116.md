# Honda Point post 288: six-source Navy archive crosswalk — HOLD

Observed November 16, 2026, 17:22–17:44 PST. Read-only provenance investigation. This is an isolated media recovery batch, **not** a second Site QA browser collector or a public website change.

Authenticated WordPress EDIT and VIEW of [The Bearing Was Right](https://finalvestige.com/2026/08/19/the-bearing-was-right-honda-point/) (post 288, modified 2026-08-19 14:37:40) agreed on six inline sources. VIEW rewrites all six to Jetpack proxy URLs. All six VIEW image elements lack explicit width, height, srcset and sizes; real layout shift is unmeasured. The adjacent machine manifest preserves the **exact twelve authored/VIEW URLs** and null guest statuses.

## Primary-source crosswalk

| WordPress image | Authored source and independent public retriever | Identified primary Navy catalog | Catalog high TIFF size → conditional no-upscale 960px target |
|---|---|---|---|
| 288:0 | NHHC long-path JPG; retriever tool 502 | [NH 69586](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69586.html), Fuller/Woodbury; Naval Historical Foundation and Admiral Pratt collection | 6256×4862 → **960×746** |
| 288:1 | Ahoy photo rendered; visible original photo heading names NH 69059 | [NH 69059](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69059.html), Delphy/Nicholas, San Francisco Maritime Museum courtesy | 6250×4904 → **960×753** |
| 288:2 | NHHC historic radio station direct JPG; retriever tool 502 | [UG 21 collection](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/ug-collection/ug-21-us-naval-california-radio-station-collection.html); individual photo still unverified | Unknown |
| 288:3 | NavSource photo rendered; visible photo heading names NH 84820 | [NH 84820](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-84000/NH-84820.html), S.P. Lee/Nicholas; Aston photograph donated by Capt. Grening | 6146×5130 → **960×801** |
| 288:4 | HyperWar/ibiblio photo rendered; visible photo heading names NH 84822 | [NH 84822](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-84000/NH-84822.html), Chauncey/Young; Aston photograph donated by Capt. Grening | 6158×4992 → **960×778** |
| 288:5 | U.S. Naval Institute image rendered | No item-level primary catalog match established | Unknown |

**Four of six authored images rendered in the independent public retriever; two Navy originals yielded tool 502. All six Jetpack proxy URLs were inaccessible to the retriever.** These outcomes do **not** establish what a logged-out FinalVestige visitor sees. A tool 502 is not a recorded visitor HTTP 502. Numeric guest image GET status, request MIME, currentSrc, decoding, screenshot, natural dimensions, cache and transferred bytes remain entirely **NULL**.

## Rights and image fidelity

[NHHC's official photo archive policy](https://www.history.navy.mil/our-collections/photography.html) states that *most* its images are public domain, not all; photographic donations, museums and individual rights notes must be checked. The accession catalog listings include relevant Naval Historical Foundation, San Francisco Maritime Museum and Aston/Grening credits. Follow [NHHC's reproduction guidance](https://www.history.navy.mil/about-us/instructions-and-forms/obtain-duplications-of-records-and-photos.html). Treat all item-level rights, exact pixels/crop and cache/rehost permissions as **HOLD** until verified.

The three third-party photo files with accession headers have embedded title strips. Navy catalog renditions may not preserve the same text, frame or crop; compare originals against prospective replacement visually before any editorial decision. The U.S. Naval Institute image's “aerial” ALT/viewpoint wording merits human review, **not** an automatic rewrite. The four 960px dimensions are **calculations from the official high-TIFF catalog metadata**, not measurements of downloaded masters or final JPEG/WebP.

## Strict future staging and rollback procedure

1. Keep the **existing Site QA #154 browser collector**. After the six already-prioritized P0 images, collect guest Chromium GET/redirect, MIME, currentSrc, successful decode, image dimensions and cold-cache transfer bytes for post 288. Never infer failures from this retriever alone.
2. Select an actual confirmed broken slot, compare exact scene/crop/header to the NHHC record, document item-level copyright/donor rights, accepted credit and any non-endorsement restrictions. A different scene is only a proposed editorial substitution, not a drop-in repair.
3. Only with explicit authorization, obtain the licensed file to isolated **staging**, compute SHA-256 and native decode geometry, preserve embedded contextual text where needed, then export proportionally up to 960px (without upscaling) plus responsive 320/640 widths when feasible. No speculative mirroring, automated scraping, or unlicensed rehosting.
4. Pin the original post revision and backed-up Gutenberg image block; stage only the approved image's minimal change, preserve captions/link destinations and ALT accuracy. Review desktop/mobile appearance, first meaningful paint, content shifts, lazy-load behavior and transferred bytes. Define exact rollback to the original image markup. Do **not** write to WordPress production without a separate explicit change authorization.

## Scope and QA evidence

A native Node test run on the exact JSON, validator and 26-case test source passed **26/26** (one baseline + 25 adversarial mutations), including rejecting manufactured HTTP success, invented bytes, copyright release, aspect distortion, mismatched proxy origin, pixel identity, and write authorization. All three byte-identical files are committed under qa/media-recovery in isolated draft [PR #2747](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2747); this document belongs to the same draft. Repository CI is not claimed.

Keep historical **61 posts / 355 image references / 286 directly offsite** separate from the later 66-post inventory. The **42 reported breaks remain guest-browser unconfirmed** and **76% visitor bandwidth reduction unmeasured**. The 20 original files above 1.5MB sum to **64,385,752 stored bytes**, not visitor wire traffic. docs/IMAGE-WEIGHT-WORKLIST.md was absent from checked main and media branch.

**Zero live image changes, WordPress writes, media downloads, cache/rehost, homepage edits, Gutenberg block rewrites, merges, deployments or subscription spend.**

