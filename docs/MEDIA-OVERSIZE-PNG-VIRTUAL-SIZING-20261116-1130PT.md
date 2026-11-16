# Oversized original media vs. actual WordPress VIEW source — 2026-11-16 11:30 PT

**Scope:** independent, read-only media performance / missing-image engineering. No homepage-design work, CMS writes, binary downloads, license assumptions, plugins, deploys, merges, or payments. Existing Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns the cold logged-out guest browser collector.

## Fresh live evidence

Read all **132 WordPress image-library media records** (100 + 32, ID descending), each `media_details.filesize`, native width/height, `source_url`, `sizes`. **20 originals exceed 1,500,000 stored bytes**, summing to **64,385,752 stored bytes**. These are original media files, **not** proven visitor network downloads. This 132-item library census is **not** the 61 published-post/355 inline-reference historical cohort, nor the later 66/361 post cohort.

The five published first-party original PNGs below total **13,267,538 stored bytes** (20.6% of the 20 oversized originals). Each has **no `sizes` entries** in the WordPress media API, but the exact published post VIEW image tag has **`src=https://i0.wp.com/finalvestige.com/...png?resize=1024%2C576&ssl=1`**. Consequently the blanket claim that these pages necessarily download each 2.5–2.9 MB full original is **unsupported**. They all include explicit inline `width=1024` and `height=576`, an ALT and `loading=lazy`; none includes `srcset` or `sizes` in the inspected inline tag. The original PNGs are 1672 × 941. Jetpack resize can deliver a different number of network bytes from storage size; neither browser decode nor HTTP response has been measured here.

| WP media / published post | Original stored bytes | Actual WordPress VIEW image source |
| --- | ---: | --- |
| 39 / [34, San Francisco fire](https://finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/) | 2,892,087 | [Jetpack 1024×576 proxy](https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png?resize=1024%2C576&ssl=1) |
| 40 / [35, James Caird](https://finalvestige.com/2026/08/16/the-boat-that-refused-to-die/) | 2,552,136 | [Jetpack 1024×576 proxy](https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png?resize=1024%2C576&ssl=1) |
| 41 / [36, Vicksburg](https://finalvestige.com/2026/08/16/the-city-that-went-underground/) | 2,498,247 | [Jetpack 1024×576 proxy](https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png?resize=1024%2C576&ssl=1) |
| 42 / [37, Petra](https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/) | 2,488,823 | [Jetpack 1024×576 proxy](https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png?resize=1024%2C576&ssl=1) |
| 43 / [38, SF cistern](https://finalvestige.com/2026/08/16/the-cisterns-beneath-san-francisco/) | 2,836,245 | [Jetpack 1024×576 proxy](https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png?resize=1024%2C576&ssl=1) |

**Rights / image fidelity:** WordPress media captions identify these five as *AI-assisted historical reconstructions*, not documentary evidence. Existing rights / upstream asset authorship must be established separately; keep documentary-vs-reconstruction labeling and existing ALT/caption integrity. Nothing here clears publication of a new derivative. Metadata-derived **960×540** is a review-only target (not a downloaded, generated or decoded image); no upscaling, no crop alteration without visual review.

## Proposed safe remediation — gated, not performed

1. Site QA #154 reuses its existing collector for *cold guest* screenshot, `currentSrc`, numeric image GET status, MIME, naturalWidth/Height, transfer bytes, mobile/desktop viewport, and measured CLS/LCP if applicable. These five do **not** outrank the six earlier suspected P0 broken third-party images (285:5, 285:2, 287:5, 418:1, 418:2, 407:1).
2. Confirm if actual 1024×576 Jetpack response is healthy and effectively compressed. If so, **do not replace merely because original is large**. If measurable transfer / responsive harm remains, assess approved 960×540 modern format *offline* from an owned, rights-cleared master, preserve originals/ALT/caption, and compare sharpness, crop, credibility, and mobile presentation. No external licensing or unlicensed scraping.
3. Any later reversible WordPress staging review must record post revision, exact binary SHA-256, decoded dimensions (max 960px width, no upscaling), attribution, current markup and complete rollback. Production publishing requires separately granted authorization; never bulk rewrite Gutenberg blocks. No automated cache/upload.
4. **76% savings claim:** only calculate from the same cold-guest page list and viewport set, full lazy-scroll and per-request CDP transferred bytes for before vs staged after, including redirects/Jetpack and visually verified image decode. Formula: `(sum(before_image_wire_bytes)-sum(after_image_wire_bytes))/sum(before_image_wire_bytes)`. Report uncertainty and denominator; do not use these original stored sizes or divide average per-page percentages.

## Reproducible offline QA

- [Machine-readable 132→20→5 evidence](../qa/media-recovery/oversize_20_five_png_runtime_20261116_1130pt.json)
- [Fail-closed offline checker](../qa/media-recovery/assess_oversize_20_five_png_runtime_20261116_1130pt.cjs)
- [37-case native-Node-compatible suite](../qa/media-recovery/test_oversize_20_five_png_runtime_20261116_1130pt.cjs)

Commands in a checked-out repository:

```sh
node qa/media-recovery/assess_oversize_20_five_png_runtime_20261116_1130pt.cjs
node --test qa/media-recovery/test_oversize_20_five_png_runtime_20261116_1130pt.cjs
```

**Execution truth:** 37/37 baseline/negative test functions were executed under isolated V8 against the exact generated assessor and audit bytes before commit. Native Node / repository CI were **not** executed in that precommit environment. The test source is Node-compatible and does not use network, CMS mutation, or media downloads. A successful metadata QA run would not establish browser failures, actual savings, rights approval, or a published fix.

Historical **42 reportedly broken third-party images remain unconfirmed in actual guest Chromium**. Both the reported 76% weight reduction and this five-PNG subset's actual visitor bytes are **unmeasured**. No production changes.
