# Five direct first-party PNG reconstructions: verified live WordPress performance/visual-integrity batch (2026-11-03)

**Boundaries:** Independent Media Recovery draft PR #183 only; Site QA draft #154 owns real guest-browser testing; homepage design remains with interim lead. No image binaries downloaded, no production CMS writes, no media republishing, no assumed rights or subscription spending.

## New actual source evidence

Read **current published WordPress posts 34–38** through authenticated **read-only** `posts_get(context=edit)` and the associated **media items 39–43** through `media_get(context=edit)`. All five posts remain published; each uses one direct first-party image as both its first inline figure and featured-media ID. Source URL, Gutenberg inline ALT, figure caption, HTML dimensions, media-library ALT, 1672×941 original dimensions, stored byte size and media `sizes: []` are captured per row in [machine-readable live batch](../qa/media-recovery/five_png_no_subsizes_live_wp_20261103.json).

| Post / media | Original storage bytes | Original PNG dimensions | HTML width×height | Registered WP subsizes |
| --- | ---: | --- | --- | --- |
| 34 / 39, 1906 San Francisco Fire | 2,892,087 | 1672×941 | 1024×576 | 0 |
| 35 / 40, Shackleton James Caird | 2,552,136 | 1672×941 | 1024×576 | 0 |
| 36 / 41, Vicksburg caves | 2,498,247 | 1672×941 | 1024×576 | 0 |
| 37 / 42, Petra water | 2,488,823 | 1672×941 | 1024×576 | 0 |
| 38 / 43, San Francisco cisterns | 2,836,245 | 1672×941 | 1024×576 | 0 |
| **5 images total** | **13,267,538** | | | |

All five media-library titles/ALT descriptions identify the pictures as **AI-assisted historical reconstructions**, and all five **published figure captions already disclose the reconstruction**. The inline image ALT strings do not explicitly say *AI-assisted* (Petra's says *Reconstruction*). This is an **accessibility/editorial refinement**, not a claim that the site conceals disclosure from sighted readers. Preserve the existing AI caption and propose corresponding unambiguous inline ALT only through the normal editorial review process.

The image block `sizeSlug=large` and HTML `width=1024 height=576` do **not** imply a smaller network payload. WordPress reports no registered subsizes, which creates a **plausible full-original delivery risk**; however, Jetpack/CDN, theme processing, `srcset` injection or runtime transformations may still reduce actual downloads. Actual guest `currentSrc`, HTTP status, decoded pixels, MIME and **CDP loadingFinished.encodedDataLength** are **not measured**. The original storage sum is NOT page weight and is NOT a verified savings opportunity or 76% achievement.

## Safe isolated remediation sequence

1. Site QA #154: cold-cache desktop/mobile captures for the five exact page URLs and their images, with scroll coverage, `currentSrc`, requestId, final response status, MIME, naturalWidth/decode, `Network.loadingFinished.encodedDataLength`, cache behavior and screenshots. Do not overwrite Site QA draft source. If runtime already serves a small derivative, avoid an unnecessary modification.
2. Confirm image ownership/generator terms and assess edit/resize rights. These are first-party **AI-assisted reconstructions**, not historic archive originals; don't source-swap with purported historical photographs or silently remove the visible reconstruction labels.
3. In an **isolated staging workflow only after approval**, generate no-upscale **960×540** derivatives from the actual first-party original binaries, compare visual/caption fidelity, keep backup/original, inspect encoded outputs/ICC/color changes. Test WebP/AVIF with a compatible fallback where necessary. Do not promise a byte-savings percentage until binary sizes and guest wire bytes are measured.
4. Preserve and, with editorial approval, refine inline ALT to announce the reconstruction; retain existing figure caption, full alt semantics, Gutenberg block IDs and attribution.
5. Approve publication only after item-level rights + editorial review and screenshot/ALT regressions. Publish via separately approved media/post changes, retain rollback of old URLs, and record matched cold-cache before/after encoded network bytes, total image requests, LCP/CLS and actual failures.

## 42 / 76 measurement definition

- **42 alleged broken:** Count only independently observed Chrome `img` failures with exact page URL, visible/scroll-loaded image key, final `currentSrc`, requestId, HTTP/redirect or loadingFailed evidence, and `naturalWidth===0` or rejected `img.decode()`. A wrapper 403/404 is not an origin/guest failure. Do not mistake an unrequested lazy image for a broken one.
- **76% claimed reduction:** Using the same post set and viewport/device, explicit disabled browser cache and service-worker controls, full scroll to trigger lazy images, compatible versions of images, and same measurement tool, compute `100 × (sum baseline image encoded bytes − sum after image encoded bytes) / sum baseline image encoded bytes`. Keep a separate cold-cache and warm-cache cohort, never add stored WP original bytes to browser transfer sizes, and do not mix bytes from HTTP response headers, decoded images, and transferred payload definitions.
- The site-wide prior census remains **61 posts, 355 stored refs, 288 offsite-origin refs, 13 WP originals >1.5 MiB** (43,522,829 original-storage bytes); **10 of 13** are linked inline including 3 first-party Jetpack proxies. The five audited PNGs are all inline, account for **13,267,538 original-storage bytes**, and have **0 registered WP subsizes**. Browser-confirmed 42 and claimed 76% remain **unverified**; **0 production repairs**.

**Native regression:** `node --test qa/media-recovery/test_five_png_no_subsizes_20261103.cjs` (positive source validation + 25 fail-closed mutations). See [validator](../qa/media-recovery/validate_five_png_no_subsizes_20261103.cjs). All audit actions read-only.
