# USS Pueblo (post 280): Navy primary-source image custody and recovery, 2026-11-04

**Scope:** Independent Media Recovery PR #183 only. No WordPress production writes, image binaries, cache/localization, homepage work or subscription spend. Site QA #154 owns actual guest-browser/CDP checks.

## Evidence and limits

The October 30 frozen WordPress source snapshot `qa/media-recovery/parts/03.json` (Git blob `49183f66f880f7c4dfd363acca906876877f2e5e`) records **six distinct image URLs** for [post 280](https://finalvestige.com/2026/08/19/the-sledgehammers-broke-first-uss-pueblo/) and six ALT strings. All 6/6 point at `www.history.navy.mil`; there is no fallback image from another origin.

On November 4, 2026, independent `web.open` probes of the **exact published JPEG URLs** resulted in five text-tool **wrapper 502** errors, and one tool inaccessible message for the Banner image. This **does not establish** origin HTTP 502, a broken browser image, or a broken Jetpack version. Image search visibly displayed published NH 75561 (280:2) and K-64728 (280:5). Independent container HTTPS requests failed **DNS resolution before HTTP**. Visitor `currentSrc`, final Image GET status, response MIME, decode success, natural dimensions, transfer bytes and screenshots are **unknown**. Neither the reported 42 broken images nor the asserted 76% image-weight reduction is proven.

[Machine-readable complete six URL/ALT/transport/rights ledger](../qa/media-recovery/pueblo_280_nhhc_primary_20261104.json) and [fail-closed validator](../qa/media-recovery/validate_pueblo_280_20261104.cjs) preserve this distinction.

## Exact preservation and primary archive mappings

| Published slot | Official catalog reference | Verified archive subject | Derivative maximum (conditional) | Concern |
| --- | --- | --- | --- | --- |
| 280:0 | [428-GX-USN-1129207](https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/ships-us/ships-usn-p/uss-pueblo-ager-2/428-gx-usn-1129207.html) | USS Pueblo off San Diego, Oct. 19, 1967 (PHCS J.M. Lahr) | **960 × 660** from catalog TIFF 3263 × 2244 | catalog high-res dimensions **not** published JPG pixel decode |
| 280:1 | [NH 75559](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75559.html) | Crewman drawing coffee, 1967; [Pueblo DANFS](https://www.history.navy.mil/research/histories/ship-histories/danfs/p/pueblo-iii.html) caption attributes this image to NH 75559 | width **≤960**, height **unknown** | archive medium label 1280×1280 is a rendition envelope, **not intrinsic size** |
| 280:2 | [NH 75561](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75561.html) | USS Pueblo crew mess and living spaces, 1967 | width **≤960**, height **unknown** | published image visibly present in independent image search, not a visitor browser check |
| 280:3 | [K-64683](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64683.html) | Crewman at **check-in after crossing the Bridge of No Return**, Dec. 23, 1968 | **960 × 773** from catalog TIFF 6184 × 4978 | editorial improvement: published ALT is more generic than Navy catalog; no edit |
| 280:4 | [Banner II DANFS](https://www.history.navy.mil/research/histories/ship-histories/danfs/b/banner-ii.html) and **different photograph** [NH 68705](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-68000/NH-68705.html) | Sister ship Banner. NH 68705 depicts Banner on **May 12, 1969**, but is NOT confirmed same photo as published DANFS image | **960 × 722** only for **different candidate** NH 68705 catalog TIFF 6312 × 4750; published asset dims **unknown** | **DO NOT SUBSTITUTE** without subject/crop/rights review; NH 68705 catalog lists copyright owner NHHC |
| 280:5 | [K-64728](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64728.html) | Pueblo crewmen eating at UN Advance Camp after repatriation on Dec. 23, 1968 | width **≤960**, height **unknown** | image search displayed published image, not proof of guest-browser success |

No source binary SHA-256, matching decoded pixels, crop equality, or actual browser HTTP response is verified. Six **catalog subject mappings** are not six binary matches.

## Rights and policy

[NHHC Photo Archives policy](https://www.history.navy.mil/our-collections/photography.html) says most photographs are public domain, but it does **not** certify rights for every image and explicitly assigns rights verification to the researcher. Its [scanning and copyright guidance](https://www.history.navy.mil/about-us/services-and-policies/scan-copyright.html) allows reproduction of official government photographs but prohibits changing their content (resizing/cropping is distinguished). Crediting the correct NHHC or National Archives catalog identity is expected. The Banner NH 68705 item labels a copyright owner and must not be automatically classified PD. The ledger keeps **all six** at item-rights-review-required; no license, download, cache, WordPress upload, or post rewrite approval is inferred.

## Conditional remediation and measurement (no production changes authorized)

1. Site QA's existing high-priority logged-out Chrome queue is unchanged. After its P0s, inspect a *single* Pueblo image (280:0) through DevTools Protocol; if actual image GET/decode fails, probe all five related NHHC origins as a **same-host fanout**, not because a text retriever returned 502.
2. Preserve `src`, resolved `currentSrc`, redirects, final GET HTTP and MIME, `naturalWidth`/`naturalHeight`, `decode()`, viewport screenshot, and `Network.loadingFinished.encodedDataLength`. Record Jetpack/CDN rewrite and any browser cache hits. Maintain controls: one positive original source and one suspected failure.
3. Restore **the same archival photograph** with per-item rights confirmed. No stock replacement, different camera angle, or Banner photo swap on superficial subject match. Verify intrinsic pixels and EXIF orientation, derive width `min(960, sourceWidth)` with proportional height and **no upscaling**; preserve labels and proper historical caption.
4. Only after separate approval, stage immutable WordPress media asset and a source/provenance/copyright manifest; compare logged-out desktop/mobile screenshots, accessibility ALT, resource waterfall and pooled image-transfer bytes. No direct Gutenberg rewrite without diff review and rollback. Do not treat original library storage size as visitor wire bytes.
5. The full 61-post/355-slot site-wide **76%** savings claim requires matching cohorts, verified source identity, cold repeat request bytes and the existing fail-closed CDP pipeline. All unmeasured values must remain `null`.

## Regression evidence

`node qa/media-recovery/test_pueblo_280_20261104.cjs` is the native Node entrypoint. The committed [test file](../qa/media-recovery/test_pueblo_280_20261104.cjs) includes frozen Git blob SHA verification, a valid-ledger baseline, **36 adversarial mutations**, wrong live SHA and drifted frozen source. **40/40** logical assertions passed in a V8 CommonJS compatibility runner against the exact GitHub-committed audit/validator/tests; the runner substituted the GitHub-reported blob SHA for Node's native SHA1 implementation. **Native Node execution, CI and guest-browser verification remain pending**.

**Boundary:** Media Recovery #183 owns provenance, rights, derivative sizing, and measurement release safeguards. Site QA #154 owns logged-out browser inspection; homepage Interim Engineering owns visual design. Do not modify their drafts or ship unapproved WordPress changes.
