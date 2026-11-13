# November 12, 2026 PT — Historical 61-post image layout-reservation source audit (draft only)

## Purpose and ownership

Media Recovery owns source/image resilience, evidence and safe recovery proposals, **not** the homepage visual design (interim lead) or Site QA #154's guest Chromium/CDP collector. This batch is a **source-only geometry exposure** supplement to [Site QA PR #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) and the existing [image-weight worklist in draft PR #183](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/qa/media-recovery-reviewed-20261030-1158/docs/IMAGE-WEIGHT-WORKLIST.md). It does not introduce another browser collector or overwrite Site QA's drafts.

Source custody: frozen historical [61-post/355-image WordPress edit-source ledger](../qa/media-recovery/live_61post_355image_integrity_consolidated_20261112.json), exact Git blob `a9706c72ad6f17a68113aa87fc063f70d0ca0c34`. The current broader **66-post/361-image** cohort must be evaluated separately.

## Newly derived site-wide visual-integrity exposure

- **305/355 (85.9%)** stored `<img>` positions have **neither literal HTML `width` nor `height` attributes**; 50 have both, zero have a partial pair and zero have literal source `srcset`. This is a potential browser space-reservation *exposure*, **NOT measured CLS**.
- **266/288 (92.4%)** historically offsite image positions have neither literal width nor height. The other 39 source positions without dimensions are first party.
- **All six P0 original external-media positions**—`285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`—lack both HTML dimension attributes. Source URLs and ALT text remain separately pinned in the machine audit. It would be incorrect to call these six visually shifted or broken without a live browser capture.
- Highest static exposure count by post: **268 Archimedes 10/10**, **367 Palomares 8/9**, **425 Courrières 8/9**, **370 West Loch 8/8**. Prioritize actual visitor failures first, then confirm visible layout shifts; post counts alone are not severity.

[Machine-readable 61-post + six-P0 audit](../qa/media-recovery/html_geometry_61post_p0_20261112.json) reports 61 per-post records, six exact published URLs, ALT, null guest statuses, conditional layout reservation and no-release policy. [Deterministic read-only generator](../qa/media-recovery/audit_html_image_geometry_20261112.cjs) requires the exact raw source Git bytes; [13 native Node adversarial/control regressions](../qa/media-recovery/test_audit_html_image_geometry_20261112.cjs) passed on exact committed code. Source coverage was independently recomputed from the GitHub ledger in this sprint. Genuine logged-out browser checks and repository CI have not run.

## Do not conflate absent HTML dimensions with actual layout shifts

The theme, CSS `aspect-ratio`, wrapper `min-height`, lazy-loader, image decoding, CSS layout and rendered image dimensions may still reserve the correct space. A static audit cannot prove a 0.1 CLS, any LCP effect, broken imagery or a 76% image transfer reduction. Some images are intentionally resized or cropped by existing CSS.

For each P0 image **in Site QA's existing collector**, request the source/currentSrc + request-ID-bound redirected HTTP/MIME, `naturalWidth`/`naturalHeight` + `decode()`, CSS `aspect-ratio`/rendered image and container bounds **before and after load**, actual layout-shift entries (`hadRecentInput` filtered), desktop/mobile viewport and DPR, screenshots, completed uncached image transfer bytes. If unavailable, keep `CLS=null`, `guest_status=null`. Do not infer image failure from web-retriever wrappers or static missing dimensions.

## Visual and rights safeguards for fixes

A conditional WordPress media proposal should retain the same photographed object, framing, caption and ALT; verify rights for **each** item (including derivatives) using Navy, Coast Guard, Florida Memory, NRC/USGS or archival catalogs; preserve creator/collection credit; verify actual native dimensions and target viewport **before** selecting a variant **at most 960 px wide and never upscaled**. For example, a 600 CSS-pixel image at DPR 2 needs 1,200 physical pixels, incompatible with a strict 960px variant without a higher-resolution exception/editorial layout decision—**HOLD**, do not silently degrade sharpness. No blanket copying of offsite photos.

The existing six P0 source/candidate mapping is in [canonical migration audit](../qa/media-recovery/p0_canonical_origin_migrations_20261112.json), and the 15 WordPress originals larger than **1,500,000 decimal bytes** (47,096,779 **stored** bytes, 11 inline matched) are documented in [P0/oversize handoff](../qa/media-recovery/p0_and_oversize_attested_release_handoff_20261112.json). Neither stored bytes nor old web-retriever statuses measure cold visitor transfer. The claimed **76%** remains unverified for both the historic 61 and the current 66 posts.

## Safe sequence / rollback

1. Site QA #154 checks true P0 broken states and separate measured layout instability from the same logged-out captures; no duplicate collector.
2. Media Recovery provides item-specific source/license/scene/crop/dimension evidence, SHA of authorized asset if one is later obtained, proposed credit, no-upscale variant and screenshot comparisons. Archive alternatives differing from the original must be explicitly labeled editorial substitutions.
3. An independent staging review can propose a new WordPress media ID and exact-slot update/rollback plan. **No production post-block rewrite, upload, cache or deployment now.**

All values in the new JSON are source-only; all P0 guest statuses, actual layout shifts and transferred bytes are `null`. No paid calls, third-party image binaries, WordPress writes, homepage edits, merges or deployments were involved.
