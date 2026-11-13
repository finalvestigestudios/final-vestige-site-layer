# P0 407:1 — USGS dual original-link verification (November 13, 2026)

**Scope:** read-only archival and current-CMS verification. No browser collector duplication, published-page change, upload, binary download or deployment. Site QA #154 owns uncached full-browser failure proof.

## New independently verified source fact
The live published WordPress post #407, *The Lake Wasn't There Yesterday* (modified 2026-10-29), still embeds `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg` at slot 407:1 and credits USGS/J. R. Stacy.

The USGS primary catalog [Hebgen Lake fault scarp in 1959](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0) supplies **that exact published URL** as its official **Original** hyperlink. Clicking it in the external retriever produced a **400 unsupported binary/octet-stream wrapper**. That is **not** an origin HTTP status, browser 404, or proof of a broken image.

A **second official USGS catalog entry** [same title](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) exposes a different **Original** hyperlink, `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg`. This second URL **rendered an image in the independent retriever** on 2026-11-13. Both catalog records describe the Hebgen Lake scarp, identify photographer J. R. Stacy, and mark the image **Public Domain**.

This establishes: official agency ownership of both link paths, exact original-source URL association for the published slot, an alternate official original-link **candidate**, and a format-dependent retrieval discrepancy. It **does not** establish the images' byte hashes, identical crop, native pixel dimensions, current guest HTTP status or quality/transfer differences. Matching `img7535.jpg` basenames are supporting provenance, **not cryptographic proof**.

## Stage-only release plan
1. Site QA's existing #154 collector captures a logged-out actual image request at post 407:1, original `currentSrc`, CDP request ID/HTTP response, decoded `naturalWidth/naturalHeight`, complete cache provenance, and `encodedDataLength`. No second collector.
2. If original genuinely fails in a visitor browser, independently compare both official USGS source variants **after item-specific rights and source verification**, including exact visual crop and metadata. Consider a single reversible staging-only external-source alternative, explicitly recording its new third-party dependency. Do not alter the live post.
3. If a first-party WordPress media asset is preferable, verify source-master rights, source SHA-256, credit line “USGS photo by J. R. Stacy”, native dimensions, and attribution in block caption/ALT. Conditional derivative `min(native_width,960)` wide, never upscale; check rendered CSS width × DPR and label/scene fidelity. Cache/upload **only after explicit approval**.
4. Compare repeat cold visitor image **network** bytes and visual quality on equal viewport/DPR. A proposed 76% saving is not evidence of achieved reduction. Roll back to original source promptly if image mismatches or introduces regressions.

## Evidence and ownership
- [USGS catalog original A](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0) — exact WordPress-hosted external URL as Original link; retriever unsupported-binary wrapper
- [USGS catalog original B](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) — alternative USGS Original link rendered in retriever
- WP post source: https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/
- [Site QA draft #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) — exclusive browser collector
- [Media Recovery draft #1703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1703) and [weight worklist in #183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183) — broader inventories
- Historical 61 posts / 355 inline positions / 42 reported failures (unverified); 15 oversized original WP files = 47,096,779 **stored** bytes; 76% cold visitor transfer saving **unmeasured**. Do not mix expanded 66/361 with frozen snapshot.

This narrowly isolated update goes into existing four-file P0 draft #1655, rather than overbroad #183/#1703 or Site QA's collector. Keep draft, do not merge or deploy.