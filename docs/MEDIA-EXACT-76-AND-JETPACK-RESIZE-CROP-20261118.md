# Media Recovery 16:26 PST — Exact 76% gate and forced-crop integrity

**Scope:** Read-only QA and archival candidate triage; no production CMS, homepage, media downloads, billing, merge, deployment, or article-block edits. Companion to [Site QA #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154), not a replacement browser collector.

## Two reproducible acceptance defects corrected

1. **False-positive 76% saving at a rounded boundary.** In the historic 61-post / 355-inline-image fixture, before=35,500 and after=8,521 measured bytes gives **75.997183%**, which the old display-rounded evaluator reported as **76.00%** and incorrectly accepted. The revised gate checks **100 × after ≤ 24 × before** exactly using `BigInt` on validated safe integer totals, requiring both desktop and mobile independently to meet the threshold. The percentage rounded to two decimal places is **display only**. Sums beyond JavaScript safe-integer range HOLD.

2. **Jetpack `resize` crops, unlike `fit`.** [WordPress Site Accelerator API](https://developer.wordpress.com/docs/developer-tools/site-accelerator-api/) documents `resize=W,H` as a resize **and crop**, with the crop depending on the target aspect ratio; `fit=W,H` maintains the source aspect ratio. Prior identity checks protected explicit `crop` and `zoom`, but let a `resize=640,360` image silently become `resize=960,960`. New offline guard requires a proportional crop box for both in-capture authored/current/final URLs and before/after identity comparisons; adding/removing `resize` triggers review. Width-only and `fit` changes remain eligible. A conservative HOLD for unequal aspect ratios is intentional; only reviewed visual evidence can clear an exception.

## Native and integrated checks

- Native Node 22.16.0: **13/13 exact-byte helper** plus **11/11 resize-crop helper** tests pass. The four committed helper/test Git blobs were compared with local `git hash-object` results: byte-for-byte identical.
- Isolated V8 with Node-test and URL shims: **54/54 existing and expanded full-cohort parity and framing test functions pass** using the committed GitHub readbacks (including added 61/66 boundary cases). This is NOT native whole-tree test execution. Full CI and logged-out desktop/mobile Chromium/CDP captures remain outstanding.
- No captures were fabricated. The [machine-readable audit](../qa/media-recovery/p0_origin_and_gate_integrity_20261118_1626.json) keeps visitor HTTP/decoded/wire fields `null` and records only independent public-retriever HTTP 404 observations for original sources: Three Mile Island 285:5, USS Tang 274:6, Sunshine Skyway 287:5. No Jetpack guest-failure conclusion.

## Replacement source and 960px plan

- Tang 274:6: Navy **80-G-227989**, Commons 1910×1288, approximate 960×647. Still requires exact frame/crop confirmation and item-level rights/credit clearance; published publisher origin 404 does not automatically authorize any reuse.
- Skyway 287:5: Florida Memory **RC09237** is a different photo from the documentary still; no silent substitution. Dimensions unknown; editorial and item-level reuse clearance required.
- Three Mile Island 285:5: film still; no exact primary-source replacement confirmed, copyright HOLD.
- Teton Dam 291:2: previously identified source-caption mismatch; NARA candidate **28894685** (2798×1966; 960×675), but editorial and rights hold.

For any approved exact asset: preserve catalog URL, rights statement, author/credit, alt/caption/chronology, original SHA-256, proportional derivative ≤960px without upscaling, WordPress media ID **only in staging**, intended cache/Jetpack response, reversible original URL, and before/after guest screenshots and cold-image transfer traces. Do not rewrite raw Gutenberg blocks automatically.

## Current state and cohort hygiene

The historical **61 posts / 355 images** and newer **66 posts / 361 images** are different baselines; use one pinned manifest per evaluation. The report of **42 visitor-broken images** has no guest-browser proof. The desired **76% image-wire reduction** has no complete CDP proof. The **20 WordPress originals over 1.5 MB (64,385,752 stored bytes)** are storage figures, not browser transfer bytes. Site QA #154 retains Chrome verification ownership; no duplicate collector is introduced.

**Release: HOLD.** This PR changes only offline test/evaluation code, audits, and documentation.
