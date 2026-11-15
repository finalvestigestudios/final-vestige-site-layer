# FV Media Recovery: Part 05 live Commons sources — November 12, 2026

## Read-only verified batch
Eight published WordPress articles **256, 255, 254, 253, 252, 221, 220, 219** were read in authenticated edit context and reconciled to frozen PR #183 Part 05 (Git blob `9b16b828342a9ac338f3e65610fd3d8d508355e9`). **54/54 original image SRCs and 54/54 ALT descriptions match**; zero missing or added image slots. All **54 images are Wikimedia Commons Special:Redirect/file** original sources, and **54/54 raw stored IMG tags lack explicit width/height and srcset**. This is actual markup evidence, not proven CLS, blur or broken loading. It does not justify risky post-block rewrites.

[Machine-readable 54-row exact-URL and source-candidate audit](../qa/media-recovery/live_part05_8posts_54_commons_20261112.json) provides original and current SRC and ALT, WordPress modification dates, 54 authoritative catalog candidate mappings and item-specific rights notes from existing full register blob `4965a862f7de7de46c1f4a1e26f3ca70a8c38805`, conditional 960px/no-upscale plans, and **null** actual visitor origin HTTP, redirect/decoded-pixel/transfer measurements. No candidate is precleared for copyright, pixel identity or publishing.

[Read-only fail-closed validator](../qa/media-recovery/validate_live_part05_54_20261112.cjs) and [32 adversarial plus one control test](../qa/media-recovery/test_live_part05_54_20261112.cjs): **33/33 passed in isolated V8**, using same source prepared for native Node. Native Node CI and logged-out Chrome not run.

## Next decision
Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) retains the existing sole visitor-browser collector. First confirm the suspected P0 originals `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Its subsequent Commons batch should capture original `src`, rendered `currentSrc`, redirect request lineage, final uncached GET status and MIME, decoded image dimensions, CSS viewport×DPR, image transfer bytes, and visual scene integrity. No duplicate browser collector.

The historical cohort remains **61 posts / 355 inline images / 288 stored external images / 118 Commons redirects**; this 54-row Part 05 subset is not additional traffic. The reported **42 broken originals remain guest-unconfirmed** and **76% claimed wire savings is unmeasured**. 15 WordPress originals exceed 1.5 decimal MB, together **47,096,779 stored bytes** — not actual network transfer. 960px is a maximum conditional candidate, not a substitute for native resolution/DPR and map/figure legibility checks.

No external binaries downloaded or cached, no WordPress production or homepage writes, no publication/merge/deployment and no subscription spending. All code and evidence isolated to draft PR #1703.
