# Apollo 1 official NASA image route custody — 16 November 2026 (read-only; release HOLD)

Scope: WordPress post **434**, [The Hatch Opened Inward](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/), last modified **2026-11-15T12:58:22** in authenticated WordPress EDIT and VIEW responses. Six `<img>` slots were compared. Slot 0 is already a first-party WebP via Jetpack with `width=1041`, `height=810`, `srcset`, and `sizes` in the WordPress VIEW response. Slots **1–5 are five NASA Images originals rewritten through the Jetpack i0 proxy**; **all five lack `width`, `height`, `srcset`, and `sizes` in the VIEW HTML**. This is responsive-markup review evidence, **not** proof of missing visitors' images, decoded dimensions, actual CLS, or network-weight excess. Theme/browser behavior may differ.

## Exact upstream route, archive accession and reader outcome

| Slot | NASA accession / EDIT original | WP VIEW proxy | Independent *original* image reader |
|---|---|---|---|
| 434:1 | [S67-15717](https://images-assets.nasa.gov/image/S67-15717/S67-15717~large.jpg) | [Jetpack](https://i0.wp.com/images-assets.nasa.gov/image/S67-15717/S67-15717~large.jpg?ssl=1) | **Rendered image** |
| 434:2 | [S66-58038](https://images-assets.nasa.gov/image/S66-58038/S66-58038~large.jpg) | [Jetpack](https://i0.wp.com/images-assets.nasa.gov/image/S66-58038/S66-58038~large.jpg?ssl=1) | Reader inaccessible |
| 434:3 | [KSC-20170124-PH_KLS01_0164](https://images-assets.nasa.gov/image/KSC-20170124-PH_KLS01_0164/KSC-20170124-PH_KLS01_0164~large.jpg) | [Jetpack](https://i0.wp.com/images-assets.nasa.gov/image/KSC-20170124-PH_KLS01_0164/KSC-20170124-PH_KLS01_0164~large.jpg?ssl=1) | Reader inaccessible |
| 434:4 | [S67-21294](https://images-assets.nasa.gov/image/S67-21294/S67-21294~large.jpg) | [Jetpack](https://i0.wp.com/images-assets.nasa.gov/image/S67-21294/S67-21294~large.jpg?ssl=1) | Reader inaccessible |
| 434:5 | [KSC-20170124-PH_KLS01_0090](https://images-assets.nasa.gov/image/KSC-20170124-PH_KLS01_0090/KSC-20170124-PH_KLS01_0090~large.jpg) | [Jetpack](https://i0.wp.com/images-assets.nasa.gov/image/KSC-20170124-PH_KLS01_0090/KSC-20170124-PH_KLS01_0090~large.jpg?ssl=1) | Reader inaccessible |

**All five Jetpack URL tests were inaccessible to the independent reader.** That is a limitation of this reader, not a measured HTTP error, Chrome decode failure or live outage; no numeric HTTP status is claimed. NASA [Apollo 1 gallery](https://www.nasa.gov/gallery/apollo-1/) corroborates accessions S67-15717, S66-58038 and S67-21294. The two 2017 NASA/Kim Shiflett accession identities are additionally cross-referenced by [KSC 0164 Commons catalog](https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_spacecraft_mockup.JPG) and [KSC 0090 Commons catalog](https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_Block_II_hatch.JPG) (secondary catalogs, not image masters).

## Rights, 960px geometry and visually faithful candidate mapping

[NASA's official media usage guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) generally allow non-promotional, factual editorial use of NASA-created imagery; NASA credit is required/expected, **no endorsement**, and item-level exceptions, incorporated third-party copyrights, NASA emblems and commercial publicity rights must still be reviewed. These five candidate master accessions are plausible **same-photo routes**, not cleared copies or authorized WordPress uploads.

The 2017 Commons catalogs identify original dimensions of **6720×4480** for KSC 0164 and **4480×6720** for KSC 0090. Their *conditional proportional dimensions* when width is capped at 960px are **960×640** and **960×1440**, respectively; they describe those catalog items, not verified decoded WordPress-source pixels. For S67-15717, S66-58038 and S67-21294, binary/native dimensions remain unknown, so no image derivative height is asserted. **Never upscale, invent a crop match, replace with merely related NASA imagery, or use a catalog HTML page as a replacement binary.**

Safe conditional cached/WordPress plan: (1) Site QA #154 first completes its previously identified six P0 browser failures; (2) when capacity permits, run its *existing* logged-out browser collector for these five (no duplicate collector) recording exact `currentSrc`, numeric GET/redirect/MIME, decoding/`naturalWidth`, screenshots and wire bytes; (3) confirm which specific image actually fails; (4) match exact NASA accession, source pixels and crop, review rights and credit; (5) calculate aspect-preserving derivative `min(nativeWidth,960)` without upscaling and verify responsive markup & before/after desktop/mobile visual fidelity; (6) propose reversible WordPress Media Library attachment staging with binary SHA-256, credit, original URL, a rollback ID and explicit approval. **No WP writes, media copies, post-block rewrites, hosting changes, public deployment or paid workflow are authorized here.**

## Repeatable offline gate and program baselines

- Machine-readable [five-slot audit](../qa/media-recovery/apollo1_nasa_five_slot_custody_20261116.json) pins WP EDIT/VIEW exact image routes, NASA accession IDs, reader-method outcomes, source policy, null actual HTTP/guest/byte fields and the only two catalog-calculated geometries.
- [Fail-closed evaluator](../qa/media-recovery/assess_apollo1_nasa_five_slot_20261116.cjs) forbids fabricated browser/HTTP statuses, premature rights/cache claims, wrong URLs/IDs, resize errors, rehosting and WordPress writes.
- [33-case Node-compatible regression definitions](../qa/media-recovery/test_apollo1_nasa_five_slot_20261116.cjs) were executed under isolated **V8** against the exact GitHub-committed evaluator (33 passed/0 failed); native Node repository execution and CI remain pending.
- Historical **61/355**, source offsite discrepancy **286 vs 288**, later **66/361**, reported **42 broken** (guest-unconfirmed), proposed **76% wire reduction** (unmeasured), and **20 oversized originals / 64,385,752 stored bytes** remain distinct. WordPress originals do not equal visitor network transfers.

No changes to Site QA #154 files, homepage visual work or FinalVestige.com production. Review-only in isolated media PR #2747.
