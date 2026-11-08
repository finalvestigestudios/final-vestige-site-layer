# Media Recovery — paired published-image source integrity (2026-11-08)

## Finding and reproducible mechanism

The offline comparator `qa/media-recovery/compare_cold_image_wire_v1.cjs` previously allowed a **different historical asset** in the candidate CDP capture, provided the post URL, stored image-slot identifier, caption ALT, decoded image geometry, network status and byte totals were internally consistent. In the synthetic reproduction the image at slot `34:0` switched from `https://finalvestige.com/wp-content/uploads/2026/08/test.png` to `https://finalvestige.com/wp-content/uploads/2026/08/unrelated-photo.png`. Both individually presented valid uncached HTTP-200 `image/png` CDP requests. Same ALT and 960×720 natural pixels. Baseline transfer: 1000 bytes; candidate transfer: 240 bytes. **Prepatch** result: `LAB_PAIR_MEASURED`, `reduction_percent:76`; an invalid historical-photo comparison even though `sitewide_76_percent_claim_permitted` was correctly false.

**These URLs and bytes are synthetic regression fixtures, not actual published post assets or real browser transfer measurements.** No original binary assets have been retrieved or modified.

## Fix (draft only)

In the paired image-key loop, require exact equality of `baseline.stored_url` and `candidate.stored_url`; otherwise emit `published_original_changed_between_runs:<key>` and return `HOLD` with no reduction percentage. This is intentionally stricter than CDN/Jetpack `currentSrc` transformations: the stored WordPress original source is the frozen source of truth. The existing numeric Jetpack transform test continues to pass when `stored_url` does not change. This only catches changed **URL strings**; it cannot establish that a publisher did not replace image bytes in-place at an unchanged URL. Asset hash/provenance and before/after visual parity still require independent checks.

An approved transfer to a new WordPress Media Library URL requires separate recorded scene-identity mapping, per-item licensing and attribution review, native geometry/no-upscale bound (maximum 960 px), editorial caption integrity, side-by-side visual inspection and explicit production authorization. The comparator must not automatically waive the source identity gate.

## Regression evidence

- Previous committed comparator blob: `8bed6f3e25b577532ad4193fe79fa54e021a1881`.
- Four additional adversarial cases: different candidate historical photo, different baseline, foreign external publisher, and same-site alias.
- Before code change: **45/49 PASS, 4/49 FAIL**, with all four new cases incorrectly yielding `LAB_PAIR_MEASURED`.
- After code change: **49/49 PASS** in isolated V8 with a test-only URL/source-equivalence adapter; Node CI and actual browser capture not executed in this environment.
- Source module: `qa/media-recovery/compare_cold_image_wire_v1.cjs`; tests: `qa/media-recovery/test_compare_cold_image_wire_v1.cjs`.

## Coordination, recovery and performance limitations

Site QA #154 already owns guest Chromium/CDP scanning and P0 checks for exactly `285:5`, `285:2`, `287:5`, `418:1`, `418:2`, `407:1`. No collector duplication or changes. No six-slot guest-browser evidence was available to this sprint. Existing third-party retriever-wrapper statuses (404/500/403/400) are **not** source-origin/visitor 404s; a mapped same-publisher candidate is not redistribution permission. Continue verifying actual browser `currentSrc`, HTTP/failed request, `naturalWidth`/`naturalHeight`, transferred bytes, licensing and visual composition before any action.

The original 61-post/355-slot snapshot and mixed-date 66/361 expanded inventory are source-cohort records, not fresh complete guest-browser measurements. Reported 42 broken originals **unverified**; 76% site-wide wire-byte reduction **unmeasured**; 15 original media objects >1.5 decimal MB sum to 47,096,779 **stored bytes, not browser transfers**. This change cannot validate field savings.

**Authorization flags:** `third_party_download=false`, `cache_or_rehost=false`, `wordpress_media_or_post_edit=false`, `homepage_design_edit=false`, `production_deploy=false`, `subscription_spend=0`.
