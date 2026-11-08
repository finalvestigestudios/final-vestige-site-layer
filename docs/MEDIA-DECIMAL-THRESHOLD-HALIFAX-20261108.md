# FV media — 2026-11-08: literal 1.5 MB threshold gap and Halifax map P1

**Scope:** Fresh, authenticated, read-only WordPress media.list pages 1 and 2 (100 + 19 image records), raw published post 269 and media.get 1714. No media downloads, production edits, draft/production post rewrites, homepage design, paid services or external cache/mirror. Complements Site QA draft #154 and existing image-performance draft #1402.

## New concrete result

| Metric | Exact threshold | Current records | Stored **original** bytes |
|---|---:|---:|---:|
| Decimal megabytes (MB) | >1,500,000 bytes | **15** | **47,096,779** |
| Binary mebibytes (MiB) | >1,572,864 bytes | **14** | **45,553,777** |

The difference is **one previously omitted asset**, not an outage: WordPress media **1714** at `https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png`, **1,543,002 bytes**, **1280×1280**. The prior 14/45,553,777 MiB statistic is correct **when labeled MiB**; it is not the literal “>1.5 MB” population. All amounts are original-storage bytes, **not** visitor-transferred bytes.

## Published article uses original despite “large” block setting

Post **269**, `https://finalvestige.com/2026/08/18/the-watch-lost-its-hands-halifax-explosion/`, is published. Its raw Gutenberg block specifies `wp:image id:1714, sizeSlug:"large"` but `<img src>` uses the exact full **1280px** original URL. This is a candidate for P1 browser-request sizing, **not** proof the visitor downloads 1,543,002 bytes. Browser runtime may use `srcset`/Jetpack.

A second discrepancy is visible in authenticated API metadata: `media.list` calls the 1024×1024 `large` rendition a **virtual Jetpack** `i0.wp.com/.../halifax-explosion-map.png?fit=1024%2C1024&ssl=1`; `media.get(context=edit)` reports `https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map-1024x1024.png`. No image binary, HTTP response or browser CDP request was retrieved, so **do not assert either URL actually transfers**, nor assume a pre-generated physical 1024 file.

## Historical graphics + rights

Published caption identifies “SyntaxTerror via Wikimedia Commons; public domain.” A **matching source-by-description**, Commons [File:Halifax Explosion map.svg](https://commons.wikimedia.org/wiki/File:Halifax_Explosion_map.svg), credits **SyntaxTerror**, displays the same mapped concepts (built-up 1917 area, coastline, destroyed area, tsunami, submarine net) and states an author public-domain dedication. It describes a **2026 modern reconstruction**, not a 1917 period map. Its cataloged vector file is **3300×3300**, not the WordPress 1280 PNG; original-pixel correspondence, modification lineage and independent rights to any adapted source material have **not** been established. Do not conflate or overwrite. The Commons page cites National Post and Canadian Geographic as visual research sources; retain an item-level copyright/provenance check for derivative material.

**Visual release gate:** Square map with location labels/legend is information-bearing, not decorative. Cropping, flattening complex vector lettering or making it illegible are not acceptable “savings.” Provisional **960×960** max (no crop/no upscale) is *only a trial geometry*. Test whether 1024 or expandable higher-resolution access is needed; preserve all captions and contextual map legends. No downloading, conversion, republishing or CMS edits without approved rights and a reversible map from original WP blocks.

## Evidence/QA order

1. **P0:** Site QA #154 owns the existing logged-out browser collector for 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. Historical “42 broken” is still unverified. Do not build a duplicate collector.
2. **P1:** Request currentSrc, genuine Chrome Image request-ID/final status, encodedDataLength, cache flags, viewport, full-scroll/decoded dimensions, CSS geometry, screenshots of map labels, and image source identity for post 269; compare with 1024 proxy candidate and conditional 960 trial *after provenance approval*.
3. Keep historical **61 posts/355 images** and newer **66 posts/361 images** cohorts separate; the proposed 76% *transferred-byte* reduction is **unmeasured**. Use existing draft comparator with full matched-page evidence; raw original sizes cannot certify savings.

## Machine evidence and re-run

- `qa/media-recovery/decimal_1p5mb_119_media_20261108.json` — all 15 exact URL/byte/dimension records, computed ≤960px geometry, status **null**, rights/write **HOLD**, and the metadata URL disagreement.
- `qa/media-recovery/validate_decimal_1p5mb_20261108.cjs` — offline fail-closed threshold, rights, identity, total and no-fabrication checks.
- `qa/media-recovery/test_decimal_1p5mb_20261108.cjs` — **28 checks**, including 27 corrupted fixtures. All 28 passed against the exact committed files in isolated V8; full native Node and real Chromium not yet run.

```bash
node qa/media-recovery/validate_decimal_1p5mb_20261108.cjs qa/media-recovery/decimal_1p5mb_119_media_20261108.json
node --test qa/media-recovery/test_decimal_1p5mb_20261108.cjs
```

**Production repairs 0 · WP writes 0 · media downloads/caching 0 · homepage edits 0 · spend $0.**
