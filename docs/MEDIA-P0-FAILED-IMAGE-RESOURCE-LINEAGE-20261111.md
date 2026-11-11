# P0 failed-image CDP resource lifecycle — 11 Nov 2026

## Defect and reproducible impact
The isolated P0 adjudicator classified synthetic cold 404/zero-natural-pixel evidence as **CONFIRMED_GUEST_BROKEN** without requiring the response to be a CDP `Image` resource or a completed `Network.loadingFinished` event. An incomplete request or unrelated navigation to the exact URL could therefore falsely convict a published image, even with the other page/slot lineage fields filled. This was a **test-only error path**, not a confirmed live outage.

The repair requires `resource_type === 'Image'` and `loading_finished === true` for HTTP >=400 + 0×0 pixels. Unknown, aborted and nonimage requests produce `HOLD: FAILED_IMAGE_RESOURCE_LIFECYCLE_NOT_PROVEN`. Error responses can legitimately be `text/html`, so MIME is not restricted for a completed failing *Image* request. Existing success-image checks still require successful image MIME, transferred body bytes, and positive intrinsic pixels. Other lineage requirements (correct article and slot, exact source URL, request IDs, uncached status, screenshot hash) remain intact.

## Source and performance custody
- PR #183 `docs/IMAGE-WEIGHT-WORKLIST.md` blob `2acd06a4ca4317646006eb6591face3fe76fedec`; main and PR #1703 do not contain the file. 61 historical posts / 355 inline / 288 source positions researched; 42 allegedly broken remain guest-unverified.
- 66-post expanded survey: 15 WordPress original files >1,500,000 bytes, total 47,096,779 stored bytes, 11 inline-associated across 8 posts, 38,480,915 stored bytes. Stored originals are **not** visitor transfer. 76% wire saving is proposed, not measured.
- Source-only six-row qa/media-recovery/p0_failed_image_resource_lineage_20261111.json preserves exact published URLs, image candidate references, rights observations, conditional 960px dimensions and **null actual guest/origin HTTP statuses and transferred bytes**.
- Independent web retriever recheck of 287:5 reported wrapper 404 while the relocated St Pete Catalyst image rendered; 418:2 original USCG image yielded wrapper 403 while Lighthousefriends version rendered. **Those wrapper outputs are not origin HTTP statuses or real browser evidence.** No third-party image downloads were made.
- Site QA draft #154 has four committed files: a source dependency classifier, tests, aggregate CSV and README. It **does not contain a committed browser collector**. Site QA owns practical browser collection; do not duplicate its other drafts or misstate that #154 already supplies CDP evidence.

## Reproduction, quality bar and release hold
- P0 queue: 285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1. Real cold Chrome/CDP page+slot+request+response+image lifecycle+screenshots are the blocking input. No fabricated status or network measurement.
- Item-specific licensing, photographer credit and same-scene verification must precede any image replacement. USCG portrait 418:1 has an official public-domain release catalog but neither its exact pixel identity nor browser failure has been verified. Skyway 1989 Florida Memory photographs illustrate **after** the 1980 collision and cannot be silently swapped for a 1980 crash photograph.
- Width target is `min(960, source native width)`, full-frame aspect ratio preserved, no upscale or silent crop, full-size access retained for maps/labels. No candidate is authorized for caching/rehosting or production writes.
- This update changes only isolated draft verification code/test/audit/docs. No WordPress, homepage, third-party mirror, deployment, merge or paid API work.
