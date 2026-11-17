# Wikimedia Commons eight fine-detail images — source catalog clearance, 2026-11-08

**Scope:** An isolated, source-only correctness improvement to the 68 conditional JPEG width-1280-to-960 candidates in [the 118-image inventory](../qa/media-recovery/wikimedia_118_width_960_census_20261108.json). This is NOT a browser test, a download/cache authorization, or a live website edit. Site QA #154 owns the CDP browser collector and six P0 missing-image slots.

## New concrete findings

Eight exact original file titles were individually traced to Wikimedia Commons catalogs. **Four original masters are narrower than 960 px**: Glomar crew patch **800×533** (218:2), Apollo 12 LRO marked landing-site image **800×800** (257:6), Archimedes Palimpsest page **665×448** (268:0), and three Antikythera fragments **786×435** (254:4). These cannot be honestly described as 960px downscaling opportunities; do not enlarge them. Their proposed maximum no-upscale widths are their native widths. The other four have native widths **1475, 5472, 8160, 8385**, but show map labels, tiny gear features, or XRF manuscript text requiring visual review before any width reduction. **All eight remain HOLD.** The broader 68 conditional JPEG URL group must not be mass rewritten: source width parameters are not browser byte measurements.

| Image slot | Native image | Conditional maximum proportional preview | Commons catalog license description | Precision concern |
| --- | --- | --- | --- | --- |
| 218:2 | 800×533 | 800×533 | PD_US_GOV_CATALOG_ASSERTION | CIA crew patch includes wordmark; text legibility |
| 254:2 | 5472×3648 | 960×640 | CC_BY_SA_4_0 | surviving gear-wheel detail |
| 254:4 | 786×435 | 786×435 | CC_BY_2_0 | small identified fragments and Commons annotations |
| 256:1 | 8385×11736 | 960×1344 | PUBLIC_DOMAIN_CATALOG_ASSERTION | small Sanborn map lettering and infrastructure annotations |
| 257:6 | 800×800 | 800×800 | PD_NASA_CATALOG_ASSERTION | small lunar equipment and footpath arrows |
| 268:0 | 665×448 | 665×448 | PUBLIC_DOMAIN_CATALOG_ASSERTION | manuscript microtext and Greek writing |
| 268:6 | 8160×10880 | 960×1280 | CC_BY_3_0_CATALOG_ASSERTION | XRF iron map and faint erased handwriting |
| 367:1 | 1475×923 | 960×601 | CC_BY_SA_2_5 | route-map labeling and refueling tracks |

The Commons file pages checked on Nov 8 are the **exact** `catalog_url` records for these eight slots in the [machine-readable audit](../qa/media-recovery/commons_8_fine_detail_catalog_20261108.json). Source trail includes the [NASA Apollo 12 LRO file](https://commons.wikimedia.org/wiki/File:Apollo_12_LRO.jpg), [CIA Glomar patch](https://commons.wikimedia.org/wiki/File:Glomar_Patch.jpg), [Archimedes manuscript](https://commons.wikimedia.org/wiki/File:Archimedes_Palimpsest.jpg), [Antikythera fragments](https://commons.wikimedia.org/wiki/File:Fragments_of_the_Antikythera_Mechanism.jpg), [Antikythera gears photograph](https://commons.wikimedia.org/wiki/File:Mechanism_of_Antikythera%2C_150-100_BC%2C_NAMA%2C_191435.jpg), [Black Tom LOC survey map](https://commons.wikimedia.org/wiki/File:Map_of_Black_Tom_Island%2C_Jersey_City%2C_New_Jersey_-_showing_area_damaged_by_explosion_and_fire%2C_July_30th_1916._LOC_2010588272.jpg), [XRF Palimpsest](https://commons.wikimedia.org/wiki/File:028v-021r_Arch08r_XRF_FeFront_registered_%289734104759%29.jpg), and [Chrome Dome route map](https://commons.wikimedia.org/wiki/File:Operation_Chrome_Dome_route.jpg).

**Licensing:** The file catalogs report four Creative Commons licensed items (CC BY 2.0, CC BY 3.0, CC BY-SA 2.5, CC BY-SA 4.0) with potentially mandatory credit, license links, change indications and share-alike conditions; four carry public-domain catalog assertions. A Commons catalog is not final legal approval of embedded logos, source-chain ownership or reuse jurisdiction. No image binary or full license compliance audit was obtained. The 2016 map historical scene is not a license exception; the 2009 Apollo image must not be misrepresented as a 1969 surface photograph.

## Engineering and release conditions

[Validator](../qa/media-recovery/validate_commons_8_fine_detail_20261108.cjs) joins each row to the exact parent stored URL, ALT, catalog file and conditional width URL, pins parent blob SHA `4c45bf5b2216bf5f0a09dbf8cd5b64136a160107`, enforces native no-upscale and proportional height, and rejects fabricated guest statuses/transfer claims or rights approvals. [Node regression definitions](../qa/media-recovery/test_commons_8_fine_detail_20261108.cjs) cover 22 valid/adversarial cases. **22/22 equivalent V8 checks executed before commit; native Node CI and guest Chrome NOT executed.**

The existing report of **42 broken images is visitor-unverified**; **76% cold-wire reduction is unmeasured**. Prior inventories: 61 posts/355 stored image sources, newer mixed-date 66/361, 15 originals above 1.5 decimal MB totaling 47,096,779 **stored** bytes. Source catalog item provenance improves potential restoration safety but does not establish a broken image, authorize rehosting, or generate measurable byte savings. No WordPress/public/homepage writes, external image download/cache, subscription changes or PR merge.
