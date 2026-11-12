# Image weight: 15-original responsive feasibility, not a 76% result (Nov 11, 2026)

**Draft-only media recovery evidence, PR #1703. No WordPress production writes, image downloads/caches, homepage visual work, merges or paid services.** Read `docs/IMAGE-WEIGHT-WORKLIST.md` in draft PR #183, blob `2acd06a4ca4317646006eb6591face3fe76fedec`, and Site QA draft #154 before preparing any future release.

## Concrete 15-item P1 batch

A new [machine-readable 15-item feasibility and exact source manifest](../qa/media-recovery/p1_15_responsive_960_feasibility_20261111.json) and [source-bound validator](../qa/media-recovery/validate_p1_15_responsive_960_feasibility_20261111.cjs) derive only from the frozen [cross-PR bridge](../qa/media-recovery/browser_handoff_6_p0_15_oversize_20261110.json), Git blob `d1a9c7a499510ec37bcdba5858d45165752587e0`.

**15** original WordPress attachments strictly exceed 1,500,000 B and total **47,096,779 stored original bytes**. **11** map to inline images across eight published posts and account for **38,480,915 stored original bytes**. The remaining **four** totaling **8,615,864 bytes** did not match *published inline* images, not proof they are unused as featured images, pages, thumbnails or products. **Five** inline 1672×941 PNGs (media IDs 39–43, posts 34–38), combined original storage **13,267,538 B**, have **zero registered WordPress subsizes**.

The five PNGs have source HTML width hints of **1024px** (not independently measured painted CSS widths). A **960 physical px** derivative is only sufficient for a painted width of **at most 480 CSS px at DPR=2** (or 320 at DPR=3) absent intentional lower-density presentation. Even the native 1672px originals would not supply a full 2048px physical width if these five images really painted at 1024 CSS px at DPR2. Do **not** indiscriminately replace the existing 1024-wide HTML-image sources with 960-only files; require actual selected `currentSrc`, painted CSS width, DPR and viewport screenshots, and favor tested responsive `srcset` variants within authorized native bounds.

The manifest records original exact URLs, attachment IDs, native dimensions, conditional full-frame and no-upscale 960px output dimensions, and each candidate's maximum safe *CSS* width for DPR 1/2/3. It does **not** create image files, measure browser bytes, or authorize reproduction. Existing 1024px Jetpack transforms on post 299 are not evidence that the browser transfers the large stored originals.

## Release sequence and QA separation

1. **P0 first:** #154's **existing** guest browser collector must adjudicate `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`, using real image resource status/MIME/body and rendered screenshots, before assigning a restoration. Reported **42 broken** is unverified.
2. **P1 later:** for each of the 11 inline-exposed originals, capture exact `currentSrc`, physical selected-image dimensions, painted CSS size, DPR, cold network bytes, responsive breakpoints, crop and text legibility. For all five no-subsize PNGs, review staging-only WordPress registered-size generation, creator rights and visible visual equivalence, not Gutenberg rewrites.
3. **Rights:** separately clear the copyright, photograph subject/caption, and any applicable attribution for each original and derivative; map/photo details must remain inspectable at larger accessible resolution. No external-image mirror or content rewrite from this manifest.
4. **Measure:** match identical article/slot identities before/after, sum distinct completed cold CDP `Image` request bytes (not two DOM references to the same request; no cache-hit or partial-206 proxy success). Publish a 76% claim **only** when real validated sitewide browser traffic supports it.

The historic source cohort is **61 posts/355 inline/288 offsite**, while the later, mixed-date census is **66 posts/361 inline**. Neither is itself a network request measurement. No guest-browser failure or transfer reduction was independently verified in this sprint; direct container HEAD checks failed DNS (not evidence of a public outage).

**Handoff:** post manifest, exact hashes and test result to Site QA #154; do not create a competing collector or modify their draft.
