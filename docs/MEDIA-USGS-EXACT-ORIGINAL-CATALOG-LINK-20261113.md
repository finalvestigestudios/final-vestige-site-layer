# P0 archive-source custody: USGS Hebgen original link (2026-11-13)

## New verified catalog-level finding

For post **407**, image slot **407:1**, the published original source URL is byte-for-byte the URL behind **Original** on the U.S. Geological Survey item [Hebgen Lake fault scarp in 1959](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0). USGS attributes the scene to **J. R. Stacy** and marks the image **Public Domain**. The catalog's **Medium** link also displays the photograph in an independent web retriever.

- Published/official **Original** link: `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg`
- Official **Medium** link: `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/medium/public/img7535.jpg?itok=q8Hes32z`
- An independent web retriever attempts the original and responds **400 / unsupported binary/octet-stream**, not a verified CDN-origin HTTP 400 and **not** a logged-out browser broken image. The catalog and medium preview prove an authoritative published relationship, **not** original binary digest, exact pixel equivalence, unbroken browser delivery, or native 960px dimensions.
- **Disposition: preserve the published original URL** until Site QA #154 produces valid cold guest failure evidence. If it actually fails, evaluate its catalog-linked Medium/Original paths in QA, verify their binary dimensions, full raster, provenance, credits and browser visual parity; do not assume a lower-resolution derivative is suitable at DPR 2.

## Other five high-priority sources (web retriever only)

| P0 slot | Independent web retriever | Candidate handling |
|---|---|---|
| 285:5 | wrapper 404 | Wikimedia TMI archive is a *different scene*, not identical-film-still restoration; review article narrative and rights |
| 285:2 | wrapper 500 / migrated UCS redirect inaccessible | Smithsonian commission report is not verified as the original figure; no drop-in swap |
| 287:5 | wrapper 404 | Same publisher's moved image displays; **pixel identity and University Press of Florida reuse rights unknown**. Source-link repair is different from third-party caching |
| 418:1 | wrapper 403 | USCG photo-catalog candidate, verify exact item/photo and rights at the item level |
| 418:2 | wrapper 403 | Lighthousefriends presents same-basename wreckage photo credited to **Coast Guard Museum Northwest**; no implied mirroring permission |

None of the six source-retriever outcomes represents an actual logged-out guest request/response. All six source HTML locations remain on the Site QA P0 queue. Source-only findings are not proof of failures.

## Machine-readable evidence / tests

- [6-row exact original/candidate/rights/960px audit](../qa/media-recovery/p0_catalog_original_link_custody_20261113.json)
- [Fail-closed validator](../qa/media-recovery/validate_p0_catalog_original_link_20261113.cjs) binds all six rows to Media Recovery's existing immutable P0 slot URL constants; distinguishes wrapper outcomes from unknown guest statuses, refuses invented dimensions and permissions, preserves the single confirmed catalog-original equality.
- [17-case regression suite](../qa/media-recovery/test_p0_catalog_original_link_20261113.cjs) checks URL slot binding, no false browser 400, no fake 76% savings, no synthetic rights grants, original link equality, unknown native pixels and 960px ceiling. **17/17 isolated V8 checks pass on the committed blobs**, with a test-only module + structuredClone shim. Full native Node against checked-out PR branch, repository CI and real logged-out Chrome remain outstanding. A separate local Node run of an equivalent predecessor validation suite also passed 17/17, but is not claimed to be execution against these exact Git blobs.

## WordPress media / performance plan (NO-WRITE)

1. Keep the six current source URLs and ALT/captions unchanged. Site QA #154 is exclusive owner of the existing cold guest Chrome/CDP collector and the priority order: `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`.
2. On a **real** verified failure, review the exact scene and publisher/primary-source item rights, attribution and derivative permission. Never download, cache, mirror or insert a third-party original without that approval. The USGS catalog asserts public domain for its specific image; this audit does not itself approve a WordPress upload.
3. Stage (not production) a **reversible** media upload/media URL proposal only after rights and original-master hashes, full-raster decoding, a maximum **960px width**, **no upscale**, aspect/crop preservation, and painted CSS width × DPR resolution checks. For long maps/figures, also verify label legibility. Preserve existing blocks/links and provide exact rollback URI and before/after screenshots.
4. Measure performance with authentic logged-out, cold uncached browser `Network.loadingFinished.encodedDataLength` and real `currentSrc` per image, record redirect chain, cache flags, content type, intrinsic/rendered dimensions, page viewport and DPR. Compute per-page observed savings as `(baseline visitor image bytes - candidate visitor image bytes) / baseline visitor image bytes × 100`, only for same-slot, same-scene and approved changes; source changes require independent historical-scene review. Compare LCP/CLS and multiple cold runs. **Do not equate stored WordPress originals with guest wire bytes.**
5. WordPress origins >1.5 **decimal** MB: **15 originals / 47,096,779 stored bytes**; 11 matched inline exposures = 38,480,915 stored bytes; the Vasa Jetpack `fit=1024` images already use transformed URLs. Treat the proposed **76%** as **unmeasured**, and the historical **42** reported broken images as **guest-unconfirmed**.

No third-party image bytes were acquired, cached or rehosted. No WordPress writes, homepage visual design changes, production deployments, merges or subscription spending.
