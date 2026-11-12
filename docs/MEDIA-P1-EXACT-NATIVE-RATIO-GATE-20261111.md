# P1 exact-native-geometry safeguard — 2026-11-11

This is an isolated engineering change to draft #1703 (no WordPress, binary, homepage-design, release, merge, or spend writes). Reviewed `docs/IMAGE-WEIGHT-WORKLIST.md` from draft #183, blob `2acd06a4ca4317646006eb6591face3fe76fedec`, and Site QA #154. Do not create a duplicate browser collector.

## Actual reproduced code defect (synthetic input, not live website)

The prior source-bound transfer evaluator accepted two 960×720 4:3 Vasa (`299:1`) selected resources as a measured **76% subset saving** even though WordPress frozen native original is 4256×2832 (~3:2). An identical wrong crop in BOTH captures evaded before/after photo-parity tests. Old result `VERIFIED_PRIORITY_SUBSET_SOURCE_BOUND_VISUAL_PAIR`; corrected result `HOLD`.

The corrected stage now requires the actual browser-selected decoded physical pixels and DOM intrinsic ratio of **both captures** to match the frozen source's aspect within 2.5% and never exceed its native physical dimensions. This is an original-frame safeguard, not item-specific rights clearance, not an image-identity hash, and not a production approval. Existing 37 regression cases were adjusted to native full-frame geometry; 6 new adversarial tests added, including a complete eleven-position positive-control cohort. Test case for high-DPR under-resolved images now retains the true native aspect while triggering the physical-density gate.

## Verified stored metadata, limitations and next actions

The frozen audit is 61 posts / 355 inline images / 288 offsite origin slots; current expanded 66 posts remains a distinct denominator. The 15 WordPress originals strictly over 1.5 decimal MB still total 47,096,779 **stored original** bytes. Eleven exact inline-matched originals on eight articles total 38,480,915 stored original bytes; all 11 exact current source URLs, native dimensions, rights HOLD and conditional 960px limits are in the sibling JSON. Five original PNGs (#39–43) have no registered WordPress subsizes. Four oversized attachments were not found in published inline images but may appear elsewhere; do not delete.

The historically reported **42 broken images have no confirmed logged-out visitor-browser failure evidence**. The proposed **76% weight reduction is unmeasured in real cold wire bytes**; synthetic percentages in test fixtures are not measurements. At DPR2 a 960 physical px resource supports at most 480 CSS px without upscaling. Preserve original full resolution and maps' legible small labels; do not replace historical photos with different crops or scenes automatically. No license is inferred from Navy/Coast Guard/USGS/Florida Memory/archives hosting; item-level commercial reuse rights, attribution and identity review remain HOLD. Caching/WordPress upload require separately documented permission and staging visual rollback.

## Site QA ownership and evidence

Site QA #154 owns logged-out Chrome CDP full-scroll capture and the six first-priority suspected missing positions `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Its future capture must supply exact frozen source/ALT, requestId/currentSrc, final actual origin response MIME/body/status, cache flags, loadingFinished encoded transfer, decoded selected-resource physical pixels, painted CSS/DPR, frame/crop, and before/after screenshots. This module only consumes completed evidence; it does not collect or publish.
