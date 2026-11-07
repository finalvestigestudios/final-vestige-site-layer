# Final Vestige Media Recovery — Commons redirect inventory and 960px rights gate (2026-11-06)

**Scope:** Media Recovery draft PR #1228 only. This is a read-only WordPress source investigation and isolated QA code, not a production repair, guest-browser HTTP test, license grant, or image downloader. Site QA draft PR #154 owns visitor-browser verification and its existing collector. Interim lead owns homepage visual design.

## What was actually verified

Read **24 published WordPress posts** through authenticated **posts.get context=edit**, preserving original source URL and `post_id:inline_image_index` for each `<img>` in stored HTML. This confirms the previously aggregated **124 Wikimedia Commons `Special:Redirect/file` source references** from the 66-post / 361-image site census. All **124 exact source URLs are distinct**; each belongs to a published article with an exact canonical permalink and WordPress modified timestamp. The four machine-readable shards record all 24 articles and all 124 references.

Requested Commons URL widths — **79 `width=1280`, 17 `width=960`, 2 `width=900`, 26 with no `width` parameter**. Thus 79/124 source URL requests specify a width above the **960px proposed optimization ceiling**, but this is **not proof** that visitors receive a 1280px binary, that the native image supports 1280px, or that resizing would save any particular byte count. The current theme, browser DPR, redirect behavior, Jetpack, actual native widths and cold transfer are unmeasured. These 124 images are **source dependencies, not 124 broken images**.

Source audit files: `qa/media-recovery/commons_redirect_20261106_shard01.json` through `shard04.json`. Validate with `node qa/media-recovery/validate_commons_redirect_20261106.cjs` and `node --test qa/media-recovery/test_commons_redirect_20261106.cjs`. Both commands are offline and read-only.

### Six evidence-grounded native geometries — do not upscale

A separate six-row file crosswalks the **exact stored URL** and provisional Commons file-page candidate to published Commons catalog dimensions. One is an individually checked file page; the other five have native dimensions listed in the Commons St. Francis Dam category, **not** item-level license verification.

| Source slot | Historical image | Commons native WxH | Stored requested width | Safe conditional preview WxH | Source of size |
|---|---|---:|---:|---:|---|
| 268:0 | Archimedes Palimpsest manuscript page | **665×448** | 1280 | **665×448** (no upscaling) | [Exact Commons file page](https://commons.wikimedia.org/wiki/File:Archimedes_Palimpsest.jpg) |
| 166:2 | St. Francis abutment | 1400×806 | 1280 | 960×553 | [Commons category](https://commons.wikimedia.org/wiki/Category:St._Francis_Dam) |
| 166:3 | Twisted Tracks | 1400×1017 | 1280 | 960×697 | same Commons category |
| 166:4 | St. Francis Dam after the 1928 failure | 1400×1043 | 1280 | 960×715 | same Commons category |
| 166:5 | Standing section | 1250×936 | 1280 | 960×719 | same Commons category |
| 166:6 | Man pointing at crack in Saint Francis Dam | 4431×5760 | 1280 | 960×1248 | same Commons category |

**Important correction to blindly limiting URLs to 960:** The actual Commons original for *Archimedes Palimpsest.jpg* is only 665px wide. Requesting 1280px in the source URL does not make the original 1280px. Any proposed 960px derivative would enlarge pixels and violate the no-upscale rule. The file description labels the original as **U.S. public domain**, but this is not a blanket approval to cache or republish it. Verify the item, terms, attribution and visual match before any action.

Six-row audit: `qa/media-recovery/commons_six_native_geometry_20261106.json`. Offline geometry and rights validation: `validate_commons_six_geometry_20261106.cjs`, `test_commons_six_geometry_20261106.cjs`.

## Why copyright and replacement controls remain closed

Wikimedia Commons hosts different kinds of public-domain and openly licensed work; Commons is **not** the copyright holder for most files. Its official [reuse guidance](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia) requires checking the license **of the particular file** (attribution, exact license text/URL, creator, share-alike conditions, modifications and other applicable rights). A WordPress caption saying 'public domain' or 'CC BY' is only an editorial hint, not verified legal provenance. A derived `File:` link is only a **lookup candidate**; its existence, binary identity and licensing are not assumed.

**No automatic redirect-to-upload conversion.** For each visitor-confirmed failure: verify the original item's publisher/Commons record and exact visual subject, compare source/thumbnail crops and decoded dimensions, verify copyright and required credit, then consider an *authorized*, isolated **WordPress staging** media derivative with a maximum width of `min(native_width, 960)`, preserved aspect ratio, responsive `srcset/sizes`, dimensions to limit CLS, descriptive alt text and full-resolution access when important (e.g. historical maps). Test mobile/desktop and logged-out cold wire. Submit a **small reviewed change**; never rewrite Gutenberg post blocks en masse.

## Verification gates and high-priority failures

Use Site QA #154's already existing **guest-browser collector**, not another. Request for the six P0 images: exact page, DOM image slot, final URL after redirects, image response and content type, decoded `naturalWidth/naturalHeight`, failed decode vs 403/404 vs CORS/wrapper artifacts, screenshot showing intended subject, and actual uncached transferred bytes. Prioritize Three Mile Island, Sunshine Skyway, Scotch Cap and Hebgen Lake before the Commons optimization opportunity. A broken source confirmed by a web retriever alone is **not** a visitor-confirmed failure.

The reported **42 broken third-party images** have **not** been confirmed in visitor browsers. The proposed **76% cold-wire image reduction** is still **unmeasured**; any site-wide assertion must cover the exact current published cohort, using the already committed verifier and actual before/after browser measurements. The previous count was 61 posts / 355 inline image refs; current WordPress census is 66 / 361, including 294 external-origin refs. There remain 13 first-party originals over 1.5MiB totaling **43,522,829 stored bytes**; disk size is not measured visitor bandwidth.

`docs/IMAGE-WEIGHT-WORKLIST.md` was unavailable on examined branches, so this source evidence is not represented as a reading of that missing document. Copyright releases, native geometry for other Commons files and browser status are **NULL / HOLD** until independently verified.

## Isolated release position

- WordPress production writes: **0**; production image replacements: **0**.
- Downloaded / mirrored / cached external images: **0**.
- Guest-browser failure claims: **0 confirmed**; actual transfer savings: **unmeasured**.
- Subscription spend, homepage visual-design changes and Site QA collector duplication: **0**.
- Tests: validator exercised against the four actual GitHub-readable inventory shards with **17/17 V8 release/mutation scenarios passing**; six-row geometry gate exercised with **13/13 scenarios passing**. Native Node CI and actual browser checks remain outstanding until separately executed.

Keep PR #1228 as a **draft**; do not merge blindly given its accumulated file breadth. Prefer review of isolated validator/shard files and a future small approved production patch per restored image.
