# West Loch + USS Tang: seven additional published Navy image dependencies (2026-11-09 UTC)

## Concrete verified batch / custody

Read-only authenticated WordPress `posts_get(context=edit)` confirms **seven current embedded U.S. Navy History image URLs** across two published posts, unchanged against the archived 2026-10-30 source inventory:

- **Post 370**, *The Lines Were in the Fire*, modified `2026-11-02T21:40:07`: slots **370:0, :1, :3, :4**.
- **Post 274**, *Twenty-Four Feet from Air*, modified `2026-11-02T21:39:50`: slots **274:1, :2, :4**.

All exact, HTML-entity-decoded image source URLs and post permalinks appear in `qa/media-recovery/navy_west_loch_tang_7_live_20261109.json`. Five exact original paths gave **502 from the independent external web retriever's wrapper**; two were **not accessible through that tool**. Neither response mode is a verified HTTP status from Navy's server or a visitor browser; `actual_origin_http`, `actual_guest_http`, `visitor_broken` and browser wire bytes remain **null for all seven**. No new broken-image claim is made. Direct container HTTP also cannot resolve `finalvestige.com` from this runner (DNS resolution failure); do not misreport this as public-site downtime.

## Official primary catalog crosswalk, not replacement approval

| Post slot | Archival ID | Official primary catalog | High TIFF catalog pixels | Conditional geometry from that TIFF at 960px width | Navy-listed medium JPEG (not wire bytes) | Identity note |
|---|---|---|---|---|---|---|
| 370:0 | 80-G-276907 | https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-270000/80-G-276907.html | 4320×4530 | 960×1007 | 239KB | May 21, 1944 West Loch burning LSTs |
| 370:1 | 80-G-202485 | https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/80-G-202000/80-G-202485.html | 5860×4890 | 960×801 | 214KB | **November 6, 1943 Bougainville**, not the 1944 West Loch disaster; contextual illustration only |
| 370:3 | 80-G-276940 | https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-270000/80-G-276940.html | 6254×5002 | 960×768 | 237KB | May 22, 1944 burned-out LST-39 |
| 370:4 | SC 427947 | https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/sc-series/SC-400000/SC-427947.html | 6084×4942 | 960×780 | 256KB | **U.S. Army Signal Corps** image archived with Navy/NARA; may depict LST-480 |
| 274:1 | 80-G-227987 | https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-g-227987-uss-tang--ss-306-.html | 4908×5948 | 960×1163 | 303KB | Richard O'Kane with 22 rescued aviators, May 1944 |
| 274:2 | NH 84498 | https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-84000/NH-84498.html | 6216×4876 | 960×753 | 157KB | Navy photograph includes **Mark 18-2 AND Mark 16-1** torpedoes, not just one |
| 274:4 | 80-G-344565 | https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/wwii/wwii-pacific/japanese-surrender/allied-prisoners-of-war/80-g-344565.html | 1464×1938 | 960×1271 | 343KB | Released Richard O'Kane photo, September 24, 1945 |

**Dimension integrity:** High TIFF dimensions come from each named catalog record. The 960-wide heights are proportional estimates for that *listed high-resolution scan* and **not observed dimensions of the currently embedded Navy medium JPEG**. The latter may differ in rotation/crop and remain null. Never upscale a lower-resolution rendition, crop a portrait into a landscape slot, or shrink labels until unreadable. Medium-size catalog KB figures are advertisements, not downloaded bytes or measured browser transfers. No asset binaries were fetched.

**Rights:** The NHHC official image guidance notes that most (not all) archive photographs are public domain and permits digital downloads, subject to rights: https://www.history.navy.mil/about-us/instructions-and-forms/obtain-duplications-of-records-and-photos.html . National Archives explicitly cautions that federally held material can have donated/private restrictions and item clearance remains the reuser's responsibility: https://www.archives.gov/research/still-pictures/permissions . Credit by photo number and owning collection; 370:4 is Army Signal Corps/NARA rather than simply a Navy-created picture. All `item_specific_clearance` and `exact_source_binary_verified` remain false. No automated external download, WP caching or publication is approved.

## Workflow and site QA coordination

Existing **Draft PR #154** remains the sole owner of guest CDP/Chrome measurement, so this branch does **not** create another browser collector. Start with the original six P0 slots **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**, and only then measure these seven Navy references (especially the four `bin/imageDownload` URLs, which share a source endpoint). Collect exact `currentSrc`, HTTP result / redirect, MIME, cache provenance, positive intrinsic geometry, actual CDP encoded bytes, screenshots and mobile visual completeness. If a source is genuinely broken, verify catalog item identity and item-level rights before staging a legal, faithful derivative on width<=960, keeping larger maps if text needs reading. Record old block markup/ALT/captions/attachment IDs for rollback; do not alter production Gutenberg blocks or media without explicit separate approval.

The previous [eight Navy source cases in Draft #1703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1703) covered posts **280 and 288**. The seven new slots are disjoint from its **43** source entries: cross-ledger distinct union now **50 investigations**, NOT 50 visitor failures. The historical site-wide baseline is **61 posts / 355 image refs**, with **288 third-party-origin** after Jetpack upstream-origin correction (source inventory is stale if newer posts are counted). A separate inventory has **66 posts / 361 refs**. The **42 reported broken originals** remain unverified via guest Chromium; the proposed **76% browser-transfer reduction** remains unmeasured and must not substitute 15 stored WP originals (>1.5 decimal MB, total 47,096,779 stored bytes) for network bytes.

### Test and release boundary

- JSON: `qa/media-recovery/navy_west_loch_tang_7_live_20261109.json`
- Fail-closed validator: `qa/media-recovery/validate_navy_west_loch_tang_7_20261109.cjs`
- Regression suite: `qa/media-recovery/test_navy_west_loch_tang_7_20261109.cjs`
- **28/28 committed-file isolated V8 Node-compatible tests passed**: two controls and 26 adversarial falsification cases; native `node --test`/CI and guest Chrome remain unrun.

No WordPress writes, downloads, caches, homepage modifications, merged/released files, subscription charges, or unauthorized image substitutions.
