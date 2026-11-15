# Frozen image-source baseline reconciliation — 2026-11-15

**Scope:** image provenance and performance only. This is an offline read-only evidence correction in existing media draft #183; Site QA #154 owns guest-browser checks and its own CSV. No homepage design work or WordPress production changes.

## Resolved 286-versus-288 offsite count discrepancy

The frozen 2026-10-30 inventory, rechecked across eight exact-source JSON parts, contains **61 posts / 355 inline image slots**. Grouping source URLs by their *underlying media origin*, not just CDN hostname, gives:

| Source | Count |
|---|---:|
| Direct first-party finalvestige.com | 60 |
| Jetpack image proxy of **finalvestige.com** media | 7 |
| Direct third-party sources (including 118 Wikimedia redirect URLs) | 286 |
| Jetpack proxy of **third-party** media | 2 |
| **Total third-party dependencies** | **288** |

The Site QA #154 snapshot CSV instead sums to **286 offsite**. All 61 per-post image totals match; **two** per-post offsite counts are one low: **post 285** (5 instead of 6) and **post 291** (5 instead of 6). The disputed slots are:

- **285:1**, exact published URL: `https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1`. The Jetpack hostname is not evidence that the origin is owned by Final Vestige. The underlying remote origin is `www.squawkpoint.com`; image-specific creator rights remain unknown.
- **291:0**, exact published URL: `https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1`. The underlying origin is the National Archives blog, not Final Vestige. The [NARA article](https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/) lists Jerry Dursteller's collapse-series photograph, including [NAID 28894685](https://catalog.archives.gov/id/28894685), as an official archival candidate. It is **not** a proven pixel-identical replacement.

Current #154 classifier source appears capable of classifying both remote-origin Jetpack URLs as external, so this is a **stale/inconsistent snapshot CSV**, not a demonstrated flaw in its current classifier. Site QA should independently regenerate its file; media recovery did not write to #154.

Both live WordPress post edit views still contain these exact URLs as of this audit (posts 285 and 291, modified 2026-11-02). **No actual image-request status, `currentSrc`, `naturalWidth`, origin HTTP status, response bytes, or logged-out guest failure was observed.** Therefore this affects *dependency counting*, **not** the still-unverified assertion that 42 images are broken.

## Rights and safe repair queue

NARA's own [publishing policy](https://www.archives.gov/research/still-pictures/publish-photos) notes that some photographs held in its archives can have third-party copyright restrictions and that rights clearance is the user's responsibility. Its Teton Dam story names Dursteller as a private-contractor photographer. **Do not infer U.S.-government-work public domain status from NARA hosting.** The Three Mile Island squawkpoint photo likewise has no verified creator license or same-scene authorized master.

No download, mirror, WordPress Media Library upload, crop or Gutenberg block rewrite is authorized. Pending successful cold-browser evidence, request item-level reuse rights and original dimensions, confirm pixel/scene identity and credit, then calculate only a proportional **maximum 960px width without upscaling**. Dimensions are intentionally null while native sizes remain unknown. Use a reversible staging-only WordPress media plan with preserved original URL and ALT/caption; visually compare before/after and measure actual paired CDP transfer bytes before proposing a release.

## Performance denominators and QA

The separate latest WordPress media snapshot (2026-11-15) has **132 image attachments**, **90,403,013 stored-original bytes**, and **20 originals strictly larger than 1,500,000 decimal bytes**, totaling **64,385,752 bytes**. Four new oversized featured images are not the corresponding published *inline* sources. These attachment storage bytes cannot support a visitor-network 76% reduction claim; the original 61/355 census and expanded 66-post site count must not be intermingled.

- Machine-readable exact URL, counts, rights, status and 960px HOLD: [`frozen_61_proxy_origin_delta2_20261115.json`](../qa/media-recovery/frozen_61_proxy_origin_delta2_20261115.json).
- Offline independent origin validator: [`reconcile_jetpack_origin_20261115.cjs`](../qa/media-recovery/reconcile_jetpack_origin_20261115.cjs). Requires all eight frozen source parts and rejects unexpected divergence.
- Native Node unit suite: [`test_reconcile_jetpack_origin_20261115.cjs`](../qa/media-recovery/test_reconcile_jetpack_origin_20261115.cjs). Standalone execution **12 passed, 1 skipped** (full eight-part fixture absent in the isolated local runner); the full repository integration case must run in CI. The eight source parts were independently read back and aggregated via GitHub connector: **61/355, 288 offsite**, 2 remote Jetpack sources.
- Site QA #154 owns six original P0 visitor checks: 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. Media Recovery does **not** duplicate that browser collector.

**Claim gate:** 42 broken originals remain unconfirmed in guest Chrome. A site-wide 76% byte reduction remains unmeasured. No change to the production site, images, homepage, media library, rights state, merge, deployment or subscription spend.
