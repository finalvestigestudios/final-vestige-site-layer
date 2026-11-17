# Cold-image wire comparison: unbound source-family transfer guard (2026-11-14)

## Outcome

An **offline false-positive** in the existing media-only paired CDP evaluator is corrected in draft PR #183, with eleven additional regression cases. The original evaluator already correctly rejected an unbound *byte-identical URL*; it did **not** reject a second image network request when the URL was a legitimate image rendition, e.g. a first-party original versus an `i0.wp.com` Jetpack `fit` rendition. A canonicalized Wikimedia Commons file redirect versus an upload/thumbnail rendition had the same gap.

Synthetic baseline: one bound 1,000-byte request + a second 1,200-byte request for **the same photo**, but at an alternate URL; synthetic candidate: one 240-byte bound request. Previously the comparator returned **LAB_PAIR_MEASURED: 76%**, silently omitting the second baseline transfer. It now returns **HOLD: baseline:unbound_same_photo_request:621** with null savings. These bytes are **fixtures**, not observed visitor traffic.

## Narrow code change

In `qa/media-recovery/compare_cold_image_wire_v1.cjs`, the unmatched CDP requests are compared against all frozen `stored_url`, `current_src`, and `request_url` slot identities using the existing conservative `sameSource` classifier, rather than strict byte-string equality. All request `url_aliases` are examined, as before. Unrelated theme/logo requests remain distinct and do not inflate article-only bytes. This does not change Site QA #154's collector or historical-source identity rules.

Regressions in `qa/media-recovery/test_compare_cold_wire_source_family_20261114.cjs` cover: ordinary baseline pair, direct original versus Jetpack, Jetpack different `fit` sizes, candidate-side extra, redirect aliases, reverse direction, exact duplicate, Commons Special:Redirect versus upload thumbnail, unrelated theme asset, unparseable alias, and another CSS/DPR rendition. Eleven checks passed in **isolated V8 using a declared URL/source-equivalence test shim** against the proposed comparator; full Node with the repository's actual image-identity helper and CI remain unverified.

## Status and operational relevance

Site QA #154 remains **sole owner** of the P0 logged-out cold Chrome collector: 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. Those six original sources, archival catalog leads, wrapper-only statuses and rights caveats are recorded in the accompanying JSON. No 404/403/500/400 from an independent web retriever is promoted to actual visitor HTTP. The historical 42 'broken' count remains unconfirmed.

The frozen 61-post / 355-image census and expanded WordPress 66-post cohort are different snapshots. Latest documented oversized count: **16 >1.5 decimal MB WordPress originals, 49,107,665 stored bytes**, NOT visitor downloads. In particular Malbone post 621's two originals total **10,352,064 stored bytes**, but WordPress also advertises virtual 1024px Jetpack renditions; no transfer measurement exists. The proposed **76% network reduction is still unmeasured**.

## Release gates

1. Obtain cold request-ID evidence, MIME, actual encoded bytes, `currentSrc`, `naturalWidth`/`naturalHeight`, complete full-scroll coverage and all four explicit cache negatives from Site QA. Reject unmatched same-source duplicates before any byte reduction claim.
2. Confirm same historical asset, original scene and crop, source rights/attribution, derivative permission, editorial review and sharpness; no generic photograph replacing an NRC diagram or alternate Skyway chronology.
3. Derivatives are **conditional**, at most 960px without enlargement. An image shown at 960 CSS px on 2x displays may need 1920 physical px: do not trade away legibility. Maps require close-up readability checks.
4. For an approved image only, create reversible *staging* WordPress Media upload and record exact media ID, caption, credit, hash, new responsive `srcset`, before/after CDP requests and rollback; **no production writes or copy approval in this sprint**.

**Branch caution:** PR #183 is a large existing audit draft; **do not merge it wholesale**. Review/cherry-pick only this narrowly scoped code/test/audit/doc change into an isolated review branch when integration is approved. Neither Site QA's four draft files nor interim homepage design is changed. No third-party binary downloads or media caching, CMS posts, deployment, merge, subscription spend or browser collector duplication.
