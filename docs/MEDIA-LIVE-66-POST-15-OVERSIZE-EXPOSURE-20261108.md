# Final Vestige — live oversized-media exposure, 8 November 2026 (source-only)

## What changed in this sprint

The **full current published-post source** was inspected read-only, not merely the media library's attachment-parent metadata. WordPress `posts.list(status=publish)` supplied 66 posts; `posts.get(context=edit)` was read for **all 66 posts in seven bounded batches**. The media library image listing now contains **122** entries (one more than the preceding 121-image snapshot). Its oversized count is **unchanged**: 15 originals strictly above **1,500,000 decimal bytes**, together **47,096,779 stored original bytes**.

This source-to-use reconciliation found **11 oversized originals referenced by inline `<img>` tags across exactly eight published posts**, together **38,480,915 bytes of their stored originals**. **Four** originals, together **8,615,864 stored bytes**, had **no matching inline image** in these 66 published posts. Those four are NOT proved unused: they may be on pages, as featured art, in other post types, or in galleries. Do not delete or modify them.

The frozen October 30 comparison remains **61 posts / 355 image tags**. The contemporaneous expanded site has **66 published posts / 361 image tags**. Source HTML/WordPress metadata is neither visitor CDP, image download success, nor measured page weight.

## Concrete affected published posts and media IDs

| Published post | Original media IDs >1.5 MB in its inline HTML | Source relationship | Next safe action |
|---|---|---|---|
| [34 — Morning San Francisco Lost Its Water](https://finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/) | 39 | Original PNG, no WP subsizes | P1 guest image/rights/960px visual review |
| [35 — The Boat That Refused to Die](https://finalvestige.com/2026/08/16/the-boat-that-refused-to-die/) | 40 | Original PNG, no WP subsizes | P1 guest image/rights/960px visual review |
| [36 — The City That Went Underground](https://finalvestige.com/2026/08/16/the-city-that-went-underground/) | 41 | Original PNG, no WP subsizes | P1 guest image/rights/960px visual review |
| [37 — How Petra Made Water Flow Through Stone](https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/) | 42 | Original PNG, no WP subsizes | P1 guest image/rights/960px visual review |
| [38 — The Cisterns Beneath San Francisco](https://finalvestige.com/2026/08/16/the-cisterns-beneath-san-francisco/) | 43 | Original PNG, no WP subsizes | P1 guest image/rights/960px visual review |
| [269 — The Watch Lost Its Hands](https://finalvestige.com/2026/08/18/the-watch-lost-its-hands-halifax-explosion/) | 1714 | Original 1280x1280 historical map; WP subsizes exist | P1 map-label legibility, item copyright and actual currentSrc |
| [299 — Thirty Men Were Enough](https://finalvestige.com/2026/08/19/thirty-men-were-enough-vasa/) | 389, 388, 382 | Inline HTML uses first-party Jetpack `fit=1024` URL, not original source | P2 check *actual* transfer, licensing and image detail; do not attribute full originals |
| [621 — Six Miles an Hour](https://finalvestige.com/2026/08/19/six-miles-an-hour/) | 1257, 1258 | Raw inline HTML references 4.8MB and 5.55MB JPEG originals | P1 logged-out CDP to rule out runtime responsive replacement |

The **five PNGs** above have a combined **13,267,538 original storage bytes**, from 1672x941 art with no media library subsizes: conditional <=960x540 images, only after source-creator rights and historical content parity review. The **two Malbone JPEGs** contain 10,352,064 stored original bytes, the **three Vasa JPEGs** 13,318,311, and the **Halifax map** 1,543,002. Sum of these four stored-original groups: **38,480,915 B**. These are *not* bytes downloaded by visitors.

Media IDs **482, 405, 293, 2148** (combined **8,615,864 original B**) are unmatched to published inline images; do not label or delete them as unused. #2148 is the newly added Caernarvon archival photo, with no published-post inline use established. Scan excludes non-post page content, custom post types, featured-image delivery and homepage assets.

## P0 broken-image priority and Site QA division of work

First resolve guest-visible failures of 285:5, 285:2, 287:5, 418:1, 418:2, and 407:1. Source-only independent retriever errors on these URLs **do not constitute actual origin/guest HTTP responses**. The historical **42 reportedly broken** image count remains unverified.

Site QA draft PR #154 **owns the existing guest Chromium/full-scroll collector and network attribution**. Media Recovery draft PR #183 supplies the exact WordPress source dependencies, candidate provenance/rights, and this source-to-use mapping. No competing browser collector should be created.

For those six P0 slots and then the eight posts above, Site QA should record `currentSrc`, final browser Image request URL/ID/HTTP/MIME, `naturalWidth` and `naturalHeight`, cache/service-worker flags, `encodedDataLength`, desktop/mobile screenshots, full scroll and visible ALT/image parity. **Guest CDP is currently absent**, so both a 42-broken count and a proposed **76% weight-reduction figure are UNMEASURED**.

## Release and cache plan (non-executable pending explicit approval)

1. Confirm the exact visual/scene identity and item-specific rights. Archival hosting does not automatically confer public domain. Capture item-level permission, credit, photo date and crop/alteration context. For Navy donor collections and Florida Memory images, do not assume rights from domain alone.
2. For approved first-party originals or individually cleared third-party masters, prepare a staging-only derivative: proportional longest useful width **<=960px, never upscale** (and preserve legible archival maps and scientific diagrams even when 960px is too small). Keep original hashes and an exact old/new URL + ALT/caption ledger; no binary downloads in this sprint.
3. For approved WordPress-managed assets, plan a distinct media item and correct responsive `srcset`/dimensions, ensuring local WP/CDN cache behavior actually helps guest pages. Preserve the historical scene and inline block identity. Do not rewrite entire Gutenberg posts; no WP production writes are authorized.
4. Require page-specific logged-out browser before/after checks and two paired cold-network samples using the **existing** evidence collector and Media Recovery wire comparator, for fixed viewport/browser/requests. Confirm images decode and LCP/CLS/alt do not regress.
5. Compute transfer savings from **actual browser-attributed image bytes**, not these original storage sums. Zero guest traces were collected here, so the site-wide 76% hypothesis remains unvalidated. Stage rollback plan before any later approved release.

## Evidence, scope and limits

- [15-row machine-readable readback](../qa/media-recovery/wp_122_media_66_posts_oversize_usage_20261108.json); [fail-closed validator](../qa/media-recovery/validate_wp_122_media_66_post_oversize_usage_20261108.cjs); [regression tests](../qa/media-recovery/test_wp_122_media_66_post_oversize_usage_20261108.cjs).
- Input media-size ledger: `qa/media-recovery/wp_live_121_15_decimal_threshold_20261108.json`, frozen Git blob `223d598d244ff496e861f8330346b341cec29fae`.
- The latest 122-image listing introduces a **small** new media record; threshold totals remain 15/47,096,779.
- This was an authenticated **read-only** WordPress source scan, not a live guest HTML/browser capture. The source-to-use mapping was cross-checked against all 66 published posts and read back on all eight implicated posts. Page/featured custom locations are not exhaustively assessed.
- All replacements/rights determinations held. **0 production repairs; 0 WordPress writes; 0 image binaries downloaded/cached; 0 homepage design changes; $0 spend.**
