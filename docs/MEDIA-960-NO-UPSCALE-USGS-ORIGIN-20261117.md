# Media Recovery — no-upscale parity gate and exact USGS source custody

**Read-only engineering sprint, November 17, 2026 (20:22 PST).** Work scoped to image integrity and third-party source resilience. Homepage visual design remains with the interim lead; Site QA #154 exclusively owns guest-browser capture. Historical `docs/IMAGE-WEIGHT-WORKLIST.md` was read at commit `f69a12cd9241ea0f39cfcb74c669bb6f7fb10357`. This does not modify WordPress or request a deployment.

## Critical false-parity scenario and code fix

The existing offline `slot_parity_61_20261117.cjs` checked image decoding, minimum 480px long side, and <=2% aspect drift. However, it would still accept a **640×480 -> 960×720 enlarged image** or **4000×3000 -> 1280×960** derivative as visually eligible, provided HTTP status and byte assertions passed. Those cases conflict with the required **max 960px derivative width and no upscaling**. The first also risks hiding a low-quality enlargement behind a smaller encoded transfer.

The new fail-closed `preservesPixelGeometry` gate additionally HOLDs when the proposed after-image `natural_width > 960`, `natural_width > before.natural_width`, or `natural_height > before.natural_height`. Portrait dimensions such as **1500×3000 -> 960×1920** remain eligible, since the limit is **width**, not longest edge. Proportional downsizing such as **4000×3000 -> 960×720** remains eligible. Existing requirements remain: exact source slot coverage, successful decode, final HTTP 200, positive unique cold transfer bytes, valid redirects, screenshot-review evidence and no claimed automatic 76% certification. Checks never certify subject/crop identity or rights.

**Important scope limitation:** `naturalWidth` reflects the browser-displayed derivative, not necessarily the archive master. A higher-DPR responsive substitution can therefore produce a conservative false-positive HOLD; manual review with archive master dimensions is required. A HOLD is a safety gate, not proof of an image defect or proof that a new smaller derivative is appropriate. Production replacement remains prohibited.

**Verification:** eight additional targeted regression cases were added to the actual CJS suite (six unit, two assessor integration). **68/68 actual test functions passed under an isolated V8 CJS harness** with minimal URL, Buffer and crypto shims. This is **not a native Node test nor repository CI**; those remain outstanding. Source blob `a434606b6085c8cb6aa8e2cc0f51e71878591c78`, regression blob `3e48236d59664eae9931ea61d9e281dc690bbe28`.

## Primary-source record matched to actual published origin

High-priority Hebgen image **407:1** is published through Jetpack at:

`https://i0.wp.com/d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg?ssl=1`

Its underlying master URL `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg` is the **exact link labeled Original** by the official [USGS Hebgen Lake catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959), corroborated by [the second USGS record](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0). Both catalog records identify the 1959 fault scarp photograph as **Public Domain** and credit **J. R. Stacy**. This is a substantial source-identity and rights-policy confirmation at the **URL/catalog** level, *not* an approved media binary: original S3 read produced an unsupported binary-content error in the independent retriever (no verified origin HTTP 400), with master pixels, digest, guest decoding, cold wire bytes and visual exact-crop proof all unknown. The official catalog's medium preview loaded, but no files were downloaded or cached.

**Recovery disposition:** prioritize 407:1 in Site QA's existing guest collector. If a visitor defect is shown and rights/editorial checks are signed off, use the **same official USGS original file** (not a different photo). Inspect master SHA-256, native pixel size and source credit; compute `target_width=min(960,native_width)` with proportional height, never upscale, preview in a reversible media draft/staging plan. No WordPress upload/rehosting or Gutenberg rewrite is authorized here.

## Another live-origin candidate remains blocked

Sunshine Skyway **287:5** exact publisher origin `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg` returned **HTTP 404** to the independent retriever on November 17; the published `i0.wp.com` route is inaccessible to that retriever, *not a confirmed visitor failure*. Florida Memory [RC09236](https://floridamemory.com/items/show/32082) is **1980 accident-day context**, a different frame, not an approved replacement. Rehosting the relocated St. Pete Catalyst photograph remains on rights and binary-identity hold. No paid archive requests were made.

The machine-readable record [p0_asset_identity_and_geometry_20261117_2022pt.json](../qa/media-recovery/p0_asset_identity_and_geometry_20261117_2022pt.json) records exact URLs, method-specific status/null, source/rights reasoning, 960px constraints and QA ownership.

## Sitewide methodology and release gate

Historical `61 posts / 355 slots / 288 external authored origins` remains the pinned October worklist; current `66 posts / 361 slots / 294 third-party-origin routes` is a separate current published census. **42 reported broken images are not yet guest-confirmed**. A proposed **76% image-weight decrease is not measured**: only independently captured same-device/same-page cold **unique encoded image network bytes** for matched before/after requests can support such a calculation, accompanied by successful image decode and unchanged visual identity. Library total and hypothetical optimized bytes do not count. The **20 originals >1.5MB decimal total 64,385,752 stored bytes**, not visitor transfer bytes; their matching in responsive WordPress/Jetpack output must be tested rather than inferred.

**Release remains HOLD:** no WordPress writes, asset downloads, scraping, caching, mirroring, live block edits, homepage-design changes, merges, deployments or subscription spend. PR #154 owns guest screenshot/network capture; media draft #2747 contains only isolated QA/code and rights/provenance evidence.
