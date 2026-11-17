# P0 media recovery: guest evidence to reversible staging — 2026-11-16 PT

**Scope:** image source integrity only; NOT homepage visual design. This is an offline preflight, not a browser collector, downloader, publisher, or production approval.

## Why this batch matters

We now have a single **six-slot restoration staging gate** tied to the exact WordPress EDIT/VIEW URLs and post revision timestamps in `wp_view_proxy_26_20261115.json` (Git blob `dcb735226eb71fcba302b38ae3ab3a73751fe2a8`). The Site QA #154 collector still owns cold logged-out Chromium/currentSrc/GET/MIME/decode/wire-byte/screenshot acquisition. This code does not duplicate it. Its input is a *manual normalized projection* of that collector's evidence and must be independently cross-checked; a JSON assertion of Chrome origin is not self-authenticating.

**Major source hygiene finding:** A Wikimedia Commons `/wiki/File:...jpg` URL names an **HTML record**, not necessarily an image file. The gate now rejects HTML catalog routes masquerading as candidate binaries even when their paths end in `.jpg`. Related-topic archive photographs also cannot silently replace the original scene or crop.

## Six P0 slots (all are HOLD)

| Slot | Source/issue | Candidate source-file readiness |
|---|---|---|
| `285:5` | Three Mile Island SayMedia photograph; Commons 819×614 is a related different crop | NO verified same-crop binary; Wikimedia record only |
| `285:2` | UCS control-panel image, prior publisher host redirects | NO verified exact replacement master or rights |
| `287:5` | Sunshine Skyway St. Pete Catalyst image, publisher-host migration | NO item-level reuse clearance; Florida Memory RC09236 is a different scene |
| `418:1` | Coast Guard portrait VIRIN `210330-G-DE713-0002` | Official same-file route identified and PD item catalog noted; original hash/rights conditions/guest failure unresolved |
| `418:2` | Coast Guard Scotch Cap debris | NO accession-verified replacement master or rights |
| `407:1` | Hebgen USGS legacy Original vs sibling-catalog Original path | Official alternative JPEG path identified; same pixels/native geometry/guest failure unresolved |

All six guest HTTP statuses, `currentSrc`, decode states and transferred bytes are **unknown**. Tool-wrapper 403/404 and image-reader failures are not browser HTTP evidence. No item is declared browser-broken; no original image has been downloaded or rehosted.

## Machine-readable deliverables

- `qa/media-recovery/p0_image_staging_custody_20261116.json`: exact six stored and Jetpack-rendered URLs, post revision pins, authoritative source candidates and related records, null HTTP status, rights HOLD, 960px cap, differing 61/355 and 66/361 cohorts.
- `qa/media-recovery/assess_p0_image_staging_20261116.cjs`: deterministic, pure evaluator with optional read-only JSON CLI. Holds unless logged-out cold browser failure, redirect chain, MIME, naturalWidth=0, screenshot/review, approved item rights, exact visual/crop fidelity, binary SHA-256, native dimensions and same WordPress revision are all present.
- `qa/media-recovery/test_assess_p0_image_staging_20261116.cjs`: 49 synthetic Node tests (a valid *synthetic* complete case can at most return `STAGING_REVIEW_ONLY`; mutations fail closed). Tested in Node 22.16.0 locally: **49 passed, 0 failed**, with committed evaluator source Git blob `103ea1a5927e8fbcbc818c4475603631629b8c6b` matching the local tested implementation. No remote CI was triggered.

Run, without any browser, network, or WordPress connection:

```sh
node --test qa/media-recovery/test_assess_p0_image_staging_20261116.cjs
node qa/media-recovery/assess_p0_image_staging_20261116.cjs qa/media-recovery/p0_image_staging_custody_20261116.json
```

The baseline produces six `HOLD` decisions, no staging candidate, zero writes and unknown savings. Future read-only normalization of #154 evidence may be supplied as a second JSON argument and separately approved rights/crop/native-size evidence as a third. These are **not** license to upload media or modify published blocks.

## Safe restoration release plan

1. Site QA #154 verifies genuinely failed images with cold logged-out Chrome: exact `currentSrc`, redirect chain, numeric GET status, MIME, `naturalWidth`, failed decode, screenshot, and encoded image bytes. Preserve distinct 360px and 1440px visual checks.
2. Media Recovery selects the **same frame** from an official archival master where available; record rights-specific catalog citation and required attribution, file hash, native dimensions, and conditional output `width=min(960,nativeWidth)`, height proportional, no upscale.
3. After separate owner approval, stage a reversible WordPress Media Library asset. Preserve old URL, ALT, caption, original block tree and post revision for rollback; do not rewrite Gutenberg post bodies automatically.
4. QA confirms post-staging image fidelity/responsive layout and repeats cold guest byte measurements. Only the existing measured cold-wire assessor can evaluate the claimed 76% reduction; WordPress original storage bytes cannot.

**Unchanged inventory and measurement constraints:** historical 61 published articles / 355 inline sources vs newer 66/361; original 42 reported breaks **not confirmed**; claimed 76% visitor reduction **not measured**; 20 current WordPress originals above decimal 1.5MB total 64,385,752 **stored** bytes, not actual downloads. No production writes, binaries, caching, post block rewrites, homepage work, merges, deploys or subscription spend.
