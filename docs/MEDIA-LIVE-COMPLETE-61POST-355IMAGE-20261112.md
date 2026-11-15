# Complete historical Media Recovery integrity census — 61 posts / 355 images

**November 12, 2026 (Pacific); owner: isolated Media Recovery draft PR #1703. No merge, deployment or WordPress changes.** This completes source-level read-only reconciliation across ALL EIGHT frozen PR #183 audit partitions. The seven committed evidence batches cover the original October 30 cohort: 8 + 8 + 8 + 8 + 8 + 8 + 13 = **61 published posts**; 52 + 59 + 49 + 56 + 54 + 49 + 36 = **355 inline image positions**. Exact source URL and ALT content matched **355/355**, with **zero missing or added positions**. Original source provenance and item-specific catalog leads remain cross-linked by slot in the consolidated machine-readable file.

## Verified source and markup position

| Measurement | Read-only historical cohort result |
|---|---:|
| Original WordPress source URLs unchanged | 355 / 355 |
| Original ALT text unchanged | 355 / 355 |
| Historically offsite/third-party origin positions | 288 |
| Historically first-party positions | 67 |
| Images with missing raw HTML width **and** height | **305 / 355 (85.9%)** |
| Images with both raw dimension hints | 50 / 355 |
| Partial width/height pairs | 0 |
| Literal source `srcset` attributes | 0 |
| Offsite source positions with candidate catalog mappings | 278 |
| Candidate positions with conditional ≤960px dimension leads | 152 |
| Guest-browser HTTP statuses confirmed | **0** |
| Guest-visible broken images proven | **Unknown** |
| Guest image-transfer savings measured | **Unknown** |

The 305 missing HTML dimension pairs are a real **stored markup observation**, not proven layout shift: theme/container CSS or runtime rewriting may reserve aspect ratio. Likewise, lack of literal `srcset` does not establish which resource a browser downloads; WordPress, Jetpack and proxies may transform source at runtime. Avoid automatic Gutenberg block edits.

## Backlog priority: visual recovery first

Keep Site QA PR #154 as the **sole** guest CDP collector. First six exact image positions: `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Record cold visitor actual request URL, redirect statuses/lineage, response MIME/status, decoded natural width/height, currentSrc, CSS display size × DPR, transferred bytes, and on-page rendering. Only label failed after a complete request-to-render trace, ruling out disabled retriever wrappers, cache, lazy-load omission and intentional placeholders. No second collector.

Where a failure is proven, map the original exact scene to Navy History/Heritage Command, Coast Guard history/museum, Florida Memory, USGS, Library of Congress or other primary catalogs; verify item-specific rights (including donor restrictions), precise historical date, pixel/scene/crop fidelity, accurate attribution and candidate native resolution. No commercial-use permission should be inferred simply from a government-hosted URL. Stage a rights-reviewed 960px-or-lower variant only if it meets actual CSS×DPR demand, without upscaling, and preserve high-resolution map/diagram labels. Keep the original URL, checksum and rollback manifest; no automated rehosting or mass media rewrites.

## Storage and claimed reduction

15 WordPress originals strictly above **1.5 decimal MB** total **47,096,779 stored bytes**; 11 are inline in eight published posts and four require page/featured-media investigation before classifying unused. Five 1672×941 PNGs in posts 34–38 are **13,267,538 stored bytes**, zero pre-generated subsizes; those are *stored originals*, not actual visitor transfer measurements. The reported **76% weight reduction** remains a hypothesis: compare matched cold baseline/variant screenshot and image-wire bytes on the same route, viewport, DPR, disabled caches and image source identity, inspect legibility, and use a weighted by transferred-bytes formula; only then claim real measured savings.

## Engineering verification

[355-row consolidated exact-source/rights audit](../qa/media-recovery/live_61post_355image_integrity_consolidated_20261112.json); [offline validator](../qa/media-recovery/validate_consolidated_355_20261112.cjs); [adversarial Node tests](../qa/media-recovery/test_consolidated_355_20261112.cjs). Source audit uses seven pinned Git blobs, each produced with authenticated read-only WordPress content and frozen-image identity comparison. Validator replays original slots against all seven source batches and the 288-slot register, recomputes 61/355/288/67/305/50 counts, and rejects false browser statuses, copyright clearances, unauthorized rehosting or production changes. Native Node CI and actual logged-out Chrome remain pending unless separately executed; the isolated JS control checks do not equal browser QA.

No third-party media binaries were fetched, cached or mirrored. No WordPress uploads, post rewrites, homepage design changes, merges, deployments or subscription spend.
