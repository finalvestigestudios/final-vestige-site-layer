# Media census: cross-article source-slot identity safeguard — 2026-11-08 PT

**State:** Draft-only engineering and offline regression evidence. No production WordPress/image writes, caching, third-party binary retrieval, article-block rewriting, homepage design, or paid services. Existing Site QA PR #154 owns guest Chrome/CDP capture; do not duplicate its collector or evidence intake.

## Reproduced issue (synthetic, before patch)

The shared `image_census_coverage_core.cjs` accepted a supposedly completed article-432 browser census containing a real-looking but **wrong-article** image key `268:0`. That record had a matching source/currentSrc/request URL, 200 image response, 960×540 decoded geometry, and transferred bytes; `assessPage` and `assessRun` both returned `complete:true`. The same misuse with a 404 result counted as an article-432 broken image. Another synthetic page containing one genuine `268:0` plus `268:9` can also appear complete with a declared two-image count; exact consecutive slot inventory is already independently guarded by the frozen-cohort binder in PR #1402, not by this fix.

This is an **offline acceptance bug**, *not* evidence that either article is currently missing images. A result for a different post must not certify or incriminate the article being inspected.

## Change isolated to media recovery draft #183

`assessPage` now checks that every valid stored-image key uses the exact decimal article ID **when `post_id` is present**. A mismatch records `source_slot_post_mismatch`, sets `complete:false`, and prevents any `confirmed_broken_count` from being returned. `assessRun` always supplies a post ID and therefore applies the guard to full guest census exports. The immediate per-page CDP probe invokes `assessPage` before adding `post_id`; this remains an initial, non-final summary and cannot establish run-wide completion. No change was made to Site QA's Chrome collector, P0 network adjudicator, or frozen source binder.

Legacy controls were corrected to use their owning article's key and to include intrinsic height, now required by the existing November 8 geometry guard. No production source URLs were altered.

**Test:** New `qa/media-recovery/test_image_census_post_key_binding_20261108.cjs` contains 12 synthetic positive/adversarial checks: foreign loaded photo, foreign 404, interchanged article evidence, mixed post IDs, numeric-prefix lookalikes, and valid image-free post #1922. Alongside the corrected 18 legacy census, 22 geometry, and 36 existing P0 adjudicator controls, **88/88 exact committed-file tests PASS in isolated JavaScript V8** (test-only HTTPS URL parser and exact-string image identity adapter). These are not Node CI tests or logged-out browser results. Native Node CI and guest Chromium are still required before merging/releasing.

## Exact P0 source URLs remain pinned; no new guest HTTP assertions

Existing immutable audit `qa/media-recovery/p0_guest_browser_disposition_pending_20261105.json`, blob `9bf9a973fce37a546f8c3e79ecd0c34345eb2457`, contains the original six WordPress image URLs, prior **tool-wrapper** outcomes and null visitor HTTP/decoded/wire fields. Examples:
- `285:5` [published Say Media photograph](https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg): prior wrapper 404; source-related [Commons 819×614 photograph](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) *not an authorized exact replacement*.
- `287:5` [former St Pete Catalyst photograph URL](https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg): prior wrapper 404; [same-publisher relocated URL](https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg) is a conditional candidate, not yet rights-cleared or browser-verified.
- `418:2` [USCG Scotch Cap debris original](https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg): prior wrapper 403; do **not** substitute NOAA's possibly misdated 1964 catalog image without image-level comparison against USCG's 1946 event.

**All six guest-browser Image GET HTTP statuses, decoded dimensions, currentSrc and actual wire bytes remain unknown.** This runner's direct curl checks still fail local DNS resolution (HTTP 000), which is not evidence of origin failure.

## Release and restoration rules

P0 order remains `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Site QA #154 should export complete full-scroll, fresh/uncached CDP request IDs and image statuses; use the updated post/slot gate on the full run before deciding whether a reported 404 belongs to the right article. Even a genuinely broken image does not authorize caching or rewriting. Every potential replacement remains HOLD until exact-scene visual identity, item-level reuse rights/credit, and non-upscaled max-960px dimensions are verified; stage a WordPress Media Library plan and rollback separately only after approval.

Inventory and performance claims are unchanged: frozen October 30 **61 posts / 355 image refs**; mixed-date expanded **66 / 361**; recent source-library **15 originals >1.5 decimal MB totaling 47,096,779 stored bytes** (14 >1.5 MiB = 45,553,777). Stored original bytes are not transfer. The original **42 reportedly broken images** remain visitor-unverified and the proposed **76% transferred-byte reduction** is unmeasured. **Production repairs: 0.**
