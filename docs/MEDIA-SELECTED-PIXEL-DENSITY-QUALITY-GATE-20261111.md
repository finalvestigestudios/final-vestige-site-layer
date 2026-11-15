# P1 source-asset retina/density safeguard — November 11, 2026

## Reproduced verification defect (synthetic, NOT a production finding)

Draft #1703's frozen eleven-slot visual verifier previously required `naturalWidth >= paintedCssWidth` and matching aspect ratios, but never verified **decoded physical resource pixels** at the browser's device pixel ratio. A 320×240 physically decoded image painted 320×240 CSS pixels at DPR 2 still passed its visual-resolution gate, despite providing only 1 physical source pixel per 2 display pixels in each dimension. With synthetic 1000→240 CDP bytes, this could report a 76% network reduction while degrading sharpness on a retina display. This concerns **verification software only**, not a measured visitor condition.

## Safe isolated correction

In `qa/media-recovery/verify_p1_11_bound_pair_20261111.cjs`, the P1 eleven-slot adapter now requires a `BROWSER_DECODED_CURRENT_SRC` physical width/height, bounded by verified original pixels, consistent with original image shape (<=2.5% relative aspect drift), and at least `ceil(rendered_css_width * dpr)` and `ceil(rendered_css_height * dpr)`. A missing, reconstructed, fractional, stretched, underdensity or upscaled resource is HOLD, never an optimization success. Existing `naturalWidth`, painted geometry, crop, matched source, item identity, request lineage and rights restrictions remain in force.

**Collection handoff to Site QA #154:** the owner of the existing guest Chromium collector must attach selected-source resource physical dimensions to the same completed Image request and `img.currentSrc`, with a documented browser-decoding method that does not trigger additional image downloads. A WordPress original dimension, `<img width>` or `naturalWidth` alone is not acceptable physical-resource proof. Do not create another collector, alter Site QA's existing draft, or weaken proof requirements to make fixtures pass.

## Exact batch and release discipline

See [machine-readable eleven-slot audit](../qa/media-recovery/p1_11_selected_resource_density_gate_20261111.json) for each published original URL, 960px **conditional** no-upscale plan and unresolved rights. Frozen research: 61 historical posts / 355 inline / 288 external images; 42 earlier reported broken images **not confirmed in a visitor browser**. Expanded read-only media inventory: 15 originals above 1.5 decimal MB = 47,096,779 *stored-original* bytes, including 11 inline slots across eight posts = 38,480,915 B. None of those are observed visitor transfer bytes. The 76% transfer reduction has **not** been measured site-wide.

**Priority remains P0 missing-image evidence**: 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. In particular do not conflate Coast Guard Pettit portrait with the Scotch Cap ruins, or the TMI emergency-feedwater-tag panel with the relief-valve indicator.

This draft makes **zero** changes to WordPress, media binaries, cache, third-party hosting, homepage design, Site QA collector, publishing, mergers, deployments or paid services. Site QA needs to obtain real cold logged-out network and decoded-source dimensions before approving any media restoration or image-compression claims.
