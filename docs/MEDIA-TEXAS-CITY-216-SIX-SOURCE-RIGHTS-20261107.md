# Texas City 216 — exact image custody, rights and no-upscale (2026-11-07)

**Draft-only, no CMS/browser changes.** This batch owns media integrity, not homepage design. Authenticated WordPress `posts_get` read on 2026-11-07: published post **216**, modified **2026-11-02T21:39:36**, six images. All six exact stored sources match frozen 2026-10-30 article image inventory; all six lack explicit HTML width/height. This is a source-level CLS exposure, **not a measured CLS regression**. Image URLs are `commons.wikimedia.org/wiki/Special:Redirect/file/...`; web.open could not access all six redirect endpoints. **No actual origin HTTP response, browser failure, image decode or transfer bytes established.** The six catalog file pages were separately inspected and dimensions recorded.

| Slot | Archival master catalog | Conditional no-upscale preview | Editorial / rights hold |
|---|---|---|---|
| 216:0 | UH Collection / Commons 3111×2421 | **960×747** | UH archive copyright/reproduction verification; original source asks width=1280, not measured as a 1280 network request. |
| 216:1 | Jim Evans / Commons 1917×1544 | **960×773** | Photograph created **2008**, correctly a memorial not contemporaneous 1947. CC BY-SA 4.0 attribution and adaptation/share-alike requirements must persist. Published caption already credits author/license. |
| 216:2 | UH Collection / Commons 2765×2112 | **960×733** | 1947 damaged building, Commons PD claim vs UH reproduction guidance needs reconciliation. Original URL lacks explicit width query. |
| 216:3 | NARA **NAID 68149862**, Army Air Forces 18-AA-121-56, 6923×5485 | **960×761** | NARA catalog describes date broadly **1917–1964**, not proven '1940s' as present ALT says. Do not date or claim immediate disaster context until primary record/scan checked. Original source requests width=1280; **16.62MB master file size is not transferred page size**. |
| 216:4 | UH Collection / Commons 2768×2120 | **960×735** | Commons narrative conflicts between **SS Wilson B. Keene** and **High Flyer OR Wilson B. Keene**. Maintain published neutral 'ship wreckage' caption until authoritative photo identity verified; do not invent a vessel. |
| 216:5 | David Provines / Commons 480×320 | **480×320 — no 960px upscale** | Modern anchor photograph, uploader public-domain claim, item-level reuse review. |

### Primary provenance and rights

- Commons records for exact six filenames: https://commons.wikimedia.org/wiki/File:Txcitydisasterparkinglot.jpg ; https://commons.wikimedia.org/wiki/File:Texas_City_Disaster_Firemen_Memorial.jpg ; https://commons.wikimedia.org/wiki/File:Txcitydisaster5storybuilding.jpg ; https://commons.wikimedia.org/wiki/File:Texas_-_Texas_City_-_NARA_-_68149862.jpg ; https://commons.wikimedia.org/wiki/File:Txcitydisasterboat.jpg ; https://commons.wikimedia.org/wiki/File:Grandcampanchor.jpg .
- Texas City Disaster Photographs, UH Special Collections: https://digitalcollections.lib.uh.edu/collections/0p0967712 ; https://findingaids.lib.uh.edu/repositories/2/resources/3 . **UH states possession of originals does not establish ownership of copyright; reproduction decisions are case-specific.** Therefore do not equate Commons uploader-side PD tagging with permission to bulk mirror all archival material.
- NARA item: https://catalog.archives.gov/id/68149862 ; municipal contextual records: https://texascitytx.gov/458/1947-Texas-City-Disaster ; original Jim Evans license: https://creativecommons.org/licenses/by-sa/4.0/ .
- Additional archives **not exact replacements**: Texas State Library L.L. Cook collection items 2016/179-1 and 2016/179-2 (https://www.tsl.texas.gov/lobbyexhibits/extraextra/texascitydisaster); Moore Memorial Public Library aerial and rescue records (https://texashistory.unt.edu/ark:/67531/metapth11736/ and https://texashistory.unt.edu/ark:/67531/metapth11791/). Require photo-level match and reuse permission before using any as substitute.

### Restoration / WordPress Media staging plan (NOT executed)

1. Existing Site QA #154 keeps its **six P0 guest-browser image slots** first: 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. Then full-scroll post **216** (360px mobile and 1440px desktop), capture guest `currentSrc`, request+redirect chain, HTTP, MIME, decode/naturalWidth, image encoded bytes, screenshots, LCP/CLS. Only declare broken for directly corroborated failed images.
2. Check Commons exact original vs candidate binary identity, photographer/agency, crop, chronology, captions, permitted modification, use rights, original SHA-256, safe max 960px width **without upscaling** and without destroying photograph framing. For 216:5 stop at 480×320; never auto-crop historic assets. For 216:1 retain Jim Evans attribution and CC BY-SA.
3. **Only after license clearance and explicit editorial/site-release authorization**, propose a cached original/WordPress Media candidate, preserving metadata and credits; stage a Gutenberg block-level surgical change in nonproduction environment, visually compare before/after and prepare rollback. No live post writes or asset caching in this PR.
4. Performance: measure identical post, browser/device/network/viewport, full-scroll and true cold-cache image-only CDP transfer before and after. `(baseline image bytes - candidate image bytes)/baseline image bytes` applies to **same-cohort network bytes**, not WordPress Media Library originals. The **76% claim remains unmeasured**, the reported **42 broken images remain guest-unverified**, and **13 >1.5MiB WordPress originals total 43,522,829 storage bytes** only. Frozen **61/355** inventory differs from later **66/361** inventory; do not mix denominators.

### Isolation and QA

Machine ledger `qa/media-recovery/texas_city_216_six_archive_20261107.json`, standalone fail-closed validator and native Node tests; no duplicate Site QA collector, WordPress writes, copyrighted downloads, spend, homepage work or automation edits.
