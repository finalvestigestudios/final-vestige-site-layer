# Media Recovery — Forrestal (post 289) same-VIRIN Navy photo recovery and 6-source triage (2026-11-02)

**Scope:** source-level, read-only provenance and media resilience. Separate from homepage visual design and Site QA #154's logged-out Chrome/CDP work. This memo does **not** authorize publishing, republishing, scraping, downloading, Gutenberg rewrites, changing ALT/captions in production, subscriptions or WordPress media uploads.

## Evidence directly observed on November 2

Frozen article source: `qa/media-recovery/parts/03.json` Git blob `49183f66f880f7c4dfd363acca906876877f2e5e`. The source has six exact `<img src>` links/ALT values at keys 289:0–5; none is first-party WordPress. All six URLs, ALT values, browser-status nulls, network-wrapper observations and candidate catalog IDs are in [the machine-readable audit](../qa/media-recovery/forrestal_289_virin_recovery_20261102.json).

Five **exact published** image URLs (289:0 Wikimedia, 289:1 Forbes CDN, 289:2 Sina CDN, 289:3 appmobile CDN, 289:5 CloudFront/DVIDS 2013 photograph) **rendered in independent web image viewer** on November 2. This is positive **image-retriever** evidence only; it is not a verified guest-browser HTTP 200, reliable site-wide load rate, LCP measurement, license decision or image-caching approval.

The remaining 289:4 publisher source, `https://media.defense.gov/2021/Dec/04/2002903623/1460/1280/0/210811-N-SG189-1105.JPG`, returned **403 Forbidden to independent web.open retriever**; no Chrome request/response or decoded image was measured. **Do not count as a confirmed visitor-broken image.** The original post ALT describes contemporary Navy firefighting simulation rather than the historical Forrestal fire; retain that crucial temporal distinction.

## Exact official same-VIRIN recovery lead (289:4)

DVIDS's [official primary photo catalog, image 6947585](https://www.dvidshub.net/image/6947585/farrier-firefighting-school) identifies **VIRIN 210811-N-SG189-1105**, which exactly matches the filename in the published `media.defense.gov` URL. Official catalog title *Farrier Firefighting School*, photographer **Mass Communication Specialist 2nd Class J. Keith Wilson**, photo date **August 11, 2021**, event **two hose teams extinguishing a simulated Class B fire in Norfolk**. The [official catalog thumbnail](https://d1ldvf68ux039x.cloudfront.net/thumbs/photos/2111/6947585/1000w_q95.jpg) rendered independently. DVIDS reports master **5448 × 3625**, catalog size **7.08 MB**, publicly marked **Public Domain**. These are catalog/master figures, **not bytes actually downloaded by finalvestige.com visitors**.

This exact VIRIN is meaningful, strong **asset-lineage evidence**, but the posted cropped/resized `1460/1280/0` derivative has not been retrieved or compared by binary SHA-256 or side-by-side with the DVIDS rendition. The conditional non-upscaled derivative would be **960 × 639**, without crop (calculated from the catalog master 5448 × 3625; confirm actual downloaded binary dimensions before execution). **No WordPress image has been created.**

Read [DVIDS's current Public Use Notice of Limitations](https://www.dvidshub.net/about/copyright): generally official-duty government photographs are not US-copyrightable, but **some third-party content is protected**, and non-endorsement, military-marking, publicity/privacy and credit rules apply. DVIDS's entry marks this particular image Public Domain and credits its Navy photographer, but an **item-level rights/usage review must precede any rehosting**. Do not treat a catalog badge as proof that third-party processed derivatives or another publisher's crops are freely reusable.

## Two NHHC historical alternate-scene leads — no auto-swap

- [NHHC USN 1124785](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/USN-1124000/USN-1124785.html), dated **July 29, 1967**, portrays crews and USS *Rupertus* directing firefighting hoses at *Forrestal*. Catalog high TIFF geometry **5634 × 4484**, conditional no-upscale **960 × 764**. It does **not** prove visual/binary equivalence to published **289:1**, a color after-fire hose scene.
- [NHHC USN 1124802](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/USN-1124000/USN-1124802.html), dated **July 29, 1967**, portrays fires/explosions on the after flight deck. Catalog high TIFF geometry **6184 × 4956**, conditional **960 × 769**. It is **not** the same documented camera view as published **289:3**.

NHHC search-index excerpts supplied authoritative record numbers/captions and high-res dimensions; **full NHHC page fetches timed out/returned gateway errors in this session**, so recheck individual records and rights before any staging. The NHHC medium-rendition label (1280x1280) must never be treated as decoded width/height. The published **289:2** is a separate overhead damage scene, **289:5** depicts a **2013** Farrier memorial/instructor, and 289:4 depicts **2021** training. No historical/modern image should be relabeled as a July 1967 incident photograph.

## Release-gated staging and caching plan

1. **Site QA #154** uses its *existing* logged-out guest Chrome instrument, not a duplicate script, to capture post 289 desktop + mobile for 289:4 first; record `img.currentSrc`, `naturalWidth/Height`, CDP requestId, final response URL/status/content-type, encoded transferred bytes, CDN redirects, and screenshot. The independent retriever's 403 is not a CDP 403.
2. If visitor image is genuinely missing, compare official DVIDS 6947585's visual scene against the existing original rendered photo where possible. Item-level credit, public-use restrictions and any needed permission must be reviewed and noted.
3. **Separate staging authorization required** to retrieve source from allowed original catalog, compute SHA-256, inspect exact intrinsic pixels/orientation/EXIF, and create a no-upscale **≤960 px** optimized derivative using a safe image library. Preserve 2021 chronology, Navy photographer credit, correct ALT/caption, and source/rights URL. No unlicensed scraping, blindly hotlinking, or commercial endorsement implication.
4. Only after staging approval: register a **new** WordPress media attachment, let WordPress generate `srcset` and stable local CDN delivery, stage **a limited and rollbackable single-image substitution** with attachment ID and original `src` retained; do not broadly rewrite Gutenberg blocks. Review responsive `currentSrc`, CLS/LCP and visual before/after at desktop/mobile.
5. Measure **actual image-request transferred bytes** (cold-cache and defined warm-cache experiments, identical device/viewport/content) before and after for the **same verified displayed image**, excluding failed/speculative, unrelated and duplicate requests; do not quote 76% savings without reproducing baseline method. Rollback on visual regression or inability to establish rights.

## Tests / scope barriers

`qa/media-recovery/validate_forrestal_289_20261102.cjs` is a fail-closed, offline audit validator. `qa/media-recovery/test_forrestal_289_20261102.cjs` covers the valid 6-slot report and **19 invalid mutations**: fabricated statuses, alt/source substitutions, source key identity, image-year misclassification, DVIDS VIRIN, rights, dimensions/aspect ratio, NHHC wrong-scene swap, 42/76 claims, WordPress publishing, and repair-count inflation. **20/20 checks passed in the isolated JavaScript V8 runtime before commit; native Node CI and public Chrome remain pending.** No source media binaries downloaded.

**Standing production status:** 61 articles / 355 image slots / 288 offsite origins / 13 originals above 1.5 MiB. **42 claimed broken not verified by visitor browser; 76% claimed reduction not measured; 0 images repaired in production.** 
