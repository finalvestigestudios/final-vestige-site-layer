# Final Vestige third-party image origin resilience — 2026-11-09

## Verified and newly reconciled
All **eight Oct 30 source files** (61 published posts, 355 images) matched all **50 distinct, nonoverlapping researched exact URLs** in existing Drafts **#1703 (43)** and **#1723 (7)** with **zero source URL discrepancies**. 288/355 slots have an upstream origin outside Final Vestige, spanning 80 hosts; **238** have no dedicated archival-recovery investigation. Distinct stored URLs across all 355 source slots: **353** (not real browser request count).

**Crucial Jetpack correction:** exactly **NINE** raw tags are delivered through `i0.wp.com`; **SEVEN** proxy original images are genuinely Final Vestige first-party (Vasa post 299), and **TWO** are external upstream origins (Three Mile Island 285:1 Squawkpoint; Teton Dam 291:0 NARA). These TWO were already classified `external` in the frozen JSON; do not claim that all nine have `jetpack_proxy` source_kind. This is the precise basis for 288 rather than Site QA's initial 286 offsite risk count.

| Upstream host | Offsite image slots | Investigated | Still pending source research | Posts |
|---|---:|---:|---:|---:|
| commons.wikimedia.org | 118 | 13 | 105 | 20 |
| upload.wikimedia.org | 18 | 0 | 18 | 10 |
| www.history.navy.mil | 15 | 15 | 0 | 4 |
| d9-wret.s3.us-west-2.amazonaws.com | 9 | 1 | 8 | 2 |
| cdn.loc.gov | 7 | 0 | 7 | 2 |
| tile.loc.gov | 7 | 0 | 7 | 4 |
| www.floridamemory.com | 7 | 7 | 0 | 1 |
| www.nps.gov | 6 | 0 | 6 | 1 |
| images-assets.nasa.gov | 5 | 0 | 5 | 1 |
| media.defense.gov | 5 | 1 | 4 | 3 |
| cloudfront-us-east-1.images.arcpublishing.com | 4 | 0 | 4 | 3 |
| objects.lib.uidaho.edu | 4 | 0 | 4 | 1 |

The 118 `commons.wikimedia.org` redirect references span 20 posts; only 13 have prior source research. This is upstream concentration, **not** a claim 105 visitor errors. Navy source hosting has 15/15 source records across the two existing drafts, and Florida Memory has 7/7; none are browser-verified as failed or loaded.

## Safeguards and operational priority
[Machine-readable 288-row URL/host/observations/candidate ledger](../qa/media-recovery/offsite_upstream_288_20261109.json) preserves literal source URLs, exact stored source slot, delivery versus actual upstream hostname, wrapper-only retrieval observations and archival catalog/copyright/960px information (where available). All visitor statuses, decoded dimensions and wire byte fields are NULL; wrappers are **not** genuine origin or visitor HTTP. No image is cleared for copying or publishing. User-visible 42 failed images remain unverified; 76% visitor-transfer saving unmeasured. 15 WordPress originals >1.5 decimal MB = 47,096,779 stored bytes, NOT transfer bytes.

Keep **Site QA #154 sole owner** of its existing real-browser collector and P0 priority six: **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. Then sample correlated Florida Memory post 432 and Navy posts 274/370. For a truly failed image, collect the actual guest Chrome source/currentSrc, final uncached HTTP and MIME, decoded width/height, request ID/bytes, screenshots and exact-scene source identity; review item-specific rights and credit, ≤960px no-upscale geometry (preserve map and scientific labels), WordPress staging rollback before separately approved production changes. Do not duplicate the #154 collector or #183 wire-comparison logic.

## Evidence
All eight original immutable Git blob SHAs and both external recovery-ledger blob SHAs are preserved in the JSON; 32-bit fingerprint `dc27c388` is only an accidental-drift guard, **not** cryptographic proof. Validator recomputes upstream rollups, blocks visitor/savings fabrication, forbidden releases, invented rights and invalid 960px sizing. **23/23 precommit isolated V8 mutation/control checks passed**; native Node CI and real visitor Chromium outstanding. Files added only to existing isolated Draft **#1703**. **No external media downloads, caches, WP writes, homepage design changes, subscriptions or spend.**
