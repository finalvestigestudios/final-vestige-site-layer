# Media Recovery: Honda Point post 288 — source integrity and restoration hold (2026-11-07 PT)

Isolated addendum on existing Draft PR #1402, *not* Site QA #154 nor homepage design. Exact six stored source URLs/ALT descriptions taken from pinned 2026-10-30 Git inventory `qa/media-recovery/parts/03.json` blob `49183f66f880f7c4dfd363acca906876877f2e5e`. This is NOT a fresh production WordPress read.

## High-value verified lineage

- **288:1** published secondary-host JPEG visibly carries Navy archival identifier **NH 69059**; primary NHHC identifies *Delphy* and *Nicholas*, high-resolution scan 6250×4904; geometry 960×753. https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69059.html
- **288:3** published NavSource JPEG visibly carries **NH 84820** (photographer Aston), *Nicholas* and *S.P. Lee*; primary high-resolution scan 6146×5130; geometry 960×801. https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-84000/NH-84820.html
- **288:4** published ibiblio image visibly carries **NH 84822** (Aston), with *Chauncey*, *Young*, *Woodbury* and *Fuller*. Navy primary does **not** substantiate the stored ALT's phrase “during rescue operations”; visual editorial review flagged, not rewritten. Original 6158×4992; geometry 960×778. https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-84000/NH-84822.html
- **288:0** published Navy URL embeds **NH 69586**, an actual Navy aerial photo. Navy catalog scan 6256×4862; geometry 960×746. https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69586.html
- **288:2** Navy radio-station photograph: exact catalog identification/native pixels unresolved. It is illustrative historical equipment, **not** proof of the actual direction finder aboard *Delphy*.
- **288:5** USNI image on publisher page shows ships from an elevated shore-facing viewpoint; current ALT's “aerial historical view” lacks publisher support. USNI credits its Photo Archive; independent rights clearance required. https://www.usni.org/magazines/proceedings/2020/march/chaos-devils-jaw-0

## Retrieval facts / limitations

Web image tool rendered exact published URLs **288:1, 288:3, 288:4, 288:5**. For **288:0 and 288:2**, the tool returned 400 *retrieval-wrapper timeouts*; **NOT** actual publisher HTTP statuses or visitor-browser broken images. Genuine origin HTTP codes, guest desktop/mobile `currentSrc`, `naturalWidth`, decode, waterfall bytes, CLS and transfer savings remain **NULL**.

## Rights, performance and permitted recovery sequence

NHHC [explicitly says](https://www.history.navy.mil/our-collections/photography.html) copyright varies by individual photograph and researchers must obtain clearances; [its Archives guidance](https://www.history.navy.mil/about-us/services-and-policies/scan-copyright.html) distinguishes official US-government works from separately copyrighted donated/commercial materials. USNI archive is independent. No licenses assumed and no image downloads, local caching, WordPress uploads/rewrites, homepage changes, billing or deployment.

Site QA retains the single guest browser collector and first-priority P0 queue **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. After P0, capture all 288 image request IDs, statuses, MIME, decoded dimensions, bytes, and full-scroll screenshots via the existing collector. For proven broken media only, confirm same photographed scene/crop, attribution and rights; stage ≤960px non-upscaled derivatives from authorized sources with retained archive links, compare visual parity, and request production/editorial approval with rollback.

Historic **42 allegedly broken** remain unverified; **76% reduction** unmeasured. The 14 oversized originals occupy **45,553,777 stored bytes**, not confirmed browser transfer. No live repairs occurred.

## Tests

`node qa/media-recovery/validate_honda_point_288_20261107.cjs` and `node --test qa/media-recovery/test_honda_point_288_20261107.cjs` — 17 expected tests including 16 negative safety mutations. GitHub runner may not execute native CI; V8 validator/mutation checks run before commit.
