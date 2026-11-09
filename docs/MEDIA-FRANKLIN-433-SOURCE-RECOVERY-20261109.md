# Media recovery — Franklin expedition post 433 (2026-11-09)

**Status: DRAFT / DO NOT MERGE / NO PRODUCTION WRITES.** This investigation covers five external images on [All Well Was Written First](https://finalvestige.com/2026/08/20/all-well-was-written-first-franklin-expedition/), distinct from Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154). The sixth, first-party Victory Point document is preserved unchanged.

## Exact source and retrieval facts

The five literal stored URLs, their original ALT descriptions, dates, catalogs, image constraints and per-image rights gates are preserved in [the JSON audit](../qa/media-recovery/franklin_433_five_source_20261109.json), joined to the **October 30** frozen WordPress fixture `qa/media-recovery/parts/01.json` at blob `948bc1b65b42799aa40cfdb810ddf6ffd80886b6`.

On **November 9**, literal web-viewer opening **displayed 433:1 and 433:5**; the tool could not open **433:2, 433:3, or 433:4**. None is a confirmed visitor-browser failure; no actual HTTP status, `naturalWidth`, `currentSrc`, transferred bytes, or downloaded binary was obtained.

| Slot | Catalog/source distinction | Conditional 960px dimensions | Rights / visual integrity |
|---|---|---|---|
| 433:1 | *Illustrated London News* ship engraving, 24 May 1845 | **750×523**, no upscaling | Historical public-domain claim from Commons; verify attribution and crop |
| 433:2 | University of Washington, **PORTRAITS 2459**, John Rae photograph, 1886 | **399×600**, no upscaling | Historical US PD asserted; UW transfer warns metadata may need correction |
| 433:3 | British Library **HMNTS 10460.d.5**, John Brown book (1860) | **960×1532** | Retrospective conjectural route map, not ship's own navigation log; offer full map/zoom for tiny labels |
| 433:4 | **FabTet**'s August **2023** photo of 1845 Fitzjames daguerreotype | **960×1159** | Modern photographic reproduction **CC BY-SA 4.0**, credit/license/adaptation and share-alike review required |
| 433:5 | Published CloudFront reward poster visually matches the topic of an archival 1850 notice | **unknown—HOLD** | Related LAC/Commons scan is not established identical in binary/crop or rights; do not substitute it automatically |

Primary and catalog review links: [1845 newspaper image](https://commons.wikimedia.org/wiki/File:HMS_Erebus_and_Terror_-_ILN_1845.jpg), [University of Washington PORTRAITS 2459](https://commons.wikimedia.org/wiki/File:Dr_John_Rae,_with_relics_from_the_Franklin_Expedition,_gold_medal,_and_map,_August_1886_(PORTRAITS_2459).jpg), [British Library HMNTS 10460.d.5 map](https://commons.wikimedia.org/wiki/File:(1860)_Map_of_the_probable_routes_taken_by_HMS_Erebus_and_HMS_Terror_during_Franklin's_lost_expedition_%26_results_of_McClintock's_Arctic_Expedition.jpg), [modern Fitzjames photograph](https://commons.wikimedia.org/wiki/File:L23402-c8qmb-t3-05-rx.jpg), [related 1850 Admiralty poster](https://commons.wikimedia.org/wiki/File:Reward_for_finding_Franklin_Expedition.jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## Safe engineering and handoff

Read-only validation: `node qa/media-recovery/validate_franklin_433.cjs`. Native Node test definitions: `node --test qa/media-recovery/test_franklin_433.cjs`. **16/16 test cases executed successfully using isolated V8 with Node-compatible require shims** against exact committed file contents; this is **not** evidence that native Node CI has run. Fail-closed tests cover fabricated HTTP/browser statuses, false 76% claim, URL mutation, duplicate slots, licensing bypass, premature WordPress changes, upscaling, attribution removal and unsupported poster replacement.

Historical baseline: **61 posts / 355 image positions / 288 external-origin positions** in frozen census; PR #154 reports 286 and this classification difference remains unresolved. The 42 alleged broken images still lack reliable visitor-browser confirmation, and 76% wire-byte reduction is unmeasured. **15 WordPress originals >1.5 decimal MB / 47,096,779 stored original bytes** are not measured visitor transfers. Keep the expanded 66-post inventory separate.

Site QA #154 owns logged-out browser checks. Original P0 six image positions (285:5, 285:2, 287:5, 418:1, 418:2, 407:1) remain first. For confirmed failures, verify exact photo/crop and authoritative catalog, individual rights/credit, legal source download and SHA-256, ≤960px derivatives/no upscaling with readable chart detail, and safe **staged** WP media. Record desktop/mobile decoded load, actual HTTP request/response and byte-count comparison before any claimed performance gains or post rewrite. **All five replacements remain on HOLD; no WordPress write, download, caching, deployment, homepage edit, or spending.**
