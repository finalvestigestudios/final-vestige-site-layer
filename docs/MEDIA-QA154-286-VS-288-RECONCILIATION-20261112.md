# Media Recovery / Site QA offsite-count reconciliation — 2026-11-12 PT

## New finding: historical counts 286 versus 288 are not interchangeable

The 61-post/355-inline-image cohort in Site QA draft [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) has 286 offsite source references in `qa/media/cms_image_census_20261030.csv` (exact source Git blob `76aa63ffaa299a6e6878edc1b66e637fa6f058ab`). The frozen 61-post/355-image source ledger in Media Recovery [#1703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1703), blob `a9706c72ad6f17a68113aa87fc063f70d0ca0c34`, has 288. **Reapplying Site QA's actual `source_image_dependencies.cjs` origin-classification logic** (Git blob `cdadab899abed4dfd222e75a5616a98390dca4ea`) to the frozen 355 URLs also yields **288**: 170 external, 118 Wikimedia redirect, 7 first-party Jetpack proxies, 60 first-party; 170 + 118 = 288. Thus the discrepancy is **not explained by Jetpack/other origin-classification policy differences**.

All 61 post image counts and the overall 355 images agree. There are exactly **two post-level offsite-count differences**:
- **285 (Three Mile Island):** QA #154 reports 5/6, recovery frozen ledger classifies 6/6 offsite. This includes the original P0 images `285:2` and `285:5`; no current browser status was established for either.
- **291 (Teton Dam):** QA #154 reports 5/6, recovery frozen ledger classifies 6/6 offsite.

The older QA artifact is an aggregate CSV, **not the original per-slot source snapshot**, so it is impossible to identify which individual source was counted differently or why. The precise cause could be input-snapshot divergence or a counting error; both are unverified. **Do not attribute either discrepancy to a particular image or classify it as broken.** An `i0.wp.com` URL proxying another publisher is still `external` under the Site QA classifier, while `i0.wp.com/finalvestige.com/...` is `jetpack_proxy`.

## Concrete, non-duplicative output

- [Machine-readable 12-slot comparison](../qa/media-recovery/qa154_vs_media1703_offsite_286_288_20261112.json), preserving every original source URL for the two posts, its source class, **NULL origin/visitor HTTP**, rights HOLD, and conditional ≤960px/no-upscale plan.
- [Pinned, unmodified 61-row QA count snapshot](../qa/media-recovery/qa154_61post_offsite_snapshot_20261112.csv), sourced from draft #154 and checked by Git blob.
- [Fail-closed offline reconciler](../qa/media-recovery/reconcile_qa154_census_20261112.cjs): verifies source Git blobs, 61 post identities, 355 unique image slots, URL/classification parity, exact 286-vs-288 scope, and the two disagreements. Emits only source-scope reconciliation; **does not use the network or declare an HTTP failure**.
- [16-case native Node regression suite](../qa/media-recovery/test_reconcile_qa154_census_20261112.cjs): synthetic positive/adversarial fixtures, Jetpack semantics, duplicate posts/slots, original source drift, Git pin failure and unknown guest status. Genuine 355-slot comparison was separately executed against exact GitHub file contents during evidence generation; full native Node replay with the large source ledger and repository CI remain outstanding.

## Restoration and performance boundaries

Site QA #154 retains its existing logged-out Chrome/CDP collector and P0 sequence `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Request only the original raw source-slot snapshot for posts 285 and 291, and preserve true guest `currentSrc`, CDP response/redirect/requestId, decode/natural pixels, uncached `encodedDataLength`, screenshot and crop geometry in the existing workflow. **No duplicate collector or browser PR**.

For any proved failure, review exact-scene match and item rights (Navy/Coast Guard, Florida Memory, USGS, NARA or publisher as applicable), then consider reversible first-party WordPress media only when explicitly authorized, with max 960px width, no upscale and larger map/figure zoom access where required. No archival photograph should be silently substituted; alternative scenes require editorial disclosure and approval. The 15 >1.5 decimal MB WordPress originals still total **47,096,779 stored bytes**, not transferred bytes; proposed **76% real transferred-byte reduction remains unmeasured**.

The prior 42 reportedly broken originals remain **not guest-browser-confirmed**. No external image binaries were downloaded, licensed by assumption, cached, or mirrored; no risky Gutenberg rewrite, WordPress production write, homepage design change, merge, deployment or subscription expense took place.
