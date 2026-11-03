# Hebgen Lake post 407 — eight exact offsite images, official USGS custody, and MIME ambiguity (2026-11-03)

## Evidence boundaries
- Input: **frozen October 30 WordPress source** in `qa/media-recovery/parts/02.json`, blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`; not a fresh November 3 authenticated CMS read.
- Eight exact existing `src` values are all on **USGS's externally hosted S3 distribution**. Independent `web.open` renderer Nov 3 displayed **407:0, :2, :4, :5, :6, :7** (**6/8**), could not fetch exact **407:3** (no numeric response) and classified exact **407:1** as unsupported binary/octet-stream (**retriever wrapper 400**, NOT an established HTTP 400). Neither exception proves visitor-visible failure.
- USGS's own 407:1 catalog links a separate `thumbnails/image/img7535.jpg` rendition, **which visibly rendered**; USGS's 407:3 catalog has a separate `styles/medium/public/media/images/EarthquakeLake3.jpg?itok=CeFY5xC-` rendition, **which visibly rendered**. Both are **first-party USGS delivery variants, not independently licensed Final Vestige rehosts**. The USGS S3 `styles/medium` format is lower-resolution and image identity/crop is not SHA-matched.
- The exact original 407:1 is not proven to return `Content-Type: application/octet-stream` to guests: the web retriever reported unsupported content type, without numeric origin HTTP, MIME header capture, X-Content-Type-Options, or browser `decode()` evidence. A browser may sniff and render despite non-image MIME. Site QA #154 owns proper Chrome verification.
- Independent runner's local DNS fails; do not infer public outage. **No historical photo binaries downloaded**, no unlicensed scraping or WordPress writes.

## Eight canonical USGS catalog matches and source rights
All eight have original source, stored ALT, official canonical USGS catalog permalink, precise method/status, rights and tentative candidate mapping in [the JSON ledger](../qa/media-recovery/hebgen_407_usgs_octet_cross_transport_20261103.json). Official USGS catalog pages all mark **Public Domain**, but that does NOT itself prove exact stored/candidate binaries are the cataloged works or that all third-party photographer rights are automatically exempt. Preserve author/date context and verify item-specific rights/crop before any rehosting:

- **407:0** Grace Miller's submerged house, 1959; catalog USGS/Fact Sheet 2005-3024 (original publisher scene displayed).
- **407:1** original `img7535.jpg` fault scarp; USGS credits **J. R. Stacy**; official separate thumbnail displayed.
- **407:2** rapid lake infill **Aug 21, 1959**, Professor **William B. Hall** (Montana School of Mines), not proven USGS staff. Preserve abandoned camping supplies in description.
- **407:3** spillway-excavation dragline **Oct 18, 1959**, **Mrs. Steven W. Nile** (non-federal credited source); USGS says PD, but item-specific source/rights and original-vs-medium crop require confirmation.
- **407:4** rockslide near Golden Gate, Yellowstone; possible NPS authorship (the second USGS page credits NPS). Do not assume USGS employee capture.
- **407:5** Sapphire Pool eruption post-1959 quake; image photograph date/copyright beyond USGS PD catalog not independently proved.
- **407:6** Seismic Geyser **in 1970**, photographer **John Brandow**; 1970 is historically important, NOT earthquake-night image.
- **407:7** modern **June 27, 2023** Quake Lake landscape, photographer **Mike Poland**; not a 1959 event photo.

## Geometry, caching and staging: HOLD
- Every `source_intrinsic_dimensions_px` is **null** until source Image decode or USGS metadata confirms it. The frozen HTML declared 1024×719 for 407:2, 1024×730 for 407:3, 1024×771 for 407:7; those are layout dimensions **not trusted source-intrinsic dimensions or transferred bytes**.
- Set **maximum 960px, preserve aspect, no upscaling**; cannot calculate honest derivative dimensions from missing intrinsic sizes. Confirm crop and caption in staging before serving WordPress Media or other cache; preserve original and rollback ref.
- After real logged-out Chromium Image GETs, Site QA should record each slot's `src/currentSrc`, status and redirect chain, response `Content-Type` and `X-Content-Type-Options`, `naturalWidth`/`decode()`, completed network bytes, console errors, screenshot, and mobile/desktop outcomes. First prioritize 407:1 and 407:3, after the higher priority P0 images **285:5, 287:5, 418:1/2**.
- An official catalog's PD label is evidence for review, not automatic permission to copy its image to WordPress. If rights/crop/current URL prove sound, *do nothing*. If actual 407:1 is broken, test the official linked thumbnail as a **staging-only** fallback after rights approval, verify its resolution, and keep author/credit. Do not automatically rewrite Gutenberg blocks.
- **No measured guest HTTP responses, decoded widths, transfer savings, 42 confirmed failures, or 76% savings.** 61/355/288 site-wide reference baseline, 13 >1.5 MiB original files, and **0 production fixes** remain unchanged.

## QA
Native Node: `node qa/media-recovery/test_hebgen_407_20261103.cjs` and `node qa/media-recovery/validate_hebgen_407_20261103.cjs`. The isolated JS precommit validator plus 24 deliberate mutation checks passed; native Node CI and logged-out Chrome not run here.
