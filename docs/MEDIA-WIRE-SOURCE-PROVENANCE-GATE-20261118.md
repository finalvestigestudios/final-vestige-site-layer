# Final Vestige image transfer QA — source-provenance hardening (Nov 18 2026, 10:25 PST)

## Actual defect in existing 76%-claim evaluator

Prior to this change, the *wire parity* consumer validated that `authored_src`, `current_src`, `final_url`, and `source_identity` were syntactically HTTPS, but did **not** test whether they referred to the same upstream image. The before/after comparison trusted the supplied `source_identity` text. An image request could be silently changed to a different image while claiming the old `source_identity`, allowing a false visual/source-integrity pass (even though external QA was still separately required).

New offline helper `qa/media-recovery/image_wire_source_guard_20261118.cjs` is imported into `qa/media-recovery/image_wire_parity_gate_20261118.cjs`. It:

1. Reconstructs the canonical upstream image and immutable publisher query parameters from the authored URL, refusing a mismatched `source_identity`.
2. Binds browser `current_src` and actual final image URL to the authored photo, allowing legitimate Jetpack responsive changes (`i0`/ `i1`/ `i2` hosts, `resize`/`fit`/`w`) but not changed upstream path, crop keys or publisher parameters.
3. Requires image slot identifiers to belong to the actual post ID (e.g. `621:0` belongs to post 621).
4. **Fails closed on changed redirects/source identities.** An archival move from `www.floridamemory.com` to `floridamemory.com` is not automatically treated as the same raster. Redirect provenance, image pixel/content proof, and any replacement approval remain manual gates.

This is **not** a browser probe, not a new collector, and not an authority to change or localize WordPress images. Source identity is still only one component of independent browser visual QA.

## New read-only source recheck

Machine ledger: `qa/media-recovery/p0_origin_2_recheck_wire_integrity_20261118_1025.json` contains **two exact published image URLs** and current independent public-retriever origin observations:

- USS Tang `274:6`: [War History Online original](https://www.warhistoryonline.com/wp-content/uploads/sites/64/2016/04/uss_tang_ss-306_rescues_airmen_off_truk_in_1944-640x432.jpg), source retriever HTTP **404**. [Navy catalog 80-G-227989](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227989.html) is an archival candidate, **exact raster/crop and item rights HOLD**.
- Sunshine Skyway `287:5`: [St. Pete Catalyst original](https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg), source retriever HTTP **404**. [Florida Memory RC09237](https://floridamemory.com/items/show/32083) depicts a **different photograph**, so it is not an automatic replacement. Item reuse and dimension verification HOLD.

The Jetpack URLs were inaccessible to the independent retriever. **Neither image is proven broken to real visitors.** Both `guest_http`, `guest_decode`, and `guest_transfer_bytes` remain null. Do not conflate an origin HTTP result with a browser render outcome.

## Rights, 960px media and rollback plan

Use **Site QA #154's existing** logged-out Chrome desktop/mobile collector. Acquire the authentic image's final GET, MIME, decoded raster dimensions, screenshot, SHA-256 and actual deduplicated cold CDP wire bytes before deciding whether a fix is needed. If a source is genuinely missing, identify the exact primary-source photograph and accession (Navy, USCG, Florida Memory, National Archives), confirm item-level reuse/credit/copyright and exact image/crop. Never borrow a merely similar historical image as a silent substitute.

Only after explicit editorial and rights clearance: make a derivative `width = min(960, original_native_width)`, `height = round(original_native_height × width/original_native_width)`; do not upscale, stretch or introduce false detail. Stage a WordPress Media Library copy **only in an approved nonproduction workflow**, with source catalog, rights, credit, image SHA-256, descriptive ALT text, media ID, mapping to original post:slot, responsive `srcset` selection, guest screenshot comparison and a reversible rollback to the prior attachment/URL and post revision. Do not bulk mirror third-party origins or touch Gutenberg blocks in this draft.

**Baseline segregation:** Oct 30 historical worklist 61 posts / 355 source images / 288 classified offsite; Site QA #154 listed 286 offsite (two-reference delta still unresolved). The newer 66-post census is a different cohort. The 42 supposedly broken images are not visitor-browser verified, and the 76% image transfer reduction is **not** measured. Current 20 media originals above 1.5MB (64,385,752 stored bytes) must never be described as browser transfers.

## Validation and release gates

- Exact new Git helper and committed test file verified through Git readback. Native Node 22.16.0: **15/15 committed tests pass** including unchanged responsive source and rejects for silently changed currentSrc, final URL, source label, post slot, immutable crop/query, HTTP and unreviewed redirects. See test `qa/media-recovery/test_image_wire_source_guard_20261118.cjs`.
- Updated existing consumer is an isolated fail-closed QA-only change; the **existing 22-test suite, full historical 79-case parity suite, native all-data CLI and repository CI are not yet claimed passed**. No guest Chromium dataset was obtained.
- No WordPress production writes, caching/rehosting or downloads, homepage design changes, article block rewrites, merges, deployments or subscription spend.
