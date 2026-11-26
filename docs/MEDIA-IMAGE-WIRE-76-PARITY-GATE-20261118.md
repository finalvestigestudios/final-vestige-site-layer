# Final Vestige image wire parity gate — 2026-11-18 09:28 PST

Read-only media-performance and third-party recovery engineering only. No interim-lead homepage design work.

## Why this is needed

The historic Oct 30 `docs/IMAGE-WEIGHT-WORKLIST.md` (old Git blob `9cdf7af84175883775aaebf55ffa5ca77b33e423`, absent at current branch) audited **61 posts / 355 source image tags**; source-origin classification is **288 offsite in that document versus 286 in Site QA #154**, a two-reference discrepancy requiring version/reclassification review. Today's broader **66-post** census is a distinct cohort. Source-level origin errors are not Jetpack/CDP guest failures. The **42 alleged broken images** and **76% image transfer reduction** remain unverified.

Current oversized library originals: 20 >1,500,000 B, 19 >1.5 MiB, 64,385,752 **stored bytes** total. Five no-srcset first-party PNG originals hold 13,267,538 stored bytes. These figures **cannot** be used as visitor wire-byte denominators.

## New safe deliverables

- `qa/media-recovery/guest_wire_capture_queue_20261118.json`: **14 exact published image slots** from the existing 51-URL VIEW ledger Git blob `2c707d4ff6424e67264db1a4048afce9eba324b6`. Seven P0 suspected visitor failure slots (285:5, 285:2, 287:5, 418:1, 418:2, 407:1, 274:6), then five no-srcset PNGs (34–38) and Malbone 621:0–1. Numeric origin HTTP 404s for 274:6 and 287:5 are public retriever observations only, not guest `currentSrc` status. All unknown guest fields remain **null**.
- `qa/media-recovery/image_wire_parity_gate_20261118.cjs`: offline existing-collector export consumer. It strictly requires a real logged-out Chromium CDP trace reference, trace SHA-256, cache disabled, bypassed service worker, complete image request coverage, per-image `current_src`, `CDP_ENCODED_DATALENGTH` wire bytes, final response/MIME, decode/raster, screenshots, unique request ID and stable source identities. Network requests are deduplicated by request ID, not by number of HTML tags. Stale/cached/missing measurement, changed or missing image slots, source substitutions without item-level rights + exact-frame approval, and dimensions >960px/no-upscale violations are HOLD.
- `qa/media-recovery/test_image_wire_parity_gate_20261118.cjs`: synthetic tests only, **not** proof of any site measurement.

Comparison: same post IDs, URLs and asset identifiers in before/after; same cold collection method and coverage for **both desktop and mobile**. For a 61-post historical claim, all 61 must appear in **both** stages on **both** devices; a modern claim needs all 66. For each device, image transfer savings = `(sum_distinct_before_transfer_bytes - sum_distinct_after_transfer_bytes) / sum_distinct_before_transfer_bytes × 100`. The threshold must meet >=76% **on both devices**; a 14-slot triage batch is never sitewide evidence. The runner deliberately always returns `claim_publicly_verified=false`: even a passing submitted dataset awaits independent review of authentic traces, visual parity, image identity, captions/ALT and LCP/CLS.

## Remediation without production risk

Use **Site QA #154's existing** logged-out desktop/mobile Chromium collector. Confirm Jetpack `currentSrc` / numeric final GET / decode / screenshot before deciding any image is missing. Do not use web-retriever 403/404/500 wrappers as visitor outage evidence. For genuinely missing images, reconcile the exact historical accession/photo/crop from Navy, USCG, Florida Memory or archives; record item-level copyright/right-to-reuse, credit and master SHA-256. Reproduce at <=960px native width, preserve aspect ratio, never upscale. After item-level approval, stage a **cached/WordPress media** attachment and its mapping to the exact source slot for human preview, with original URL+revision, HTML screenshot, captions and rollback documented. No automated Gutenberg post-block rewrites, unlicensed scraping/mirroring, WordPress production writes, merges, deployments, subscription spending, or homepage changes.

Run in native Node: `node qa/media-recovery/test_image_wire_parity_gate_20261118.cjs`. Optional existing-collector export: `node qa/media-recovery/image_wire_parity_gate_20261118.cjs export.json`.

**No actual guest-browser export exists in this sprint**. All 14 guest statuses/wire bytes are explicitly unknown; 42/76% claims remain HOLD.
