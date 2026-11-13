# Media Recovery — same-URL image identity & P0 visual evidence gate
2026-11-12 Pacific · draft PR #1703 · Site QA PR #154 owns the browser collector

## Critical finding and safe engineering
The existing per-post cold-transfer comparator accepted a synthetic 76% transfer reduction for a **different photograph served from the same image URL**, provided CSS, source dimensions, `image_identity` (a caller-provided string), and ALT remained unchanged. Aspect ratio is not scene identity. CDN paths and reused URLs can change the image subject without affecting geometry.

`qa/media-recovery/compare_cold_pair_visual_parity_20261111.cjs` now **fails closed** without an independent per-slot side-by-side screenshot review, even if `current_src` has not changed. Each assertion is bound to the baseline/candidate cold-run IDs, selected image URLs, 64-character screenshot SHA-256 references, and editor confirmation of same scene, crop, and ALT fidelity. Existing source-change rights approval is still independently required. On missing/stale/negative review, returns `HOLD / MISSING_OR_STALE_INDEPENDENT_SCENE_REVIEW`; no savings or release claim.

**Integrity limitation:** the comparator verifies the *shape and binding of review assertions*, **not the screenshot PNG bytes or actual scene pixels**. It expressly returns `screenshot_artifact_bytes_verified:false`, and never grants `production_change_allowed`. Verify actual screenshot artifacts with a separate byte-bound verifier; a supplied hash or reviewer boolean must not be treated as cryptographic proof. Synthetic passing fixtures likewise do not prove the live site passes.

## Machine-readable handoff
- `qa/media-recovery/p0_same_url_scene_review_queue_20261112.json`: six unchanged original URLs, candidate source/catalog leads, retriever-wrapper outcomes (where recorded), null actual guest/origin HTTP, explicit rights and identity HOLD, no-upscale max-960px output, and exact evidence required. Input Git blob `a593817eabe42fd1f108882d8349a26e0c65b023`.
- Keep Site QA's queue **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**. **Do not create another guest CDP collector**. Return currentSrc, redirect lineage, actual GET HTTP status/MIME, natural dimensions, screenshot bytes/hash, rendered CSS width/DPR and `Network.loadingFinished.encodedDataLength`.
- Candidate mappings include UCS domain migration, Skyway moved publisher media, official USCG catalog, Coast Guard secondary copy, and USGS fault-scarp catalog. None is approved for rehosting. Florida Memory alternative photographs are different scenes and must not silently replace the publisher's Skyway image. Official hosting alone does not resolve donated-image copyright.
- Image source URL consistency, aspect-ratio preservation, and a secondary copy's filename alone do not establish identical pixels.

## Tests and verification
- Comparator exact committed file Git blob: `0f177764a28a75d4ba4df67e09cf803e9fb7da27`.
- Adversarial regression exact Git blob: `8c329d22e886b662c0a14cd0deb4596ccac76935`. **30/30 passed in the isolated V8 Node-compatible harness** on postcommit file readback (24 previous + 6 new).
- Historical synthetic fixture suite Git blob: `54899321270ca6e3ddabead6225596fa72e99dc4`. Adjusted to include per-slot review assertions. **61/61 simulated cold post pairs / 355 image slots passed the isolated integration smoke**. The full Node test runner, CI, genuine browser and screenshot-byte checks were NOT run.
- An attempted direct command-line HEAD of finalvestige.com in this isolated runner failed at DNS resolution. That is an environment limit, **not evidence of a site outage**. Independent web retriever statuses, if present in the prior six-source handoff, are not browser/origin status.

## Weight math and no-risk release plan
The frozen historical count remains **61 posts / 355 inline image slots / 288 directly external sources in the recovery ledger** (Site QA #154 classified 286, with two post-level discrepancies still unresolved). The expanded WordPress cohort has **66 posts / 361 source tags**, and **92 other published pages** were separately audited (60 inline tags, 48 external); do not blend these denominators silently. The historical 42 broken originals are still visitor-browser **unconfirmed**.

The 15 WordPress original files exceeding **1,500,000 decimal bytes** occupy **47,096,779 stored bytes**, not visitor transfer. Eleven are inline-matched in eight posts; five PNGs have no subsize metadata; three large Vasa originals already use Jetpack resized URLs, so original storage is not the actual download. A blanket 960px resize is **not acceptable** when a photograph paints at 1024 CSS pixels or needs high DPR, or if an archival map's labels lose legibility. Never upscale a smaller archival original. Keep a zoom-access path for technical maps.

A claimed **76%** reduction must be based on before/after cold visitor **image-network bytes**, counted once per unique completed request with identical scroll, viewport, DPR and page content; review visual fidelity and actual source rights independently. It is **not measured today**. A total-page-weight claim further needs CSS backgrounds, scripts and other loaded media; neither stored-file byte totals nor synthetic tests validate it.

## Release hold and rollback
No binary downloads, cache/mirroring, WordPress writes, Gutenberg rewrites, homepage visual changes, merge, deploy or paid call were authorized. Only after a genuine failed visitor image, independently bound scene/rights review, responsive-width feasibility and staging screenshot/CLS check should an editor consider a reversible WordPress media derivative. Preserve the original source markup and attribution for rollback. Site QA #154 retains the browser diagnosis; Media Recovery PR #1703 retains downstream safe engineering and rights/performance triage.
