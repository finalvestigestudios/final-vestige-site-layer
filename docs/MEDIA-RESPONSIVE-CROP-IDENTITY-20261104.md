# Media Recovery — crop-preserving source identity, 2026-11-04

## Scope and critical finding
PR #183's offline browser identity classifier previously treated every static-photo `resize=` value as *size-only*, discarding it when comparing a stored historical image with a runtime `currentSrc` or redirected CDP image response. That is not safe: a resizing endpoint may **crop** rather than only proportionally scale. The documented WordPress Site Accelerator behavior explicitly distinguishes `?resize=W,H` (exact dimensions with crop) from `?fit=W,H` (preserve aspect ratio). Reference: https://developer.wordpress.com/docs/developer-tools/site-accelerator-api/ . This is a *conservative identity rule*, not a finding that all third-party `resize` endpoints crop.

Specific frozen source example: Iroquois Theatre post **283**, image **283:3**:
`https://bloximages.chicago2.vip.townnews.com/enidnews.com/content/tncms/assets/v3/editorial/b/4e/b4e59e84-74da-5f9e-b24f-5e9e3658fd34/54716e12ac97b.image.jpg?resize=1200%2C804`

The post's previous authenticated read-only CMS and independent-renderer audit in `iroquois_283_visual_custody_20261104.json` records 7/7 sources and ALT strings matched the pinned October 30 part 03. The exact TownNews rendition was inaccessible to a non-browser retriever. **Actual visitor browser status, naturalWidth, currentSrc, final CDP response and transfer bytes are all unknown. Do not equate this with a verified 404.** The 1200×804 parameter is a *requested rendition*, not verified intrinsic dimensions.

## Engineering change
`browser_probe_core.cjs` now retains `resize` as a content-affecting selector in `imageIdentity` / `sameSource`, while keeping proportional `fit` size-only and already-preserved `crop` and photo-ID query selectors. An unchanged crop across i0/i1 Jetpack delivery hosts remains comparable. Comparing an uncropped master with a crop-capable rendition, or different resize geometries, fails closed as `current_src_identity_unverified`. A cross-host redirect ending at a different filename remains `redirected_image_identity_unverified`, not a verified broken historical original—even with an HTTP failure in the synthetic fixture.

Existing tests covering crop and redirect behavior were amended for the corrected policy; new synthetic tests explicitly pin the exact 283:3 source URL. These tests assess comparator code and synthetic CDP states only, **not actual guest browser visibility, transferred bytes or image quality**.

## Safe visual restoration decision
Site QA PR #154 keeps logged-out Chrome inspection ownership, without duplicated browser scripts. Investigate P0 **285:5 → 285:2 → 287:5 → 418:1–2 → 407:1** first, then Iroquois 283:3 if confirmed high-risk. For 283:3 record exact live `img.src/currentSrc`, full redirect chain, final Image GET status/MIME, decode/natural dimensions, screenshot including crop and cold CDP image bytes. Verify whether WordPress/Jetpack has rewritten the stored TownNews source before judging breakage.

A Northwestern/Chicago History Museum *subject-matched* ICHi-36007 is **not** an approved binary-identical replacement. Source access does not establish commercial reuse rights. No scraping/caching/rehosting is authorized. Once an exact rights-cleared asset is independently obtained, stage locally; derive **at most 960 px wide, no upscaling** based on decoded master dimensions (height unknown today), maintain aspect ratio and accurate captions, preserve source/credit and original URL for rollback, perform staged side-by-side visual review and CDP byte measurement. **WordPress production writes remain prohibited.**

## Sitewide claims
Historical baseline remains **61 articles / 355 slots / 288 offsite-origin references**; **13 WordPress originals >1.5MiB** total **43,522,829 stored bytes**, not guest transfers. **42 broken images unverified** as visitor failures; **76% image-wire saving unmeasured**; **zero production image repairs**. No new media binaries, licensing assumptions, homepage changes or spend.
