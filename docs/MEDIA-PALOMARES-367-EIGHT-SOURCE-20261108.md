# Palomares image provenance / conditional recovery — Nov 8, 2026

Read-only WordPress `posts_get(context=edit)` confirmed **post 367** remains published, modified **2026-10-29T17:34:27**, with **nine identical stored image URLs** compared with pinned October 30 archival blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`. One image is first-party; eight are externally referenced. No WordPress writes.

## Live sources and retrieval evidence

Seven Commons `Special:Redirect/file` stored links returned **URL_NOT_ACCESSIBLE_VIA_TOOL** on `web.open`; the Naval Undersea Museum image `https://navalunderseamuseum.org/wp-content/uploads/2016/03/CURV-I-H-Bomb-Recovery-300x243.jpg` rendered as an image. These are **web tool outcomes**, not HTTP codes, uncached browser requests, or measured transfers. The former cannot be counted as seven visitor-broken images. Exact eight URLs and all NULL guest fields reside in the JSON ledger.

## Primary/catalog crosswalk and historical image integrity

- **367:1 Chrome Dome map** — Commons file (1475×923; conditional 960×601) is an authored **CC BY-SA 2.5** map, **not** a blanket federal public-domain photograph. Rehosting or modified derivatives require attribution, license link, and share-alike compliance. Map labels need mobile readability testing. https://commons.wikimedia.org/wiki/File:Operation_Chrome_Dome_route.jpg
- **367:2 USS Skill** — Commons catalog traces a Navy 428-NPC-36556 image to NARA **NAID 85011** (1227×898; conditional 960×703). Confirm actual accession and federal-work rights for exact still before reuse. https://commons.wikimedia.org/wiki/File:USS_Skill_(MSO-471)_operating_off_the_coast_of_Spain,_in_February_1966_(428-NPC-36556).jpg
- **367:3 Alvin launch** — Dutch Nationaal Archief **Anefo 918-8161**, dated 21 February 1966, catalog states **CC0** (3440×2453; conditional 960×685), photographer unknown. Provide National Archives/Anefo credit even when optional. https://commons.wikimedia.org/wiki/File:Zoeken_naar_H_bom_in_Spanje,_de_Alvin_wordt_te_water_gelaten,_Bestanddeelnr_918-8161.jpg
- **367:4 CURV I / Petrel** — primary U.S. Naval Undersea Museum story documents the scene and displays a 300×243 rendition. **No permission to rehost or true native dimension established.** https://navalunderseamuseum.org/petrel-helmet/
- **367:5 Carl Brashear** — 428-GX-USN-118930 (1854×2464; conditional 960×1276); *photographed April 22, 1971*, while digital reproduction metadata is from 2016. Never present it as a February/April 1966 photo. https://commons.wikimedia.org/wiki/File:428-GX-_USN_118930_(26941557635).jpg
- **367:6 Petrel recovery crew** — 662×374 (stay native; do not upscale). Commons notes a later *lossless crop* of the earlier 666×374 copy and a Navy public-domain claim. Exact crop identity remains to be checked. https://commons.wikimedia.org/wiki/File:1966_Palomares_B-52_crash_-_recovered_H-bomb.jpg
- **367:7 contaminated-soil barrels** — 500×252 (stay native). Commons claims USAF public domain; original reference was an older Brookings project page, so check provenance/credits. https://commons.wikimedia.org/wiki/File:Palomares_barrels.jpg
- **367:8 Mk 28RI recovered bomb** — 617×461 (stay native), Navy public-domain claim with historically moved NAVAIR link; verify exact image and credit. https://commons.wikimedia.org/wiki/File:Recovered_Mk_28RI_bomb.JPG

**Practical consequence:** Three of eight stored external refs request Commons width=1280 even though their originals are **500–662px wide**, so replacing the query with width=960 does not create new detail and must not upscale. Four other Commons originals can be *conditionally* served at 960px, but size savings and visual equivalence are unmeasured. The eighth museum photo has no verified native dimensions. No image was downloaded.

## Handoff and release gates

Site QA **#154** owns the existing CDP guest image collector. After the six preexisting P0 image slots, check post 367 desktop/mobile with `currentSrc`, redirects, final MIME, status, cache flags, decoded `naturalWidth/Height`, network transfer size, and screenshot. Distinguish image failures from web-tool redirect limitations.

Before any WordPress-media localization: check individual catalog rights and photo/crop identity, image pixel dimensions, attribution and 960px maximum width without upscaling; stage a versioned derivative, compare visual/caption readability, link a specific approved image to the exact source and preserve rollback URL. Do not touch Gutenberg blocks until a separately approved publication path exists.

Historical inventory: 61 posts/355 stored inline refs (expanded cohort 66/361). Reported 42 broken images **not visitor verified**. Proposed 76% transferred-image reduction **not measured**. Fifteen WP originals >1.5 **decimal MB** = 47,096,779 **stored** bytes only. Zero image downloads/caches, production changes or subscription spend.

**Test:** `node qa/media-recovery/test_palomares_367_eight_source_20261108.cjs`. Draft-only; no deployment.
