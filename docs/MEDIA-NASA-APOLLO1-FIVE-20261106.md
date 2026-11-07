# Media recovery: NASA Apollo 1 five-image audit (2026-11-06)

**Status:** isolated evidence and offline QA only. No production edits or downloaded images. Article https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ (WordPress post 434) was read in editor context, read-only.

The article contains **6 inline images: 1 already hosted on FinalVestige.com** (S67-19766.webp, excluded from localization) and **5 external NASA `images-assets.nasa.gov` references**. All six stored image elements already have explicit width and height. No blanket dimension fixes are appropriate.

Five official NASA catalog pages were individually opened and all identify the **exact PIA / KSC photo ID** used by the article, with dimensions:
- S67-15717: 1514 × 1920 → conditional 960 × 1217 (catalog https://www.nasa.gov/image-detail/amf-s67-15717/)
- S66-58038: 1920 × 1546 → conditional 960 × 773 (catalog https://www.nasa.gov/image-detail/amf-s66-58038/)
- KSC-20170124-PH_KLS01_0164: 1920 × 1280 → conditional 960 × 640 (catalog https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/)
- S67-21294: 1920 × 1297 → conditional 960 × 649 (catalog https://www.nasa.gov/image-detail/amf-s67-21294/)
- KSC-20170124-PH_KLS01_0090: 1280 × 1920 → conditional 960 × 1440 (catalog https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/)

The stored URLs appear in the machine-readable audit. **Web retriever:** 1/5 NASA image URLs rendered as a picture; 4/5 image URL fetches returned a *tool internal error*, NOT a browser HTTP status. **All 5 catalog HTML pages were retrievable**. This is NOT evidence that four visitor images are broken; logged-out browser `naturalWidth`, HTTP status and transferred bytes remain unknown. Site QA #154 owns that browser collector.

**Copyright/rights:** NASA's primary [media policy](https://www.nasa.gov/nasa-brand-center/images-and-media/) generally permits informational use of NASA-created media, with source credit, no implied NASA endorsement, and additional restrictions for third-party-owned material, identifiable people, or promotional uses. Captions already credit NASA/JSC or NASA/Kim Shiflett and link catalog pages. Preserve existing linked original/catalog context. Hold any new caching, conversion and WordPress republication until item-level check and browser need; promotional reuse of astronaut likenesses requires separate review.

**Staging-only derivative plan, if need is proven:** acquire only individually authorized original NASA images; retain original, copyright, provenance, metadata and a persistent record URL; compute aspect-preserving `min(960, original width)` output (listed in audit); choose a modern format only after comparing actual decoded quality; use WordPress Media Library attachment + `srcset`, credit and license record, original source link and rollback. Compare cold mobile actual wire bytes and image decoding **before and after**, across the same article and full 61/66-post cohort before asserting 76%. Preserve the two 2017 hatch photographs as different historical subjects, and do not touch existing page blocks or SEO.

**Current global baseline is a prior snapshot, not newly re-counted here:** original 61 posts / 355 references; later 66 posts / 361 references; 42 suspected broken; 13 oversized WP originals (43,522,829 stored bytes). The proposed 76% *transfer* saving remains unmeasured. No live image repairs.

**Verification:** `node --test qa/media-recovery/test_nasa_apollo1_20261106.cjs` and `node qa/media-recovery/validate_nasa_apollo1_20261106.cjs qa/media-recovery/nasa_apollo1_five_20261106.json`. Script has no outbound requests. Coordinate via existing QA draft #154; do not create another media collector or PR.
