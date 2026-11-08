# Navy source-recovery bridge — two formerly unresolved published image slots
**Date:** 2026-11-08 Pacific. **Scope:** media recovery Draft PR #183 only; read-only authoritative catalog research and offline QA. Complements, does not replace, Site QA Draft PR #154.

## High-value findings
The previous [eight-source Navy audit](../qa/media-recovery/navy_8_live_pueblo_honda_retriever_20261108.json) confirmed two published images had no independently matched archival accession. Both now have a traceable **catalog-level** path, and the USS Banner slot also has three specific alternate scenes:

| Published slot | Original embedded subject | Official catalog candidate | Catalog-advertised master TIFF | Conditional <=960px proportional output |
|---|---|---|---|---|
| 280:4 | USS Banner in Pueblo story | NH 68705, **port bow**, 12 May 1969 | 6312 × 4750 | 960 × 722 |
| 280:4 | Same | NH 68703, **stern**, 12 May 1969 | 4766 × 6274 | 960 × 1264 |
| 280:4 | Same | NH 68706, **bow**, 12 May 1969 | 4846 × 6194 | 960 × 1227 |
| 288:2 | Mare Island radio equipment | UG 21-01.02, Building 115 Electrical School | 2197 × 2773 | 960 × 1212 |

Catalog sources: [NH 68705](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-68000/NH-68705.html), [NH 68703](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-68000/NH-68703.html), [NH 68706](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-68000/NH-68706.html), [UG 21-01.02](https://www.history.navy.mil/our-collections/photography/technology/communications/radio/ug-21--us-naval-california-radio-station-collection/mare-island-naval-radio-station/ug-21-01-02-mare-island-naval-radio.html), and [DANFS Banner II](https://www.history.navy.mil/research/histories/ship-histories/danfs/b/banner-ii.html).

**Crucial visual-integrity distinction:** the three Banner images are **different photographs of the same ship** until visually matched against the currently embedded DANFS image. No same-image restoration is confirmed. NHHC identifies the radio photograph as equipment in Building 115; the item metadata does **not** establish that the equipment was a 1923 shore direction finder. Do not imply a dated operational scene from this undated reference.

The source-page search results list **Medium JPEG** files of 228 KB, 213 KB, 232 KB and 189 KB respectively, with 1280px rendition envelopes. These numbers are **catalog claims, not actual visitor-transfer measurements**. Above proportional dimensions are computed from **advertised high-resolution TIFF sizes**, not verified dimensions of the PNG/JPEG delivered by the live site. A binary/source identity check must precede any derivative creation.

## Rights, browser evidence, and publication
The catalog field **Copyright Owner: Naval History and Heritage Command** occurs for the four official records. This is **not a public-domain declaration**. The Banner records say *Courtesy of USS Banner, 1969*, and UG 21-01.02 says *Donor: Found in collection*. Per [NHHC Photo Archives](https://www.history.navy.mil/our-collections/photography.html), the archive holds both official and donated material; most images are public domain, but NHHC does not warrant individual copyright status. **No caching/republication rights are presently cleared.**

On Nov 8 the previous source-retriever returned **NOT_ACCESSIBLE_IN_TOOL** (280:4) and **BAD_GATEWAY** (288:2), neither origin nor logged-out browser status. Current guest HTTP, decoded natural dimensions, currentSrc, wire bytes, image hashes and same-photo identity all remain **null**. Subsequent direct official-catalog opens in this investigation also encountered gateway errors/timeouts; catalog-level metadata was available from indexed NHHC records. This is *not* proof of a visitor outage.

**Release sequence:** Site QA #154 takes complete, uncached, logged-out Chrome evidence for the six existing P0 slots before these additional two. If a genuine failure is observed, inspect actual matched images and source rights, preserve correct historical subject and date, obtain approval, then consider a proportional <=960px first-party WordPress media plan. No bulk mirroring, WordPress post/block edits or speculative replacement.

## Reproducibility and safety
- [Two-slot/four-catalog JSON](../qa/media-recovery/nhhc_two_catalog_bridge_20261108.json) binds current published URL and ALT to the already-frozen eight-image audit, with **null guest statuses** and release-hold flags.
- [Fail-closed validator](../qa/media-recovery/validate_nhhc_two_catalog_bridge_20261108.cjs): `node qa/media-recovery/validate_nhhc_two_catalog_bridge_20261108.cjs`. Requires source/ALT equality with upstream, exact accession IDs, NHHC domain, proportional no-upscale, null browser results, and no release flags.
- [22-case regression suite](../qa/media-recovery/test_nhhc_two_catalog_bridge_20261108.cjs): `node --test qa/media-recovery/test_nhhc_two_catalog_bridge_20261108.cjs`. Tests source swaps, invented 404/200, invented 76% savings, rights errors, mismatched dimensions and unauthorized CMS/cache operations.
- **Native Node v22.16.0 local copy: 22/22 tests passed.** Exact committed Git blobs were separately rerun in isolated V8: **22/22 passed; full prior-audit bind PASS**. No guest Chromium pass; runner DNS prevents actual external browsing.
- Historical 61 posts / 355 stored img references; reported **42 broken not guest verified**; proposed **76% wire reduction not measured**. Current separate WordPress media census: **15** originals >1,500,000 bytes = **47,096,779 stored original bytes**, not wire data.
- **Production repairs, WP writes, binary downloads/caching, homepage modifications, paid subscriptions: all zero.**

**No action in this batch changes the existing Site QA browser collector or any homepage owner lane.**
