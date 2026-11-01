# Hebgen Lake post 407 — USGS eight-image repair-readiness custody and image-weight QA

**Audit:** 2026-11-01. **Ownership:** Media Recovery PR #183, separate from Site QA PR #154 and the interim homepage visual-design lane. Source-only, unmerged; no WordPress uploads or edits, third-party image copying, paid requests or homepage changes.

## Evidence actually obtained

Read-only authenticated WordPress `posts.get(id=407, context=edit)` returned published post [The Lake Wasn't There Yesterday](https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/), last modified `2026-10-29T18:30:30`. All **8 exact `<img src>` URL strings and complete ALT strings** matched `qa/media-recovery/parts/02.json` (Git blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`). All eight use the USGS-controlled `d9-wret.s3.us-west-2.amazonaws.com` source host.

The earlier independent web image retriever displayed the **existing** URLs for slots **407:0, 407:2, 407:4, 407:5, 407:6, 407:7**. It could not display **407:3** and rejected **407:1** with unsupported `binary/octet-stream`; the repository's web retriever describes this as unsupported content type, **not a verified visitor HTTP 400 or a browser 404**. For 407:1, the official USGS item page links an alternate **Original** JPEG `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg` that the prior independent viewer displayed. The published URL is instead `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg`. **Neither binary equality nor logged-out browser rendering has been established**. New web retriever attempts on November 1 could not access the alternate image or 407:3; don't mistake those limits for a public outage.

| Slot | USGS archival record | Source credit / pictured year | Identity level and action |
| --- | --- | --- | --- |
| 407:0 | [House in Hebgen Lake](https://www.usgs.gov/media/images/earthquake-damage-1959-hebgen-lake-event-yellowstone-plateau) | USGS Yellowstone / 1959 | Official-described historical scene; current viewer displayed; verify ALT's extra broken-roadway claim visually. |
| 407:1 | [Fault scarp](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) | J. R. Stacy, USGS / 1959 | **P0 alternate Original path** exists; comparison and guest Chrome required. |
| 407:2 | [Madison Slide, Aug. 21](https://www.usgs.gov/media/images/view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake) | Professor William B. Hall, Montana School of Mines / Aug. 21, 1959 | Existing viewer displayed, publication rights still HOLD for credit and exact image. |
| 407:3 | [Outlet dragline](https://www.usgs.gov/media/images/dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959) | Mrs. Steven W. Nile / Oct. 18, 1959 | **P0 retriever-inconclusive stored URL**; do not substitute another engineering photo. |
| 407:4 | [Golden Gate rockslide](https://www.usgs.gov/media/images/rockslide-damage-golden-gate-area-near-mammoth-hot-springs) | USGS/NPS contextual source / 1959 | Original catalog URL previously exact-matched; current viewer displayed. |
| 407:5 | [Sapphire Pool](https://www.usgs.gov/media/images/sapphire-pool-upper-geyser-basin-erupting-after-1959-hebg) | USGS Yellowstone / after 1959 | Original catalog URL previously exact-matched; do not invent precise exposure date. |
| 407:6 | [Seismic Geyser](https://www.usgs.gov/media/images/seismic-geyser-eruption-1970) | John Brandow, USGS / **1970** | Original catalog URL previously exact-matched; ALT's extra formation-cause claim merits editorial review. |
| 407:7 | [Earthquake Lake and Madison Slide](https://www.usgs.gov/media/images/earthquake-lake-and-madison-slide) | Mike Poland, USGS / **June 27, 2023** | Modern aftermath photo, not original disaster coverage. |

All eight USGS catalog pages mark **Public Domain**, but the photographer credits for Hall and Mrs. Nile especially warrant checking third-party underlying rights, exact-photo identity and attribution. A catalog-level rights label is not final asset-specific editorial/legal approval.

## Conditional 960-pixel dimensions, not binary measurements

The frozen WordPress editor stores intrinsic HTML attributes for **407:2 = 1024×719**, **407:3 = 1024×730**, and **407:7 = 1024×771**. If decoded approved exact masters match those geometries, proposal: **960×674**, **960×684**, and **960×723** respectively. Treat these as **conditional** because markup dimensions are not proof of actual original file dimensions. Other five originals have no verified intrinsic dimensions and remain NULL. Never upscale or replace a smaller pre-existing image solely to reach 960px.

## Guest browser and cache release sequence

1. Site QA #154 owns guest logged-out Chrome: on post 407 scroll each section and collect source-slot screenshot, active `currentSrc`, final Image request GET/redirect/status/content-type, `naturalWidth/Height`, encoded bytes, and desktop/mobile LCP/CLS. First target **407:1**, then **407:3**, before wider checks. Do not count a retriever's unsupported octet-stream as a guest failure.
2. Media Recovery verifies exact authoritative catalog/source filename, photograph/crop identity, binary SHA-256, source photographer, chronology, individual reuse/attribution conditions, original dimensions and suitability. For 407:1, compare the USGS Official Original alternate with the existing file **without assuming matching bytes or frames**.
3. Only for a proven broken or meaningfully overweight image with rights cleared, stage approved exact-photograph derivative at **min(960px, true master width)**, with aspect ratio preserved, quality review, source credit and predictable responsive `srcset/sizes`. Never change captions/history automatically, and never cache unknown copyrighted third-party content. Avoid replacing already-small archive JPEGs with heavier files.
4. Compare real same-page transfer before/after (cache state, network throttling, same viewport/scroll coverage, same image set and decoded identity), not Media Library originals. WP/Jetpack may already serve smaller variants. **76% reduction not measured** and **42 reported broken assets not guest-verified**; the 13 originals >1.5 MiB represent media-storage bytes, not necessarily transferred bytes.

## Machine-readable guarded files

- `qa/media-recovery/hebgen_407_usgs_custody_20261101.json` — all eight exact published URLs/ALTs, USGS records, alternate candidate, viewer results, credit, years, 960px conditional dimensions, visitor network NULLs and explicit WordPress/copyright HOLD.
- `qa/media-recovery/validate_hebgen_407.cjs` — deterministic crosswalk against frozen post and viewer inventory; fails closed on fabricated HTTP, fake 42/76% statistics, copyright approval, identity changes, upscaling or unauthorized CMS writes.
- `qa/media-recovery/test_hebgen_407.cjs` — one positive exact-source case and 35 negative mutation cases. **36/36 pass in isolated V8 re-execution of the exact GitHub-committed Node test source with Node API shims**. Native Node CI/live browser were **not run**.

**No production media replacements, no license assumptions, no copy of restricted images, no homepage edits, no subscription expense.**
