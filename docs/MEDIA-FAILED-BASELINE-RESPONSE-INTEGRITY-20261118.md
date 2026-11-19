# Media P0 — broken-baseline image transfer integrity (2026-11-18 14:31 PST)

**Scope:** Media Recovery draft PR #2747 only; collaboration with the existing Site QA #154 browser collector. This is not homepage design work, a WordPress edit, or permission to rehost any asset. The October 30 `docs/IMAGE-WEIGHT-WORKLIST.md` was read through historical Git blob `9cdf7af84175883775aaebf55ffa5ca77b33e423`; it is not present at the current branch path.

## Blocking issue fixed

The existing 76% image-wire parity gate required every baseline image to have `mime=image/*` and a strictly positive encoded transfer length. A real broken `<img>` request producing **HTTP 404 + `text/html`**, or a verified zero-byte failure, therefore invalidated the **before** cohort. That prevented measurement of the very before/after recovery scenarios the media team is assigned to investigate. In addition, treating error-page HTML as image bytes would overstate the image-bandwidth denominator.

The new pure helper `qa/media-recovery/media_failure_wire_semantics_20261118.cjs` is consumed by the existing `image_wire_parity_gate_20261118.cjs`, **not** by a new collector. It implements:

| Case | Baseline (before) | Remediated (after) | Image-wire byte accounting |
|---|---|---|---|
| Decoded HTTP 2xx image, positive CDP encodedDataLength | Accept | Accept | Count transferred image bytes |
| HTTP 2xx image MIME, decode failure, positive encodedDataLength | Record broken | Reject | Count genuinely transferred image bytes only |
| HTTP 2xx image MIME, failed decode, measured zero bytes | Record broken | Reject | Zero |
| HTTP 404/5xx failed decode, HTML/text/plain or image MIME, measured bytes including zero | Record broken | Reject | **Exclude error-response body** |
| HTTP 404 falsely recorded as decoded | Reject | Reject | Zero |
| HTTP 2xx HTML masquerading as a decoded image | Reject | Reject | Zero |
| Browser network failure with no HTTP response/verified response length | HOLD | HOLD | No invented zero |
| Cached, service-worker, missing or inconsistent transfer evidence | HOLD | HOLD | No claim |

Both phases still require the existing logged-out guest Chromium instrumentation, complete image request coverage, actual final numeric HTTP responses, CDP encodedDataLength, decoded state, `naturalWidth`/`naturalHeight`, image-slot provenance, no cache or service worker, screenshots and independent trace authenticity review. A 404 observed by a **public retriever** is only a *candidate* until the Site QA browser records its actual status.

The *before* vs *after* policy is deliberately asymmetric: the baseline may be broken, but **all after image slots must decode successfully**. No savings may be published merely because the accounting helper returns a threshold; independent desktop/mobile waterfall, image identity, perceptual visual parity, LCP/CLS and rights review remain mandatory.

## Current evidence and source review

The machine-readable P0 crosswalk `qa/media-recovery/failed_baseline_source_recheck_20261118_1431.json` pins seven exact published Jetpack URLs and their original third-party URLs to the earlier 14-slot queue (Git blob `7d2c71e5770e7bca7a973076102b7e64634d2d8d`). Two original origins were independently checked again on **November 18** and returned **HTTP 404 to the public retriever**:

- 285:5 Three Mile Island — `https://images.saymedia-content.com/.image/ar_16%3A9%2Cc_fill%2Ccs_srgb%2Cfl_progressive%2Cq_auto%3Aeco%2Cw_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg`. This is a **movie-related** still/crop; a generic reactor image is **not** an exact-photo replacement, and rights remain HOLD.
- 287:5 Sunshine Skyway — `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg`. Florida Memory RC09237 depicts the disaster but is **not** the same documentary photograph. No silent substitution is permissible.

USS Tang 274:6 has earlier origin-only 404 evidence and Navy accession 80-G-227989 as a photo-identity lead; Scotch Cap 418:1–2 have only retriever 403 responses, with 418:1 official USCG portrait VIRIN 210330-G-DE713-0002; Hebgen 407:1 and NRC/UCS 285:2 are retriever-wrapper ambiguities. **All seven guest-browser statuses, image decodes and transfer bytes remain unknown.** In Teton 291:2, a confirmed source-side street-cleanup photograph contradicts a dam-breach caption; retain the separate editorial review and NARA candidate NAID 28894685.

## Test and release evidence

- **16/16 native Node 22.16.0 tests passed** against the new helper and dedicated tests, including genuine 404 HTML, response-error byte exclusion, corrupt 2xx image, zero bytes, false decode, service worker, cache and strict after recovery. These two files are byte-identical to the verified Git blobs.
- Two additional tests were added to the **existing** sitewide parity fixture to assert a 404 baseline across both historic 61-post mobile/desktop cohorts and to reject an unrecovered 404 after. These new integration tests were **not executed in native Node** within this runner, and full repository CI / guest Chromium remain pending.
- The historical **61 posts / 355 image slots** and current **66 posts / 361 image slots** are separate measurement cohorts. Claims of **42 visitor-broken images** and **76% measured reduction** are **not verified**.
- Twenty originals over 1.5 MB decimal total **64,385,752 stored bytes**, not transferred bytes; five high-priority PNG originals without authored `srcset` total **13,267,538 stored bytes**. Actual decoded cold transfers, not WordPress originals or failed error documents, determine savings.

## Safe media recovery sequence

Site QA #154 runs its existing logged-out desktop/mobile Chromium capture first, with URL, final HTTP/redirect, decoded dimensions, screenshot, and cold CDP network transfer per slot. Media Recovery then maps only genuine visitor-broken images to **the exact historical photo** in an official Navy, Coast Guard, Florida Memory, USGS or National Archives catalog. Preserve item accession, current URL, author/credit, source restrictions, item-level rights, caption date, and original-asset SHA-256. Do not assume that government hosting makes a photograph public domain, or that a thematically similar image is interchangeable.

For an **approved** asset only: prepare a proportional derivative **no wider than 960px**, never upscale or crop misleadingly; compare its decoded visual identity against the approved master; plan a WordPress Media Library item with rights/credit metadata and locally cached responsive variant (prefer WebP/AVIF when lossless visual inspection permits). Test only in isolated staging; preserve exact existing Gutenberg block structure, caption semantics, permalink and a rollback reference. No blanket scraping, live WordPress write, media rehosting, risky post-block rewrite, merge, deployment or subscription spend is authorized.

**Release status: HOLD.** The helper corrects baseline accounting; it does not certify a recovery or authorize the 76% claim. A separately known limitation remains: the parity gate's source-identity guard must eventually reconcile *reviewed and approved replacement identities* without silently accepting substituted photographs. That is a distinct follow-up QA change, not a production task.
