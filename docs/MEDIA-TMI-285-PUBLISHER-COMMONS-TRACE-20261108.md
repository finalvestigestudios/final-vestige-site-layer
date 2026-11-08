# Three Mile Island image recovery — source provenance and actual no-upscale geometry (Nov 8, 2026)

This is an **isolated evidence package** for two P0 image slots, **not a WordPress/public website change**. Frozen source `qa/media-recovery/parts/03.json` Git blob `49183f66f880f7c4dfd363acca906876877f2e5e`. Site QA #154 owns the already-existing guest Chromium collector; no duplicate collector created.

## 285:5 — newly established publisher → Commons master trace

Published image: `https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg`. A fresh Nov 8 independent web retriever returned **wrapper 404**. This is not proof of an origin 404 or actual browser failure. The [original publisher article](https://discover.hubpages.com/entertainment/The-China-Syndrome-Blockbuster-Movie-Becomes-Eerie-Prophecy) directly links its aerial photograph to [this Wikimedia original](https://upload.wikimedia.org/wikipedia/commons/0/09/Three_mile_island_062010.jpg), credited as public domain. [The Commons catalog](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) identifies uploader **Marque1313**, creator public-domain dedication, JPEG **819 × 614**, about 235 KB. Rights evidence applies to *that Commons original*, not automatically to every crop or publisher compilation. We have **not** retrieved or hashed the image binary.

**Important visual warning:** The frozen published SayMedia URL requests a **1200px, 16:9 filled crop**; the Commons original is approximately **4:3**. It is likely the same underlying photograph through the publisher link, but exact published-frame pixels have **not been matched**. An uncropped substitute could shift page layout. A 960px rendition would *upscale* an 819px source, so the conditional maximum is **819 × 614**, no crop/no upscale. Commons internally conflicts on photo date (narrative **June 6, 2010**, structured date **June 16, 2010**); do not depict this as imagery from the **1979** event.

## 285:2 — publisher relocation not proven browser failure

Published `https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg`. The Nov 8 web retriever returned wrapper 500 **after redirect** to `https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg`, which this retriever could not access. This is not an actual guest Chrome 500. Neither a legally cleared same-control-panel photograph nor trustworthy native dimensions have been established. A [Nuclear Regulatory Commission schematic](https://commons.wikimedia.org/wiki/File:Tmi-2_schematic.gif) illustrates the reactor, but **is not** a substitute for the published control-panel photograph. Status HOLD.

## Staging/WordPress and measurement plan (no writes)

Site QA's **existing** browser collector should capture exact slot/source, redirected `currentSrc`, network image GET status and request ID, CDP cache flags, decoded natural dimensions, encoded bytes and full-scroll desktop/mobile screenshots. Any browser failure must be isolated first. Then review item-level rights, credit and exact scene; for 285:5 compare published 16:9 composition against Commons full-frame before editorial approval, stage a first-party Media Library item sized at most 819×614, visually test aspect ratio and CLS, and separately authorize any CMS edit, with rollback. Slot 285:2 stays blocked until a same-photograph source and rights are found.

No assets downloaded, mirrored, cached, published or edited. Reported **42 browser-broken images remain unverified**; claimed **76% site-wide transferred-byte reduction remains unmeasured**. Fifteen originals >1.5 decimal MB = 47,096,779 **stored** bytes, not wire traffic.

Machine audit: [JSON](../qa/media-recovery/tmi_285_primary_archive_20261108.json) | [validator](../qa/media-recovery/validate_tmi_285_primary_archive_20261108.cjs) | [26 regression tests](../qa/media-recovery/test_tmi_285_primary_archive_20261108.cjs).
