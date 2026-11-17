# Sunshine Skyway 287:5 — primary archive recovery and conditional caching (2026-11-02)

**Scope:** Source-only Media Recovery PR #183, independent of homepage design and Site QA #154. The stored article [Sunshine Skyway](https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/) has image slot 287:5 with source https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg and ALT: “The old Sunshine Skyway wreckage and the later bridge replacement in Tampa Bay.”

The independently recorded original source result is a **web-retriever wrapper 404** on November 2, **NOT verified origin/guest Chrome HTTP 404**. Publisher's relocated image credits University Press of Florida, with reuse/caching rights not established. The relocated publisher image depicts 1980 collision aftermath; the stored ALT describes a later replacement bridge, so its historical identity must not be silently retained with a different scene.

## Newly verified original-primary-source archival choices

**USF Libraries, Gandy commercial and aerial collection — explicit item CC BY 3.0:**

1. [Gandy 21_1014 / item 4785](https://digitalcommons.usf.edu/gandy/4785/): George Skip Gandy IV; **January 28, 1982**; a collapsed-span section alongside the still-standing original span. The catalog directly links [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) and supplies title, author, date, collection and recommended citation. This is the **preferred contextual alternate**, not the same picture as the published original, and does not depict the replacement bridge.
2. [Gandy 21_0970 / item 4742](https://digitalcommons.usf.edu/gandy/4742/): same photographer and date; a close view of a damaged concrete pier, also expressly cataloged **CC BY 3.0**. More narrowly focused than the wide image. Not an exact-image replacement.

The CC BY 3.0 license permits redistribution and adaptations, including commercial use, conditional on appropriate creator/title/source credit, license link and identification of changes; other rights may remain. USF item-level licensing should still be rechecked before selecting and resizing a binary. Directly linking a multi-megabyte archival master is not an approved performance optimization.

**State Archives of Florida / Florida Memory — disaster-day scene, rights unresolved:**

3. [RC09236 / item 32082](https://floridamemory.com/items/show/32082): **May 9, 1980**, black-and-white 7×5-inch photoprint, catalog text describes a car stopped just short of the breached span. The catalog path identifies /fpc/reference/rc09236.jpg.
4. [RC09237 / item 32083](https://www.floridamemory.com/items/show/32083): same date, 8×10-inch photoprint, similarly describes a car near the breach; catalog path /fpc/reference/rc09237.jpg. Do not assume the two image binaries are identical.

For both Florida Memory records, an affirmative republication license was **not** found: hold reproduction, downloading and hosting pending item-specific rights review. These complement rather than duplicate the earlier H. Milo Stewart / Florida Memory K894127 c.1987 old-and-new-bridges alternate, whose rights remain unresolved.

## Strict staging and verification gates

1. Site QA #154 continues its **existing** logged-out desktop/mobile Chrome workflow, capturing actual rendered currentSrc, CDP Image request ID, redirects, HTTP/MIME, network bytes, naturalWidth/naturalHeight and screenshot for 287:5. The 42-image broken count remains unverified.
2. An editor decides between exact-image restoration (publisher rights review required) and a **different historical photo**. The two 1982 USF photos precede the 1987 replacement bridge, so they require a truthful 1982 ALT/caption rather than the stored new-bridge ALT.
3. If USF CC BY 3.0 approved, retain a linked item source, George Skip Gandy IV, catalog title, 1982 date, license URL and crop/resize change note. If Florida Memory chosen, obtain a sufficiently documented item-level usage grant first.
4. On authorized file inspection, confirm intrinsic pixel geometry; optimize to **width at most min(960, intrinsic width)** and proportional height, no enlargement. Catalog does **not** establish numeric master/preview dimensions here, so target height stays **null**. Evaluate image integrity, responsive srcset, accessibility, EXIF, compression and cold-cache page-wire bytes in approved staging.
5. WordPress Media Library upload, block replacement, CDN caching or caption change require a **separate human-approved production step and rollback**. This PR does none. Never call a broken image's zero transferred bytes a performance saving; complete paired cold-cache CDP evidence is required for any 76% claim.

## Auditable deliverables

- Machine-readable 4-candidate record and original retriever status: qa/media-recovery/skyway_usf_florida_primary_recovery_20261102.json
- Fail-closed offline evidence validator: qa/media-recovery/validate_skyway_usf_florida_primary_20261102.cjs
- Native Node regression: qa/media-recovery/test_skyway_usf_florida_primary_20261102.cjs
- Native local Node.js 22.16.0 check: **30/30 PASS**, plus validator syntax check. Full catalogue binary downloads, real Chrome and production modifications were **not** performed.

Baseline **61 posts / 355 stored image references / 286–288 offsite depending on source snapshot / 13 WordPress originals >1.5 MiB**. Reported 42 broken are not guest-verified, 76% image transfer saving is unmeasured, **0 production image repairs**. No image binaries downloaded or scraped, subscription spend, homepage redesign or Site QA PR #154 code changes.
