# Media recovery — framing-integrity regression and three P0 origin observations (2026-11-18, 15:24 PST)

**Draft QA only.** Scope is the media recovery lane, not homepage aesthetics. Production WordPress is untouched. Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns logged-out Chromium and existing browser export; recovery draft [#2747](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2747) consumes those exports. Do not instantiate a parallel browser collector.

## Concrete defect fixed

The existing Jetpack photo-identity guard could accept `?crop=left` in place of `?crop=center`, or newly added `?zoom=2`, despite the authored source pointing to the same file. These transformations can remove vital historical content while leaving `source_identity` unchanged. The existing parity evaluator imports `image_wire_source_guard_20261118.cjs`, which imports `jetpack_source_identity_20261118.cjs`; fixing `sourceMatches` in the latter enforces same-phase source checking, and adding `sameFraming` directly to the existing parity evaluator also blocks **before/after authored URL changes** that preserve the original `source_identity`. No browser collector is duplicated.

**New rule:** an authored Jetpack `crop` or `zoom` must be preserved exactly in the selected `currentSrc` and final response; adding, removing, or changing either is a HOLD. Preserve the literal upstream publisher query too. Normal Jetpack width, resize, fit, quality and strip transformations are still permitted by the source identity validator, subject to independent visual and ratio checks. This is a conservative safety guard, not proof of pixel equality, rights clearance or correct caption.

**Tests:** 17 new native Node 22.16.0 framing regressions passed, alongside 24 mirrored existing Jetpack identity regressions, total **41/41** in an isolated local directory. Two new cross-phase parity integration tests were committed but have **not** been executed. The locally mirrored helper is semantically equivalent to the committed patch, and the committed source/test blobs were read back from GitHub; native whole-tree execution and full integration against exact committed GitHub blobs have **not** been performed. The pre-existing 76% parity gate's unrun integration tests and Site QA guest Chromium remain release blockers. Check GitHub blob SHAs on the draft branch before relying on a built artifact.

## Actual original-source URL probes — November 18, 2026

Exact original URLs and statuses are in `qa/media-recovery/source_404_framing_hold_20261118_1524.json`. Three sources yielded **HTTP 404 in an independent public retriever**:

- **285:5, Three Mile Island:** `https://images.saymedia-content.com/.image/ar_16%3A9%2Cc_fill%2Ccs_srgb%2Cfl_progressive%2Cq_auto%3Aeco%2Cw_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg`. Movie-related image: do **not** replace with an unrelated historical reactor photograph. No exact licensed counterpart established.
- **274:6, USS Tang:** `https://www.warhistoryonline.com/wp-content/uploads/sites/64/2016/04/uss_tang_ss-306_rescues_airmen_off_truk_in_1944-640x432.jpg`. Navy accession [80-G-227989](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227989.html), with [Commons scan](https://commons.wikimedia.org/wiki/File:USS_Tang_(SS-306)_rescues_airmen_off_Truk_in_1944.jpg), is a research lead, **not proven identical pixels/crop or item-level rights approval**. Commons 1910×1288 scan has an approximately 960×647 derivative.
- **287:5, Sunshine Skyway:** `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg`. [Florida Memory RC09237](https://floridamemory.com/items/show/32083) is a **different photograph** from the documentary still; automatic substitution is disallowed. Its precise original pixel dimensions and item-specific reuse status remain unverified.

**Important:** a public-retriever origin 404 is *not* a verified Jetpack 404 or broken visitor image. The published proxy responses were inaccessible to this retriever; actual visitor final URL, image decode, natural dimensions and transfer bytes remain `null`. No fake browser measurements or manufactured 42-item list.

## Release methodology and backlog

The original [archived worklist](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2747) (Git blob `9cdf7af84175883775aaebf55ffa5ca77b33e423`) records a historic 61-post / 355-image source census; Site QA's earlier 286 offsite-source result and the newer 288 for shared 61 posts are reconciled by snapshot drift, not source breakage. The current 66-post census has 361 inline image slots. The **42 broken visitor images remain unverified**.

The 20 WordPress originals larger than 1.5 MB represent **64,385,752 stored bytes**, not observed browser transfers. The alleged **76% savings have not been measured**. Use Site QA's existing desktop and mobile cold CDP waterfall export with cache and service-worker disabled. Match the exact 61-post baseline or separate 66-post cohort; require full per-slot request-ID evidence and positive image decoding after recovery. Reject counting an HTML 404 error body as image download. Report before/after bytes and LCP/CLS only when measured, plus trace SHA and visual review.

For each genuinely broken image, first establish exact-photo and caption identity and verify item-level public-domain/licensed usage; do not infer rights from archive hosting alone. Secure approved master and hash **only after** rights review. Generate responsive proportional derivatives at **max 960px**, never upscale, retain caption/date/credit, stage as a WordPress media candidate with original post blocks unchanged, compare rendered guest desktop/mobile screenshots, keep the original URL and reversible rollback plan. No production upload, no automated scraping, no speculative replacements, no subscriptions and no Gutenberg bulk rewrites.

**Release decision:** HOLD until real guest failures and trace-backed savings are established and editorial rights/framing checks clear.
