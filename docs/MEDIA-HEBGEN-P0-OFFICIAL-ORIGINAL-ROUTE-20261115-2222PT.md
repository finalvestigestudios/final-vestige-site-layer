# P0 Hebgen fault scarp: verified official Original route, no production action

Date: 2026-11-15 22:22 Pacific. Independent Media Recovery QA draft #183; Site QA owns guest Chromium/CDP collector in #154. No homepage design ownership or changes.

## What changed materially

WordPress post **407 image 1 (zero-based), 407:1**, currently renders `https://i0.wp.com/d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg?ssl=1`, which proxies the authored legacy upstream `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg`. The **official USGS item catalog** [Hebgen Lake fault scarp in 1959](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) identifies **J. R. Stacy (USGS)** and states **Public Domain**. Its **Original** link resolves to `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg` — a different S3 path that includes **/thumbnails/image/** and the same basename `img7535.jpg`.

A public image reader **rendered the official Original**. The upstream legacy path returned an *unsupported binary/octet-stream* tool response; the Jetpack URL was *tool-inaccessible*. These are three different **retriever outcomes**, **not HTTP status codes**, no conclusive browser failures, and not a causation proof. The official file is incident- and filename-matched, but **exact pixel/frame identity has not been proven** by hashes or a side-by-side guest screenshot. No image was downloaded or rehosted. All numeric visitor HTTP, transferred-byte and decoded-dimension fields remain `null` in [machine audit](../qa/media-recovery/usgs_hebgen_407_1_official_original_route_20261115_2222pt.json).

## Reversible restoration candidate / release gates

1. Keep **P0 six** priority order in Site QA's existing collector: 285:2, 285:5, 287:5, **407:1**, 418:1, 418:2. Capture 407:1 logged-out cold Chrome desktop/mobile: actual `currentSrc`, response status/redirects/content-type, `naturalWidth/Height`, bytes, and screenshot; test official Original in the same run without creating a new browser collector.
2. Compare the failed delivered frame and official Original visually. Record exact image identity, USGS attribution **J. R. Stacy / USGS**, item-level public-domain record, and any WordPress-specific reuse/caching review. Distinct route and matching basename alone are not exact-pixel proof.
3. Only after original dimensions are verified, compute no-upscale **width = min(960, sourceWidth); height = round(sourceHeight × width / sourceWidth)**. No prefilled 960px height/width claims. Proposed WebP/JPEG derivative and **WordPress Media Library staged cache** require explicit signoff; no remote hotlink swap or blanket proxy bypass. Preserve ALT, adjacent caption, reading order and image relevance. Stage one slot, compare guest screenshots, then separately authorize publish with rollback path to stored source. No global Gutenberg block rewrite.
4. This report is **evidence-only**. No CMS write, image download, WordPress upload, PR merge, deployment or subscription spend is authorized.

## Baseline accounting

Historical 61 published posts / 355 image tags and updated 66 / 361 are **different snapshots**, not contradictory tallies for one cohort. A reported **42** broken originals remain **guest-browser unconfirmed**; the proposed **76%** transfer saving remains **unmeasured**. Twenty WordPress originals >1.5 MB total **64,385,752 stored bytes**, which cannot be substituted for browser network bytes. Use the existing [cold-wire assessor](../qa/media-recovery/assess_cold_wire_savings_20261115.cjs) only after real matched CDP exports.

Offline guard: [validator](../qa/media-recovery/validate_usgs_hebgen_original_route_20261115_2222pt.cjs) and [regressions](../qa/media-recovery/test_usgs_hebgen_original_route_20261115_2222pt.cjs) reject synthesized HTTP status, premature 960px dimensions, unapproved caching and fictional savings. The validator reads only the JSON and performs no HTTP requests.
