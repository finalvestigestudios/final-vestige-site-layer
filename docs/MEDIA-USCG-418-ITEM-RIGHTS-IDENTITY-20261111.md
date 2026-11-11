# USCG Scotch Cap 418:1 and 418:2 — primary-source item/rights crosswalk (2026-11-11)

**This is source-only recovery work; no visitor browser failure, WordPress write, image download, production operation or homepage design change.** The existing Site QA #154 collector retains sole browser ownership. PR #183 holds the image-weight worklist.

## New finding, 418:1
The exact published image URL, `https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG`, is documented by the **official Coast Guard item record** [TLBL: Scotch Cap Disaster](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/). It is **Chief Petty Officer Anthony Pettit's service portrait**, not lighthouse debris. Catalog VIRIN: `210330-G-DE713-0002.JPG`. The official item labels this image public domain and cleared for release, requests photographer credit, and links [DoD visual-information limitations](https://www.dma.mil/Services/Visual-Information/References/Limitations/) concerning endorsement/insignia and associated reuse conditions. That is meaningful *item-specific* provenance/rights evidence, but not automatic authorization for this workflow to download, publish, or assume exact binary hash.

The official catalog advertises an approximately **0.04 MB** download. This is not a measured visitor transfer. The `1920/1080/0` rendition path is not proof of native image dimensions: retain **native dimensions unknown** and 960px **conditional maximum** with no upscaling and no crop until an authorized master inspection.

## 418:2 remains different and unapproved
Published original: `https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg`. [Lighthousefriends](https://www.lighthousefriends.com/Scotch_Cap_debris2_1946.jpg) displays a 1946 bluff-side debris image sharing the filename, but filename/similar scene does **not** prove pixel identity, source permission, or license. Do not swap the portrait for debris or substitute a rebuilt 1950 lighthouse. Original rights and native dimensions still HOLD.

Independent web retriever returned **403 wrapper errors** on both published originals on November 11, 2026. The Lighthousefriends alternate displayed; these are NOT HTTP statuses from a cold guest browser, not confirmed broken images.

## Execution plan and guardrails
1. Site QA #154 checks the six P0 exact sources in order `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`; collect completed uncached CDP Image request, final URL, status, MIME, cache flags, natural pixels, decoded identity, full-page screenshot and image transfer bytes. Never infer from web retriever errors.
2. Once guest failure and item-level rights are independently verified, obtain editorial approval to stage a **same-image**, correctly credited WordPress derivative. Respect `min(960px, verified native width)`; no crop, upscaling, or diagram-detail destruction. Compare guest browser displays before and after; preserve rollback source.
3. No production post block edit, binary copy, cache, theme/homepage modification, deployment or paid API use without explicit separate approval.

Historical baseline: 61 posts / 355 inline positions / 288 external source positions researched; **42 reported broken images unconfirmed**. Performance: **76% proposal unmeasured**; 15 WP originals >1.5 million decimal bytes total **47,096,779 stored bytes**, not cold visitor transfer.

Machine audit: `qa/media-recovery/uscg_418_p0_official_catalog_item_rights_20261111.json`. Regression: `test_uscg_418_item_lineage_20261111.cjs`.
