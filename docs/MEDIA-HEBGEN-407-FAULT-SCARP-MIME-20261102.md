# Hebgen Lake 407:1 — USGS fault-scarp MIME/source recovery decision (2026-11-02)

**Scope:** media dependency recovery only, separate from homepage design and Site QA PR #154. **No production changes or media downloads.**

## Fresh source verification
Read-only, authenticated WordPress `posts.get(id=407, context=edit)` returned published post *The Lake Wasn’t There Yesterday*, modified `2026-10-29T18:30:30`. Its slot **407:1** still uses:

- **Published image URL:** `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg`
- **Published ALT:** “Fresh fault scarp near Hebgen Lake produced by the August 1959 earthquake.”
- **Frozen source:** `qa/media-recovery/parts/02.json`, Git blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`.

The independent text/web retriever **refused the exact published URL** with a wrapper **400 “Unsupported content-type: binary/octet-stream”**. That is **not** a 400 from the asset origin, not a measured `Content-Type` from logged-out Chromium, not a browser decode failure, and not confirmation that site visitors see a missing photo. It is nevertheless a concrete **MIME/anti-hotlink compatibility risk** warranting a targeted Chrome image GET test.

## Item-matched first-party archive alternative
The official USGS [Hebgen Lake fault scarp in 1959](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) record credits **J. R. Stacy (USGS)** and states **Sources/Usage: Public Domain**. Its **Original** link resolves to the separate path:

`https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg`

That official original **displayed in the independent image renderer**, with a **1000 × 1000-pixel rendered canvas**. A conditional square **960 × 960** local derivative would remain below the renderer dimensions, preserve the aspect ratio, and avoid upscaling. The 1000² size is *renderer-observed*, not a saved-binary header read or authenticated archival master-dimension attestation.

**Relationship:** This official URL shares the `img7535.jpg` filename with the published source, and the USGS page explicitly offers it as “Original.” It is a **strong same-item recovery candidate**, but the published and candidate bytes have **not** been downloaded, hashed, visually compared side-by-side, or proven binary-identical. The current ALT is retained pending scene/crop review; do not substitute other fault-scarp scenes merely because they depict the same earthquake. Avoid inventing an HTTP 200 for the candidate; the independent image viewer succeeded, but origin headers are not recorded.

## Rights / WordPress staging gate
The USGS catalog's Public Domain statement and credited USGS photographer provide a positive basis for **item-specific review**; they do not establish byte-for-byte identification, approve an external image from another custodian, or authorize this automation to upload media. Before any staged migration, require: source asset/right-of-reuse verification for the precise binary; visual comparison of current crop and official original; credit **J. R. Stacy / USGS**; natural dimensions and MIME inspection; bounded 960px/no-upscale derivative (only if source binary supports it); optimized JPEG/WebP sizing without obscuring the scarp, jeep or historical context; internal WordPress Media Library alt/credit and direct image reference **in staging only** with rollback mapping; before/after logged-out Chrome screenshot and network-byte capture. **No Gutenberg block rewrite, first-party cache, image download, WordPress post/media write or paid tool use is authorized now.**

## Site QA #154 handoff (do not duplicate browser instrumentation)
Please inspect **407:1** within the existing high-priority queue (285:5, 287:5, 418:1/2, 407:1). Capture the *actual* currentSrc, final image GET URL, redirects, HTTP status, response MIME, `X-Content-Type-Options`, decode/naturalWidth/naturalHeight, request ID/transfer bytes and desktop/mobile screenshot. Specifically test whether `application/octet-stream` is delivered to Chromium and, if so, whether the browser decodes or blocks it. Revisit any caching only after confirming a visitor-visible defect and clearing source-specific rights. Do not modify Site QA's existing PR, classifier, probe or drafts.

## Evidence and limits
- [Machine-readable ledger](../qa/media-recovery/hebgen_407_fault_scarp_mime_20261102.json) captures precise URLs, renderer result, copyright, conditional geometry, unknown browser fields and release HOLD.
- [Offline validator](../qa/media-recovery/validate_hebgen_407_mime_20261102.cjs) fails closed on fabricated HTTP status, invented binary-match, unauthorized reuse, wrong image/source URLs, invalid 960px geometry and measured-savings claims.
- [30-case negative/positive regression suite](../qa/media-recovery/test_hebgen_407_mime_20261102.cjs): **30/30 isolated V8 cases PASS** before publication against the in-memory code/audit; native Node and real browser not yet run.
- Site-wide source census remains **61 published posts, 355 stored image references, 288 offsite source references**. There are **13** WordPress originals >1.5 MiB. The alleged **42 broken images** still lack visitor-browser proof; **76% transfer savings** remain unmeasured; **production repairs = 0**. Storage size and browser wire size are different quantities.
