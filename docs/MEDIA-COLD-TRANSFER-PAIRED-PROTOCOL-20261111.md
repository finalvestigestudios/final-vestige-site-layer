# Media recovery: image-transfer measurement and safe restoration handoff — 2026-11-11

**Ownership:** Draft PR #1703 is media recovery only. Site QA PR #154 owns the existing logged-out Chrome/CDP collector; the interim lead owns homepage visual design. No collector duplication, WordPress writes, image downloads/rehosting, homepage change, merge, deploy or paid subscriptions.

## Source of truth and denominator separation
Read the worklist in PR #183, Git blob `2acd06a4ca4317646006eb6591face3fe76fedec`. The frozen 61-post historical cohort has 355 stored image tags and 288 external positions researched. The expanded 66-post cohort has 361 images. The reported 42 broken images are *not confirmed guest-browser failures*. Do not merge cohorts or turn web-retriever wrapper errors into origin HTTP statuses.

Fifteen WordPress originals >1,500,000 decimal bytes total **47,096,779 stored bytes**; eleven associated with eight published posts total **38,480,915 stored bytes**. Neither figure measures downloaded bytes. Vasa already uses a Jetpack `fit=1024` transform in stored markup. The five PNG originals in posts 34–38 have no generated WP subsizes. Malbone 621 directly links two large originals. Halifax 269 is a map whose fine labels need scrutiny.

## New isolated calculation contract
`qa/media-recovery/measure_image_transfer_pair_20261111.cjs` accepts only pairs of **actual** cold, logged-out, full-scroll CDP capture results for *the same post, image positions, content fingerprint, viewport and device pixel ratio*. It rejects cache hits, MIME=HTML, HTTP error shortcuts, zero/unknown network bytes, missing images, duplicate slots, mismatched photos, changed sources without item rights and visual approval, and incomplete lazy loading.

The only accepted network metric is the CDP `Network.loadingFinished.encodedDataLength` for a successful `Image` request, compared on both sides with identical measurement semantics. The module emits **per-post** reductions, and **always refuses a site-wide 76% claim**. That headline needs full agreed cohort coverage, all corresponding network requests, stable guest conditions, no extra missing images and a separate cumulative aggregation review. `transferSize` from cross-origin Performance API can be zero without proving zero transfer; WordPress media original filesize cannot substitute.

**Collection order:** Site QA checks missing images 285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1. Only after P0 verification, measure controlled baseline/candidate pairs for post 621, then 34–38, 299, 269. Use the same collector; do not add a new browser tool here.

## Rights/visual workflow — no authorization to publish
For a confirmed missing image, bind the actual displayed request to the exact published slot and independently verify archival item identity, title, creator, event year, reproduction/commercial use rights and attribution. Official Navy/Coast Guard/USGS/Florida Memory hosting alone is not universal permission. For Three Mile Island 285:5 the Commons original is **819×614**, not 960px; it must not be enlarged, silently forced into the published 16:9 crop, or called pixel-identical to SayMedia without proof. For 285:2 the NRC-attributed original has not been proven identical to the retouched archive alternative. Skyway 287:5 alternatives reflect different scenes and decades.

A candidate **may be evaluated for a separate rights-approved staging design** with the original asset preserved, no automatic image scraping, a full-frame at-most-960px derivative when appropriate, ALT/caption credit, responsive `srcset` and `sizes` verification, and before/after screenshot checks at desktop and mobile. Never overwrite media originals or rewrite Gutenberg blocks automatically. Staging itself is **not authorized by this draft**. Capture source URL, license proof, dimensions, checksum, editorial signoff, cache behavior and an explicit rollback mapping before any separately authorized WordPress changes.

## Evidence and release
New machine-readable worksheet: `qa/media-recovery/transfer_pair_workbatch_20261111.json`. It preserves all six suspected missing original URLs/catalogs and all 15 >1.5MB media originals, with actual HTTP and wire-byte fields explicitly `null`, not inferred or simulated. **20/20 isolated V8 tests** passed against GitHub-fetched committed module/test source blobs. Native Node CI and real logged-out browser tests have not run; no performance savings or live repairs have been established.
