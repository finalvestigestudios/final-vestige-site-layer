# Media Recovery — Rendered-Footprint Integrity Gate (2026-11-11)

## Source basis
- Isolated draft #1703, built against prior gate blob `3928a6275597af61b18f1d329265e4598400ef2a` and previous audit blob `44a67243f1f8fc56952cfc29bb8fbcbc0b07746e`.
- Authoritative 66-post, 15 >1.5 **decimal** MB original inventory: PR #183, exposure blob `5e474e1cb293353b2226d84fceedca0a182894d8`; source worklist `docs/IMAGE-WEIGHT-WORKLIST.md`, blob `2acd06a4ca4317646006eb6591face3fe76fedec`.
- Site QA #154 alone owns the logged-out CDP/Chrome image collector. No duplicate collector or production writes.

## Reproduced synthetic defect
Prior 11-slot comparator accepted synthetic Malbone 621 before/after image captures at intrinsic widths **120px** with visually valid original aspect ratios, even though rendered CSS widths were **320px** and a hypothetical 76% reduction was claimed. The comparison thus accepted a strongly upscaled, visibly blurry rendition. This is *test-only evidence*, not an observed live-site failure.

## Correction
The pinned P1 comparator requires each captured position to report actual integer CSS painted dimensions, full-frame visibility, and `object_fit`; rejects painted dimensions larger than intrinsic browser density-corrected image pixels; rejects `object-fit:cover` or unknown clipping modes; requires original aspect-ratio fidelity within 2.5%; and rejects changed CSS geometry/object-fit between baseline and candidate. No asserted screenshot-quality boolean substitutes for measured geometry. Image downloads, rights decisions, 960px file creation and post rewrites remain prohibited.

**Collector contract for Site QA**: Only augment the existing collector with actual `getBoundingClientRect()` dimensions, computed `object-fit`, and evidence that the image was entirely in the captured visual frame or a correctly stitched/full-scroll visual pass. Never synthesize missing geometry. Intrinsic `naturalWidth/naturalHeight` are browser density-corrected CSS pixel values, not necessarily raw binary physical pixels; do not multiply by DPR for this conservative geometric guard. Keep actual `currentSrc`, request/response/CDP lineage, MIME, cache flags, encoded byte length and screenshot identifier.

## No result inflation
- Historical 61 posts / 355 source images / 288 offsite researched; 42 previously reported broken images **not visitor-verified**.
- Later 66 published posts / 361 raw inline; 15 originals strictly over 1,500,000 stored bytes total **47,096,779**; 11 inline originals from 8 posts total **38,480,915** stored bytes.
- Prior proposed 76% visitor network savings **not measured**. The synthetic counterexample is *not* a traffic optimization.
- Preview sizing remains **min(960px, native_width)**, height scaled to full-frame source ratio, no upscale, no silent crop, special full-resolution access for maps/technical diagrams.
- Original P0 order: **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**. Investigate *real* visitor failures ahead of P1 optimization.

## Verification / restrictions
49/49 offline V8 regressions passed before commit (39 existing + 10 new), including all eight article cohorts; exact postcommit file verification should be repeated. Native Node CI and logged-out Chromium unavailable/unrun. Zero WordPress writes, third-party binaries/caches, homepage edits, merge/deploy or subscription spend. All replacement candidates remain rights/identity HOLD.
