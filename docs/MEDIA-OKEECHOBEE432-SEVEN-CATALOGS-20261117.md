# Media Recovery — Okeechobee post 432: seven exact Florida Memory catalog records (2026-11-17 PT)

**Scope:** read-only catalog/source provenance; no homepage redesign, browser collector duplication, image downloads/cache/rehosting, WordPress writes, block rewrites, merge/deploy, or paid services.

## Verified catalog progress

Previously only two of seven Florida Memory image slots in [prior 11-slot crosscheck](../qa/media-recovery/primary_rights_11slot_crosscheck_20261116.json) had exact per-item catalog URLs. This batch adds **five** official item matches: **PR04493** (432:0, Woodlawn Cemetery funeral), **RC17068** (432:1, September 1928 flooded Avenue A in Belle Glade), **RC10673** (432:2, demolished automotive garage), **RC04344** (432:4, coffins beside canal), and **RC07668** (432:5, victim burial). Existing **N031889** (432:3, Pahokee Health headquarters) and **MSF-PB11548-001** (432:6, 2001 historic mass-burial-site photograph) are retained. Each official indexed catalog lists exactly the image path already authored in WordPress, providing **7/7 URL/accession-level provenance matches**; no image binaries, HTTP responses, native image dimensions or pixel identity were retrieved. Direct attempts to open Florida Memory pages returned a web retriever 403: do not represent it as origin/guest browser HTTP 403.

## Evidence / catalog URLs

- `432:0` **PR04493** — https://floridamemory.com/items/show/4144 — dated 1928; Funeral service for hurricane victims; Woodlawn Cemetery, West Palm Beach. No scene/date discrepancy in catalog.
- `432:1` **RC17068** — https://www.floridamemory.com/items/show/38362 — dated 1928-09; Flooded Avenue A, Belle Glade. Published ALT broadly says Lake Okeechobee region; catalog more precisely says Avenue A, Belle Glade.
- `432:2` **RC10673** — https://www.floridamemory.com/items/show/33289 — dated 1928; Automotive garage demolished by hurricane, Belle Glade. No scene/date discrepancy in catalog.
- `432:3` **N031889** — https://floridamemory.com/items/show/141398 — dated 1928; State Board of Health headquarters personnel, Pahokee. Post-hurricane disaster-response role is not evidenced by catalog; editorial fact-check HOLD.
- `432:4` **RC04344** — https://floridamemory.com/items/show/27848 — dated 1928; Coffins along bank of canal, Belle Glade, after hurricane. Scene matches archive description.
- `432:5` **RC07668** — https://floridamemory.com/items/show/30741 — dated 1928; Burial of 1928 hurricane victims, West Palm Beach. Scene matches archive description.
- `432:6` **MSF-PB11548-001** — https://floridamemory.com/items/show/340182 — dated 2001; Historic mass burial site, West Palm Beach, photographed in 2001. Archive photo was taken in 2001, not 1928; caption must preserve that chronology.

## Editorial warnings

The archival catalog calls **432:1** Avenue A, Belle Glade (the broader WordPress ALT says Lake Okeechobee region); **432:3** supports 1928 Pahokee State Board of Health personnel, *not the specific claim* of post-hurricane disaster-response headquarters; and **432:6** is a **2001 color-slide photograph of a historic 1928 mass-burial site**, not a 1928 image. Preserve chronology and dignity; any editorial correction requires separate human review and approval. No published post modified.

## Rights and responsive/staging gate

The [Florida Memory collection FAQ](https://floridamemory.com/share/order-info/faq.php), previously checked in the source worklist, describes **Public Domain Mark 1.0** for its images and requests **State Archives of Florida** credit; PDM is a status description, not a new item license. Check each catalog's current rights/creator requirements and crop before any localization. **960px maximum review width, proportional height only after native decoded dimensions are known, no upscaling**. Do not derive pixel dimensions from the catalog's physical photo/slide measurements. No approved binary, no WordPress Media Library asset, and no cached version.

Site QA PR [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) retains its existing **logged-out browser collector**: record exact currentSrc/redirects, numeric GET+MIME, decode, naturalWidth/Height, cache/service-worker state, full-scroll screenshot and CDP image encoded bytes for affected slots. Only after source revision still matches, visible failure, item rights + credit, exact image/crop, SHA-256 of reviewed binary and no-upscale geometry may a separate staging-only review be considered. Avoid automatically rewriting Gutenberg blocks; preserve prior source/captions and plan a reversible post/media rollback.

## Measurement integrity

Historical 61 posts / 355 inline images; **42 reported broken is not browser-confirmed**; proposed **76% visitor-byte savings remains unmeasured**. Count 20 originals >1.5 decimal MB, 64,385,752 **stored** bytes, which cannot be used as CDP transferred bytes. No real client HTTP status, network bytes or cached/uncached comparison was collected in this sprint. Dataset and fail-closed validator are in `qa/media-recovery/okeechobee432_seven_catalog_crosswalk_20261117_0033pt.json` and `qa/media-recovery/validate_okeechobee432_seven_catalog_crosswalk_20261117_0033pt.cjs`.
