# New London School — six-image provenance, rights and no-upscale release gate
**Media Recovery | 2026-11-05 | Source-only / draft / NO PRODUCTION CHANGES**

## Scope and evidence
Article **217**, [The Gas Had No Smell](https://finalvestige.com/2026/08/18/the-gas-had-no-smell/), has six stored `<img src>` URLs in the pinned October 30 WordPress inventory `qa/media-recovery/parts/06.json` (Git blob `0f3dfe398a76838049cebba7cb773d5c5a0c8c69`, saved post modified `2026-10-29T16:04:52`). This is *not* a fresh full-site census or visitor-browser measurement. [Machine audit](../qa/media-recovery/new_london_217_six_catalog_20261105.json) retains all exact published `src` and `alt` text, individually checked Wikimedia Commons file titles/catalog dimensions, claim-specific rights, and only conditional derivative dimensions. All six `browser_http_status`, `source_http_status`, `visitor_natural_width_px`, actual transferred bytes and verified-broken fields remain **NULL**.

| Slot | Commons master | Conditional staging only (no upscale) | Source / rights note |
|---|---:|---:|---|
| 217:0 — explosion aftermath | 760×609 | **760×609** | AP/unknown author; Commons US nonrenewal public-domain claim requires item review |
| 217:1 — school before disaster | 960×685 | **960×685** | Unknown photographer; image uploaded June 2026, vintage origin and nonrenewal assertion require check |
| 217:2 — INP newspaper scan | 2861×2244 | **960×753** | INP, San Antonio Light, published March 19; Commons PD-scan/nonrenewal designation |
| 217:3 — INP crop 1 | 2457×1950 | **960×762** | Extracted from the same 217:2 parent newspaper scan; not separate custody |
| 217:4 — INP crop 2 | 2457×1862 | **960×728** | Another extraction from 217:2; not separate custody |
| 217:5 — 2016 memorial | 3840×2160 | **960×540** | QuesterMark, **CC BY-SA 2.0**: credit, link to license, changes notice, and share-alike rules |

The six stored Commons `Special:Redirect/file?width=1280` URLs **request 1280px**. Two masters are smaller than that: 217:0 is 760px wide and 217:1 is 960px wide. This indicates a **source-request-vs-catalog-size discrepancy**, *not proof* that a visitor receives an enlarged or incorrectly displayed image. Do not upscale either.

## Specific historical-integrity finding
[Commons page for 217:0](https://commons.wikimedia.org/wiki/File:New_London_School_explosion.jpg) describes an aftermath scene but lists **March 17, 1937** as image date, one day **before** the March 18 school explosion. Treat this as inconsistent catalog metadata. The article's March 18 chronology should not be changed to match it. Also, **217:2, 217:3 and 217:4 are one photographic document with two crops**, and the memorial image 217:5 is modern (July 5, 2016), not a 1937 exposure.

## Primary-source fallback candidates — RESEARCH ONLY
- [Texas State Library / Archives: New London exhibit](https://www.tsl.texas.gov/exhibits/railroad/other/newlondon.html): contemporaneous **nighttime rescue** photograph, subject-level alternative only; exact photographer/reuse rights and original binary dimensions UNKNOWN. No local copy.
- [UT Arlington Libraries, Star-Telegram catalog 10013106](https://mavmatrix.uta.edu/specialcollections_startelegram1930s/2593/): March 20 overview, subject-level alternative only. **CC BY-NC 4.0, archive rights reserved**: the archive expressly restricts use; **do not import commercially** or infer permission from public display.
- [Austin History Center / UNT, Neal Douglass negative ND-37-103-02](https://texashistory.unt.edu/ark:/67531/metapth19251/): March 1937 removal of debris, subject-level alternative only; image publication rights unresolved.

A primary archive's publication of a picture does not create a general commercial rehosting grant. Commons catalog licensing assertions are evidence for review, **not independently verified permission** to copy or adapt all six. The modern CC BY-SA image is an especially distinct obligation.

## Controlled WordPress and performance staging plan — NOT AUTHORIZED TO EXECUTE
1. **First capture actual failures:** Site QA #154 owns the existing P0 six-slot logged-out Chrome queue (285:5, 285:2, 287:5, 418:1, 418:2, 407:1). Post 217 remains P2, does **not** compete with or duplicate that collector. Save per-slot page URL, `currentSrc`, decoded natural size, image request IDs, actual GET/response, error, encoded transferred bytes, cache provenance, viewport and source HTML.
2. **Rights and identity gate:** resolve exact photographer/credit/license, capture date, crop/scene parity, permitted derivative/redistribution terms for *each specific item*. Do not use the NC UTA candidate for revenue-generating FV without express additional rights.
3. **If a visitor-facing problem is confirmed and reuse is authorized:** preserve source link/caption/ALT chronology; download *only the approved item* to a review-only staging location; hash source and derivative; output no wider than 960px and never upscale; reserve intrinsic dimensions or an aspect-ratio container to avoid layout shifts; compare actual image pixels and color/crop before/after.
4. **Proposed future CMS release, NOT approved here:** use a new WordPress Media Library attachment rather than silently hotlinking another mutable source; preserve attribution/license in media metadata, page visible captions where required, and original source URL in restoration ledger; make **one** reversible media-reference change under separate production approval. Keep exact original Gutenberg block revision + source URL for rollback; do not bulk-rewrite article HTML.
5. **Only claim performance savings** after a *paired, fully decoded, uncached guest-Chrome image-wire measurement* on same pages, slots, viewport, and network conditions. Original master file size, server HEAD, Commons nominal width and WordPress stored bytes do **not** equal browser-transferred bytes. The existing **76%** reduction claim remains unmeasured.

## Verification and scope
- [Validator](../qa/media-recovery/validate_new_london_217_20261105.cjs) checks exact six frozen source identities/ALTs, Commons catalog dimensions, 960px geometries, mandatory rights and chronology HOLDs, false HTTP/bytes claims, archive NC restrictions, and prohibition of copies/publication.
- [Tests](../qa/media-recovery/test_new_london_217_20261105.cjs): **38/38 exact-source V8 Node-compatible assertions passed**, comprising one valid audit plus 37 deliberate invalid mutations. Native Node CI and logged-out Chromium remain pending.
- Pinned file blobs at verification: validator `bf2149d18df299dbb3f5d4e3870e7cb77396f556`; JSON `6534c51c72fb37d0baf35c3b0e5ab43b24caf2d7`; tests `a0788ed6dbbd007864130b39e513c22a1c319103`.
- Established overall baseline only: **61 articles / 355 slots / 288 external-origin refs**, **13 WP originals above 1.5 MiB totaling 43,522,829 *stored* bytes**, **42 reported broken but visitor-unverified**, **76% transfer reduction unmeasured**, **0 production repairs**.
- **Nothing** was downloaded, locally cached, resized, uploaded, rehosted, rewritten, or published. Zero spending; homepage/interim lead and Site QA source files untouched.
