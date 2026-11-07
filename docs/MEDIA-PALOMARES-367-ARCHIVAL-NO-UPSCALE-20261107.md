# Palomares 367 — nine-source archival custody, no-upscale and image-integrity gate
**2026-11-07 | isolated media recovery QA | nonproduction draft**

## Source evidence and scope
Authenticated **read-only** WordPress editor-content retrieval of published article [They Found the Bomb Twice](https://finalvestige.com/2026/08/19/they-found-the-bomb-twice-palomares/) (post **367**, modified **2026-10-29T17:34:27**) established **nine** exact image `src` attributes plus their existing ALT and captions. Eight source references are third-party: **seven** Wikimedia Commons `Special:Redirect/file` URLs requesting `?width=1280`, and **one** U.S. Naval Undersea Museum image. One image is first-party and declared 425×329. **Eight of nine** stored image tags have no explicit numeric HTML width/height, and **none** has a stored `srcset`. Front-end rewriting is not accounted for; do not assert visible CLS, broken images, 1280px actual transfers or visitor experience from stored markup.

The historical 2026-10-30 snapshot covers 61 posts/355 inline sources/288 external references; a separate November 5 source census covers 66/361/294. Neither census is a visitor-browser failure count. The report of 42 broken images remains **unverified**; proposed 76% reduction in actual image-transfer weight remains **unmeasured**. Thirteen WordPress media originals totaling 43,522,829 **stored bytes** do not measure image download traffic.

## Per-image primary-source mapping and conditional 960px geometry
These are catalog-pixel calculations, NOT resized/downloaded assets and NOT proof that exact published binaries/crops match catalog renditions. Proposed width is `min(original_width,960)` with aspect ratio preserved; nonbinary museum page has no proposed preview size.

| Image slot | Catalog / provenance | Catalog native px | **Conditional** <=960px no-upscale | Rights / chronology gate |
| --- | --- | ---: | ---: | --- |
| 367:0 | [Recovered weapon, US Navy](https://commons.wikimedia.org/wiki/File:Palomares_H-Bomb_Incident.jpg), first-party rendition | 425×329 | **425×329** | Commons government-work indicator; first-party derivative binary identity unverified |
| 367:1 | [Operation Chrome Dome route](https://commons.wikimedia.org/wiki/File:Operation_Chrome_Dome_route.jpg) | 1475×923 | **960×601** | CC BY-SA 2.5; original creator/uploader Emt147, linked license/credit review; preserve legible map labels |
| 367:2 | [USS Skill](https://commons.wikimedia.org/wiki/File:USS_Skill_(MSO-471)_operating_off_the_coast_of_Spain,_in_February_1966_(428-NPC-36556).jpg) | 1227×898 | **960×703** | Navy 428-NPC-36556 / NARA 85011; item attribution and exact rendition |
| 367:3 | [Alvin lowered, February 21 1966](https://commons.wikimedia.org/wiki/File:Zoeken_naar_H_bom_in_Spanje,_de_Alvin_wordt_te_water_gelaten,_Bestanddeelnr_918-8161.jpg) | 3440×2453 | **960×685** | Netherlands National Archives/Anefo 918-8161; Commons CC0, preserve archive credit |
| 367:4 | [Naval Undersea Museum CURV I](https://navalunderseamuseum.org/petrel-helmet/) | **Unknown** | **HOLD** | Museum official subject/custodian; no assumed permission to download, cache or rehost |
| 367:5 | [Carl Brashear, official Navy 428-GX-USN 118930](https://commons.wikimedia.org/wiki/File:428-GX-_USN_118930_(26941557635).jpg) | 1854×2464 | **960×1276** | PHC A.J. Walker, **April 22, 1971**; do NOT portray as a 1966 scene |
| 367:6 | [Recovered weapon with crew/CURV](https://commons.wikimedia.org/wiki/File:1966_Palomares_B-52_crash_-_recovered_H-bomb.jpg) | 662×374 | **662×374** | Navy PD tag; distinct view from close-up and first-party photograph |
| 367:7 | [Palomares barrels](https://commons.wikimedia.org/wiki/File:Palomares_barrels.jpg) | 500×252 | **500×252** | USAF PD tag via a secondary Brookings source; original custody still merits review |
| 367:8 | [Recovered Mk 28RI close-up](https://commons.wikimedia.org/wiki/File:Recovered_Mk_28RI_bomb.JPG) | 617×461 | **617×461** | Navy PD tag via legacy NAWCWPNS original; closeup is not interchangeably the crew image |

**Concrete no-upscale risk:** `367:2`, `367:6`, `367:7`, `367:8` request Wikimedia `width=1280` although respective catalog masters are only **1227**, **662**, **500**, **617** pixels wide. Commons may cap a request at the native image; **no actual browser upscaling has been observed**. Replacements must never enlarge these or alter historically significant crops. One map is CC BY-SA and cannot be silently treated like a US Navy government photograph.

Every row's **actual guest HTTP status, currentSrc, decoded dimensions, transferred bytes and verified broken status is NULL**. All carry `rights_review:HOLD`, `binary_match_verified:false`, `rehost_authorized:false`. The existence of a catalogue record is neither a digital binary match nor universal rehosting authorization.

## Safe verification and conditional remediation
**Priority unchanged:** Site QA PR [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns the guest browser collector and P0 slots **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. This Palomares batch is **P1**; do not displace those six. Have Site QA's existing collector capture both desktop and mobile after complete scrolling: logged-out `currentSrc`, Chrome CDP request/response IDs, actual HTTP/redirect/MIME/encodedDataLength, `naturalWidth/naturalHeight`, cold-cache flags and screenshots. Confirm visible image and source scene, not just the image URL's response.

If a specific visitor failure is confirmed, independently verify exact image identity/hash, item-level license/attribution and allowed redistribution before producing one *offline* <=960px preview. Compare relevant details, period labels, chronological captions, map legibility and image crop at multiple widths; preserve the original ALT/caption/source link. Any WordPress Media Library upload and exact image-block replacement requires a separate review, controlled staging screenshot test, rollback URL/content record and later explicit publishing authorization. Measure cold-browser before/after transfers under identical conditions; never substitute WordPress Media Library original bytes for wire bytes or claim 76% site-wide improvement on a sample.

## Artifacts and checks
- `qa/media-recovery/palomares_367_nine_catalog_20261107.json` — exact WordPress URLs and ALT/captions, archival candidates, catalog native geometry, cautious 960px proposals and explicit **NULL** browser evidence.
- `qa/media-recovery/validate_palomares_367_20261107.cjs` — deterministic fail-closed source/geometry/rights validator; no network operations.
- `qa/media-recovery/test_palomares_367_20261107.cjs` — baseline plus **25 deliberately unsafe mutations**, with native Node runner below:

```sh
node qa/media-recovery/validate_palomares_367_20261107.cjs
node qa/media-recovery/test_palomares_367_20261107.cjs
```

The uncommitted validator logic and 25 mutations passed **26/26 assertions in a Node-compatible V8 replay** before commit; full native Node checkout/CI and logged-out Chromium are **not executed**. Readback after commit must be verified separately.

**Safety statement:** zero WordPress production writes, zero binary downloads/mirroring/caching, zero changes to homepage design or Site QA collector, zero subscriptions/spend, zero live image repairs. No post-block rewrites.
