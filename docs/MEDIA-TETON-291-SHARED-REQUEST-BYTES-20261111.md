# Shared CDP image requests: a real 76% measurement blind spot (Nov 11, 2026)

**Isolated media-recovery engineering only.** No website edits, image binaries, WordPress media, caching, publishing, deployment, merges or subscriptions.

## Exact-source example from the archived published Teton post
The source-bound [six-slot audit](../qa/media-recovery/teton_291_six_nara_byui_identity_20261110.json) establishes that **291:2 and 291:5 are two DOM image positions pointing to the identical Deseret News/Arc CloudFront source**:

`https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG`

It does **not** prove how many requests a real browser makes. Normal HTTP cache/request coalescing could allow one completed CDP Image request to satisfy both positions. Conversely a browser can make two requests. The old evaluator required unique request IDs per DOM slot, rejecting valid coalesced evidence and creating pressure to miscount each position's encoded bytes as a separate transfer.

## Correction
The source-only module [measure_image_transfer_pair_20261111.cjs](../qa/media-recovery/measure_image_transfer_pair_20261111.cjs) now accepts shared `request_id` across distinct slots only if **every completed network field, source URL, pixel geometry, cached state, and visual identity agrees**. It sums `Network.loadingFinished.encodedDataLength` once per unique completed request ID within each capture. Different IDs count separately; conflicting reuse, missing slots, broken responses and cached responses HOLD. Results expose unique request and shared slot counts and remain explicitly single-post, not site-wide.

Synthetic examples: 2 slots using one completed 1000-byte request before and one 200-byte request after yield 1000 → 200 bytes (**80%**). If there are two genuine independent requests in each run, they yield 2000 → 400; both must be measured, never guessed. A capture with only one of the two DOM slots fails coverage.

**This is not an observed visitor traffic figure.** The 42 broken-image claims remain browser-unconfirmed, and the proposed 76% site-wide reduction remains unmeasured.

## Rights, visual and safe restoration constraints
The Deseret source remains third-party copyrighted/rights-unverified, with unknown native dimensions and no approved 960px derivative or WordPress cache plan. Previous source research flagged a likely wrong ALT for **291:2** (dam breach wording on a street-cleanup scene); an editor must review that separately before any caption or image change. Do not hotlink as a workaround, scrape, rehost, or rewrite post blocks.

Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns collecting cold guest CDP evidence. Existing P0 missing-media order stays `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. This evaluator does not implement a competing collector. Site QA should preserve DOM image-to-request lineage, even if several DOM slots share one request. Record full-scroll success, currentSrc, resource type, response/finish, decoding, cache flags and bytes.

Historical inventory **61 posts / 355 images / 288 external** versus expanded **66 posts / 361 inline images** must not be conflated; 15 stored WordPress originals over 1.5 decimal MB total **47,096,779 stored bytes**, not on-wire bytes. Require actual cache-disabled matched before/after browser evidence to test the claimed **76%** reduction.

Regression gate: **32/32 isolated V8 Node-compatible checks** on the patched module and expanded tests. Native Node CI and actual logged-out Chromium pending.
