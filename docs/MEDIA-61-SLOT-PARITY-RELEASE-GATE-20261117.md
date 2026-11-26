# Media Recovery: missing-image-proof acceptance before any 76% claim

Date: 2026-11-17 08:27 Pacific. Draft-only isolated QA, with Site QA #154 as the **only** guest Chromium collector. No homepage visual design, WordPress editing, image downloads, rehosting, merging, deployment, or spend.

## Newly demonstrated safety gap

The existing `qa/media-recovery/assess_image_wire_reduction.cjs` measures the transfer of the `image_requests` array supplied by a page and relies on an unverified `visual_slots_preserved:true` flag. It does not independently join all 355 historical inline authored image slots to decoded network records. A purported 76% transfer reduction could therefore be *consistent with missing images*, not an improvement. The existing evaluator already refuses to certify the sitewide claim; the additional gate makes the missing-slot failure testable rather than relying only on a self-report.

## New fail-closed, offline source-vs-guest acceptance

`qa/media-recovery/slot_parity_61_20261117.cjs` accepts **exactly eight SHA-pinned archival JSON source inventory parts** from draft #183 (`qa/media-recovery/parts/01.json` through `08.json`) and optionally a normalized `fv-siteqa-image-slot-parity-v1` capture from Site QA #154. It validates Git blob identity for each of the eight sources, 61 unique posts, 355 contiguous image slots, 288 authored offsite references, and the explicit null original-browser-HTTP status. After supplying a capture, each paired post must match the historically pinned source URL and modification revision, contain every expected slot, record a source-matched currentSrc/GET request, image MIME, numeric 2xx status, decoded nonzero pixels, safe cold CDP transfer bytes, complete lazy loading and a screenshot fingerprint/review marker. No dropped, duplicated, cache-hit, service-worker, unrelated-origin or unknown MIME image can quietly count as a transfer saving.

Run locally from a materialized checkout of source draft #183; source parts are not duplicated in media PR #2747:

```
node --test qa/media-recovery/test_slot_parity_61_20261117.cjs
node qa/media-recovery/slot_parity_61_20261117.cjs qa/media-recovery/parts/{01..08}.json
# Append Site QA's sanitized normalized slot-parity capture file to the above command when it exists.
```

These parts were independently fetched from GitHub at commit `4366489a68620d26592d8438b4402feb453c3166` and their blob SHAs pinned in the evaluator. The new 32-case suite passed locally under native Node 22.16.0. The P0 image collector itself is **not** duplicated or modified.

## Real P0 image queue / strictly unverified delivery

Site QA's six priorities remain `285:5`, `285:2`, `287:5`, `418:1`, `418:2`, `407:1`. Source reader 404 for SayMedia 285:5 and publisher 287:5, retriever 403 for Defense 418:1 and USCG 418:2, UCS 285:2 redirect-wrapper error, and unsupported octet-stream for 407:1 **are not verified guest HTTP failures**. Exact authored/currentSrc URLs and replacement catalog leads remain in draft #2747 six-source ledger and USGS Hebgen ledger. USGS 407:1 official alternate image path `.../thumbnails/image/img7535.jpg` is catalogued Public Domain and J. R. Stacy; neither same-crop binary nor native pixel size is verified. The Skyway moved publisher image credits University Press of Florida; rights are not cleared. The 600×463 USCG museum preview must not be upscaled. No automatic replacements.

## Claim and recovery gate

The only defensible formula is `100 × (1 − Σ CDP after image-received bytes / Σ CDP before image-received bytes)` for identical page set, device, viewport, network, cache state and image completeness. A strict 61-post/355-image self-reported match is still `ALL_355_SELF_REPORTED_REVIEW_REQUIRED` and NEVER certifies 76%; independent screenshot/frame, binary, rights and live traffic reviews are still required. The 20 WordPress originals above 1,500,000 decimal bytes total 64,385,752 **stored bytes**, not actual visitor downloads. Later 66-post census is a different cohort. For an approved asset, use a reversible WordPress Media Library staged attachment with credited primary-source rights, verified source frame/crop and SHA-256, native-limited 960px long-side sizing without upscaling, explicit width/height and responsive `srcset/sizes`; no production update before separate signoff.

The first current-run tool probe attempted cold HEAD of a Jetpack P0 URL; DNS failed in this isolated runner. The public reader also cannot open those Jetpack paths. Neither is evidence that a guest image is broken. Browser status/currentSrc/decode/screenshots/wire bytes remain unavailable here.
