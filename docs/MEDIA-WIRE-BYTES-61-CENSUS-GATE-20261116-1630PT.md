# Media Recovery — CDP wire-byte claim gate (61-post historical scope)

**2026-11-16 16:30 Pacific · draft/offline only · no WordPress changes.** Owned by Media Recovery draft PR #2747; Site QA #154 owns the existing guest-Chromium collector. This sprint does NOT add a browser collector or touch the interim lead's homepage design.

## New finding / why the 76% claim is still on HOLD

A fresh source-derived accounting crosswalk pins the historical Site QA article census at **61 posts / 355 stored inline IMG references / 286 directly offsite references** (Site QA CSV Git blob 76aa63ffaa299a6e6878edc1b66e637fa6f058ab). It separately pins **20 WordPress original assets strictly greater than 1,500,000 bytes**, totaling **64,385,752 bytes stored**, from the authenticated 132-item Nov 16 WordPress media inventory (source JSON Git blob c07d27296d89f980499a0c0b9d83dd1fdcb7531d).

Five historical-reconstruction PNG originals (media 39–43) account for **13,267,538 stored bytes (20.61% of the 20-original storage total)**, but the published posts 34–38 embed *Jetpack resize=1024,576* URLs instead of those original URLs. All five have inline width/height, no srcset/sizes, and reconstruction captions. Actual visitor currentSrc, decoded pixels, HTTP status, image transfer size and CLS are **unobserved**. WordPress storage bytes are **not** a network-before baseline; computing 76% from original bytes would be misleading.

Machine audit: qa/media-recovery/image_weight_no_capture_20261116_1630pt.json contains **20 exact WordPress original URLs**, sizes, declared native geometry and conditional no-upscale 960px review dimensions, plus five exact published Jetpack URLs. All guest statuses and network bytes remain **null**. Its provenance is a read-only transformation of the pinned WordPress JSON, *not fresh origin HTTP probing or a logged-out browser measurement*.

## Offline assessor, no duplicate collector

Inputs: frozen Site QA census CSV (qa/media-recovery/siteqa_61post_census_reference_20261030.csv), existing WordPress source JSON, and *optionally* a local sanitized paired-network export from Site QA.

Run at repository root:

~~~sh
node --check qa/media-recovery/assess_image_wire_reduction.cjs
node --test qa/media-recovery/test_assess_image_wire_reduction.cjs
node qa/media-recovery/assess_image_wire_reduction.cjs \
  qa/media-recovery/siteqa_61post_census_reference_20261030.csv \
  qa/media-recovery/oversize_20_five_png_runtime_20261116_1130pt.json
# Optional: supply PRIVATE logged-out Site QA before/after capture JSON as a third argument.
~~~

The offline script validates all 20 stored originals, all five observed Jetpack PAGE srcs, source IDs/URLs, historical census counts, and reports **NO_BROWSER_CAPTURE** when none was supplied. It does not make image status claims from public-retriever 400/403/404/500 results. Its test fixture contains deliberately **synthetic** requests, not visitor evidence.

A paired export must use schema fv-paired-image-wire-v1, a logged-out **Chromium** environment, both sessions with cache disabled and service workers bypassed, matched mobile viewport/DPR/network profile, same published post IDs/URLs, complete lazy-image loading and scroll, visually preserved image slots, and image requests uniquely identified with 2xx statuses, image MIME, successful decode, no cache/prefetch/service-worker/redirect ambiguity and nonnegative safe CDP Network.loadingFinished.encodedDataLength bytes.

The assessor sums all qualifying image request-received bytes across matched pages:

**percent reduced = 100 × (1 − Σ after CDP received bytes / Σ before CDP received bytes)**.

This is *request-received* network data, not media-library storage or necessarily exact image payload bytes. Missing, cache-contaminated, unsuccessful, unpaired or unverifiable image rows cause **HOLD**, rather than a fabricated savings percentage. Partial coverage is explicitly **MEASURED_SUBSET_NOT_SITEWIDE**. Even a complete 61-page self-described export is **COMPLETE_61_PAGE_SELF_REPORTED_REVIEW_REQUIRED**, not independently verified. The evaluator never certifies 76% and does not claim that the reported 42 broken images are visitor-confirmed. Note that this **historical 61-page** cohort is not interchangeable with the later 66-post live scope.

## Approval and visual-integrity gates (no changes made)

- **P0 missing-image triage first:** Site QA #154 should feed actual guest currentSrc, status, MIME, successful decode, natural width/height, screenshots and measured bytes for 285:5, 285:2, 287:5, 418:1, 418:2 and 407:1 into the existing P0 evidence evaluator. Do not duplicate its collector.
- **Primary-source recovery:** Keep the existing Navy, Coast Guard, USGS, Florida Memory, NRC/NASA/archives mappings and item-level credit/licensing decisions in draft #2747. Images that merely look similar are NOT exact-frame/crop replacements. For Coast Guard museum Scotch Cap 600×463 and TMI 604×590 derivatives, *never upscale*. Material from private publishers is a rights HOLD, not automatically cacheable.
- **WordPress media plan:** only after verified same-frame identity and rights, stage a reversible WordPress media-library attachment with sensible WebP/AVIF/JPEG sizes capped at a native-width-aware 960px (no upscaling), explicit dimensions, srcset/sizes, preserved ALT/captions/credits, and per-post URL rollback. Visual/mobile screenshot diffs and measured cold network deltas are release gates. No live post-block rewrites, download/rehosting or production writes in this sprint.
- **Other oversized originals:** 15 of 20 currently lack the five PNGs' pinned published-tag crosswalk; prioritize guest currentSrc/transfer testing by live page rather than treating an 8.17 MB original as an 8.17 MB download. Keep media provenance and displayed captions intact.

## Evidence and safety

37/37 **native Node 22.16.0 synthetic-fixture assertions passed** locally (including 30 fail-closed cases); source/test blob hashes were checked against the exact local files. The 20-source JSON was checked against the original WordPress ledger in the GitHub connector. Native Node with the actual connected inventory and GitHub Actions CI still require independent execution. No network fetch, unlicensed scraping, production image replacement, CSS/homepage work, WordPress writes, merges, deployments or subscription spend.
