# Wikimedia request-width performance triage — 2026-11-08 (draft only)

This audit is **NOT a visitor-browser measurement or a published media change**. It uses the original 61-post / 355-inline-img frozen source inventory pinned by eight Git blob hashes in the JSON ledger. Site QA #154 owns actual guest Chrome/CDP evidence. The six previously prioritized potential broken image slots (285:5, 285:2, 287:5, 418:1, 418:2, 407:1) **remain first**.

## Newly quantified, actionable bounded scope

Of **118** stored Wikimedia Commons `Special:Redirect/file` references across the 61-post source cohort:
- **75** explicitly request `width=1280`.
- **17** explicitly request `width=960`.
- **26** omit a width parameter.
- Among the 75 explicit 1280 requests, **68 are JPEGs** eligible only for review of an *identical Commons file title* requested at `width=960`; **7 are format/detail-sensitive** (4 PNG, 2 WebP, 1 GIF) and held for separate legibility/animation review.

The [official MediaWiki help](https://www.mediawiki.org/wiki/Help:Images/en) documents `Special:Redirect/file` and its `width` parameter with aspect-preserving resizing. This supports a *possible* transport-level optimization without finding a different historical photo. It does **not** establish that any image currently transfers at 1280 pixels, that a 960px response will be smaller for each viewer/DPR, that the native file is at least 960px wide, or that a requested 960px response preserves readable fine detail.

## Safe candidate process

**P0 missing images first.** The 68 JPEG URLs are conditional P1 candidates, not production instructions. For every selected URL Site QA must capture actual `currentSrc`, redirected image HTTP result, decoded width/height, cold CDP transferred bytes, cache flags, viewport and rendered screenshot. Verify each Commons file's item-level copyright/license/attribution and the native master dimensions; **never upscale** a file narrower than 960px. Confirm 960px still renders legibly at the actual layout width and browser device pixel ratio, retain original image/crop, and compare before/after cold transfers on a *complete matched* article cohort. Only after review can an authorized separate WordPress edit be proposed. No blanket `width=1280` to `width=960` rewrite.

Machine source audit: `qa/media-recovery/wikimedia_118_width_960_census_20261108.json`. Offline fail-closed gate: `qa/media-recovery/validate_wikimedia_118_width_20261108.cjs`. Native Node test definitions: `qa/media-recovery/test_wikimedia_118_width_20261108.cjs`.

The historical 42-image failure count remains **unconfirmed in guest Chrome**; the earlier 76% image-weight reduction remains **unmeasured**. Fifteen WordPress Media Library originals above 1.5 decimal MB (47,096,779 stored bytes) have a different denominator from these 118 external-source URLs and are not an image transfer measurement. This isolated work downloads/caches no images, changes no production pages or homepage design, and spends nothing.
