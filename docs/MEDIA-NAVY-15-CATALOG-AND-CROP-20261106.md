# Navy-hosted media: 15 live source slots, official catalogue crosswalk, crop and provenance gates (2026-11-06 Pacific)

**Owner:** FV Media Recovery Engineering (not homepage design). **Scope:** read-only live WordPress sources, official U.S. Navy/NHHC archival catalog records, isolated draft QA. No production changes.

## Verified, pinned current content

Fresh `posts.get(context=edit)` for [post 274](https://finalvestige.com/2026/08/19/twenty-four-feet-from-air-uss-tang/), [280](https://finalvestige.com/2026/08/19/the-sledgehammers-broke-first-uss-pueblo/), [288](https://finalvestige.com/2026/08/19/the-bearing-was-right-honda-point/), [370](https://finalvestige.com/2026/08/19/the-lines-were-in-the-fire-west-loch/) gives **15 literal Navy-domain `img src` occurrences** (3 + 6 + 2 + 4) in 27 total stored images. Every Navy record includes exact current article/image URL, Gutenberg slot index, ALT, publisher catalog link when matched, attribution, rights HOLD, conditional geometry, and **null visitor HTTP/decoded pixels/wire bytes**. The original image host is `www.history.navy.mil`. This does **not** establish even one visitor-visible failure.

- [15-row JSON audit](../qa/media-recovery/navy_fifteen_primary_catalog_20261106.json)
- [Fail-closed offline validator](../qa/media-recovery/validate_navy_fifteen_20261106.cjs)
- [32-case regression suite](../qa/media-recovery/test_navy_fifteen_20261106.cjs)

Ten of the 15 original URLs have corresponding **individually identified publisher accession catalog pages**. The five without a discrete image-ID match are **274:1, 274:2, 280:1, 280:4, and 288:2**. These should **not** be replaced on the strength of Navy domain origin alone. Source URL/subject/credit and a catalogue match still do not prove the exact same binary or crop.

### The newly discovered visual-integrity blocker: accession 80-G-202485

Published `370:1` is the Navy photograph of troops landing from LST-353 at Bougainville on **November 6, 1943**, rather than the **May 21, 1944** West Loch disaster. Navy sources for the same photo accession give materially different **high-resolution** dimensions:

- [NHHC numerical archive 80-G-202485](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/80-G-202000/80-G-202485.html): **5860 × 4890** pixels (conditional 960 × 801).
- [Navy Museum 80-G-202485](https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/wwii/wwii-pacific/south-southwestern-pacific/bougainville-campaign/bougainville-land-campaign/80-g-202485.html): **2851 × 2280** pixels (conditional 960 × 768).
- Aspect-ratio discrepancy: **about 4.35%**, larger than the normal 1% visual-parity tolerance. This could represent a different scan/crop rather than a publisher error. **Do not choose a 960px derivative geometry or overwrite the photo until the actual selected rendition is examined.** Catalog labels describing a medium JPEG as `1280 × 1280` may be size-class envelopes; they are not proof of decoded native square imagery.

Seven other specifically cataloged high-resolution masters have **provisional**, no-upscale 960px previews based on their listed master pixels: **274:4 960×1271, 280:0 960×660, 280:3 960×773, 288:0 960×746, 370:0 960×1007, 370:3 960×768, 370:4 960×780**. Those are *candidate dimensions*, **not generated replacement files**, guaranteed current decoded dimensions, or completed source-matching checks.

### Provenance and editorial accuracy

- **288:0 — NH 69586 (Honda Point)**: the publisher credits **Naval Historical Foundation / Admiral William V. Pratt collection**; it is not automatically public domain simply because it is served by a .mil site. Preserve rights **HOLD** until item-level determination. [NHHC item](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69586.html).
- **370:4 — SC 427947**: [Army Signal Corps collection](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/sc-series/SC-400000/SC-427947.html), not proof of Navy photography; the Navy only suggests **probably** USCGC Woodbine and **possibly** LST-480. Preserve uncertainty and credits.
- **274:4 — 80-G-344565**: Richard H. O'Kane photographed in the **1945** POW-release period, not October 1944. [Navy Museum item](https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/wwii/wwii-pacific/japanese-surrender/allied-prisoners-of-war/80-g-344565.html).
- **370:0 — 80-G-276907**: the original ALT merely says “Aerial view of Pearl Harbor.” [NHHC catalogue](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-270000/80-G-276907.html) identifies the **West Loch LST explosions**. Proposed later editorial ALT (not published): “Aerial photograph of tank landing ships burning in Pearl Harbor's West Loch, May 21, 1944.”
- **370:3 — 80-G-276940** shows LST-39 **May 22, 1944**, the day after the incident; retain that timing. [NHHC item](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-270000/80-G-276940.html).

The official [NHHC Photo Archive notice](https://www.history.navy.mil/our-collections/photography.html) says many, *not all*, images are public domain and that individual copyright clearance is the researcher's responsibility. [NHHC archival scanning policy](https://www.history.navy.mil/about-us/services-and-policies/scan-copyright.html) permits official government imagery reproduction while restricting donated/personal copyrighted content. Individual publisher attribution and rights requirements still need review. **No downloading, scraping, rehosting or bulk mirroring has occurred.**

## Safe actionable recovery / WordPress media plan

1. **Site QA #154** retains its existing guest Chromium image-failure collector. Do not duplicate it. First prioritize its six P0 suspects (**285:5, 285:2, 287:5, 418:1, 418:2, 407:1**) and then the Drive podcast artwork **1484:0**. If one of these 15 Navy sources is observed broken, feed its `post_id:image_slot` and exact source URL from this audit to the same collector, capturing `currentSrc`, response code/final URL/content type, Image request ID, `naturalWidth/Height`, screenshot, cache flags and actual `encodedDataLength`.
2. **Confirm identity before changing anything.** Compare publisher catalog accession, historical subject, dates, original crop and credit. For 80-G-202485 compare *both* official high-res catalog representations to the actual selected rendition; keep preview unknown until verified. Never replace specific ships, crew members, or chronology with a generic museum image.
3. **Reuse rights gate.** Record per-item official government-versus-donated provenance; honor credits and third-party restrictions. Only where the reuse basis is affirmatively cleared should an editor plan to download from the official archive. No unlicensed image copying and no paid services.
4. **Staging-only conversion after rights/source clearance.** Derive a JPEG/WebP <=960px wide, never upscale, preserve true decoded aspect and necessary map/text legibility; report actual bytes, hash, MIME, pixels, EXIF/orientation, credit and ALT. For archive diagrams/maps, offer a separately cleared high-detail link rather than destroying detail in a flattened 960px image. Test mobile and desktop visual continuity.
5. **WordPress-controlled upload in a later separately approved change**, keep the original image/caption/credits and a reversible URL mapping; change *only* verified-failing individual media blocks, never rewrite an entire post or proxy merchant affiliate media. Re-check image appearance, responsive selection, licensing and rollback. This draft does not authorize production media writes.
6. **Performance methodology:** `76%` is unmeasured. Use #183's already-existing `compare_cold_image_wire_v1.cjs` and #154's browser evidence on a **matched, fully scrolled, logged-out, uncached** article/page cohort with unchanged viewport/network settings. Sum delivered image `encodedDataLength` (deduplicate repeat Image requests), verify visual parity, distinguish **61 historical posts** from **66 current published posts and 83 published pages**, and do not mistake listed Navy JPEG/TIFF catalogue sizes or WP Media Library storage sizes for visitor transfer. A catalogue `1280px` medium JPEG may already be a small optimized rendition; no invented 76% gain.

## Verification and boundaries

The validator and 32-case mutation suite use **real GitHub-committed audit source**; a separate independent readback can confirm exact Git blob hashes. No native Node CI or actual guest Chrome was executed for this batch. **42 reportedly broken image count remains not visitor-confirmed; 13 WP originals >1.5 MiB still total 43,522,829 stored bytes; 76% real wire reduction unknown; production repairs 0; WordPress writes 0; rehosts 0; additional spend $0.**

**Review boundary:** Stay on draft #1228, no homepage design changes. Site QA #154 owns browser adjudication; this lane owns accession/copyright/crop/960px restoration plans and their testable safeguards.
