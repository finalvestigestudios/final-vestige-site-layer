# Final Vestige Media — November 13, 2026: five new articles, six Commons image sources

**Draft-only source/rights/weight audit; no visitor-browser outage or network-byte saving claimed.** This work is independent of Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154), existing recovery draft [#1655](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1655), broader recovery [#1703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1703), and homepage visuals. Worklist: `docs/IMAGE-WEIGHT-WORKLIST.md` at #183 (blob `2acd06a4ca4317646006eb6591face3fe76fedec`), absent `main`.

## Exact new-scope reconciliation

Read-only authenticated `posts.list(status=publish)` returned **66 posts**, versus frozen Site QA #154's **61** historical published IDs (355 stored inline images). All original IDs remain published. Precisely five added November 2 posts were independently read using `posts.get(context=edit)`. These add **six** literal `<img src>` elements: IDs 1917 (2), 1920 (2), 1922 (0), 1924 (1), 1926 (1), making **361 raw inline slots**. Every new stored source is an offsite `commons.wikimedia.org/wiki/Special:Redirect/file/` link. Under Media Recovery's 288 historical offsite-source counting method that is **294/361**; this does not resolve or silently overwrite Site QA's historical **286** count (the +2 difference previously isolated to third-party Jetpack tenants in posts 285 and 291). No guest `currentSrc` was collected, so runtime proxy/origin requests could differ.

[Six-row machine record](../qa/media-recovery/wp_nov02_five_post_six_commons_20261113.json) contains exact published source URLs, ALTs, full figure captions, official Commons catalogs, catalog native pixels, rights status, proposed conditional 960px geometry, unmeasured guest HTTP/pixels/bytes, and refusal flags.

## Exact original-to-authoritative catalog mapping

| WordPress slot | Source file catalog and original dimensions (not on-wire) | Catalog rights | Current requested Commons rendition | Conditional max-width 960 output |
| --- | --- | --- | --- | --- |
| 1917:0 | [Piri Reis map](https://commons.wikimedia.org/wiki/File:Piri_reis_world_map_01.jpg), 1964×2619 | Public-domain faithful 2D reproduction; jurisdiction caveat | width=1280 | 960×1280 |
| 1917:1 | [Cantino planisphere](https://commons.wikimedia.org/wiki/File:Cantino_planisphere_(1502).jpg), 10643×4998 | Public-domain historical work / mechanical scan | width=1280 | 960×451 (map legibility HOLD) |
| 1920:0 | [Lycurgus front](https://commons.wikimedia.org/wiki/File:Front_of_4th_century_CE_Roman_Lycurgus_Cup,_British_Museum_(1958,1202.1).jpg), 2720×3649 | Chappsnet, **CC BY 4.0** | width=1280 | 960×1288 |
| 1920:1 | [Lycurgus top](https://commons.wikimedia.org/wiki/File:Top_view_of_the_famed_Lycurgus_Cup_in_the_British_Museum,_showing_the_glass_both_green_and_ruby_red.jpg), 3024×4032 | Chappsnet, **CC BY 4.0** | width=1280 | 960×1280 |
| 1924:0 | [Le Baquet de Mesmer](https://commons.wikimedia.org/wiki/File:%22Le_Baquet_de_Mesmer%22_Wellcome_M0006352.jpg), 2988×3538 | Wellcome Collection, **CC BY 4.0** | width=900 | 960×1137 only if independently master-sourced; don't upscale existing 900px rendition |
| 1926:0 | [Crystal Skull British Museum](https://commons.wikimedia.org/wiki/File:Crystal_Skull_British_Museum_26072013_05.jpg), 1436×2001 | Vassil, **CC0 1.0** | width=900 | 960×1338 only if independently master-sourced; don't upscale existing 900px rendition |

These are **same-named catalog file leads**, not proofs of identical downloaded binary, crop, decoded dimensions, responsive representation or permission to host a derivative. No binary was fetched.

All six current WordPress image **captions already provide attribution/rights text**. Therefore do not claim missing credits. Review full license-compliance details before republication: CC BY 4.0 normally requires appropriate license link and change notices on derivatives, and catalog rights do not clear every institutional, moral, privacy or contractual concern. Piri Reis maps and especially the very detailed Cantino planisphere need readable archival labels and full-resolution zoom paths; a single 960px version must not replace access to detailed originals.

**New raw-markup visual risk:** all six `<img>` elements omit explicit `width` and `height` HTML attributes. This is **not** proof of CLS because theme/CSS/plugin runtime layout may reserve space. Ask Site QA for actual rendered `getBoundingClientRect`, CLS/visual evidence and desktop/mobile `currentSrc` before applying any markup fix.

## Methodology and safe deployment path

The archive-original catalog sizes (including Cantino's 35.99 MB original file) are **not** measured visitor downloads. The published URLs request Commons width=1280 or 900 renditions; browser transformation and cache behavior are unknown. Compare measured **uncached** `Network.loadingFinished.encodedDataLength` for source-bound identical slots and request IDs, with same viewport/DPR, complete event chain, valid Image MIME and decoded natural width/height, then calculate `100*(baseline_bytes-candidate_bytes)/baseline_bytes`. Repeated full-census cold runs and stable scene/crop are required before any site-wide **76%** reduction claim. Do not mix original WordPress storage totals with visitor transfer.

Maximum 960px **width**, no upscale; target CSS width must satisfy `rendered_css_width * device_pixel_ratio <= candidate_natural_width` to avoid expected softness, and retain full-size archival map viewing as applicable. For a legal, editorially approved exact-image candidate only: generate derivative from authorized master, choose responsive `srcset` with safe larger alternatives when needed, retain ALT/caption/source links and proof of the right-to-rehost, stage a reversible image-only change and run real browser visual QA. WordPress Media/production post edits are **not authorized** by this draft. Static cached local copy requires separate licensing and owner approval.

## Gate and handoff

The existing Site QA #154 browser collector alone owns original P0 queue **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**. Do **not** add a competing collector or reorder that queue. These six newly published Commons references are P1 verification after genuinely broken priority items. The historical **42 allegedly broken** remain unverified in a visitor browser; the proposed **76%** remains unmeasured. The earlier **15** WordPress originals above 1.5 decimal MB still total **47,096,779 stored bytes**; separate latest draft #1655 census finds **16** / **49,107,665** including a draft-attached image #2432, not a confirmed published-article transfer.

Fail-closed validator and adversarial tests: `qa/media-recovery/validate_nov02_six_commons_20261113.cjs`, `test_nov02_six_commons_20261113.cjs`. Tests are safe and offline. Native Node and full CI should run at review; no guest Chromium measurement or WordPress production change is claimed here. **Zero downloads, new caches, WP writes, homepage design edits, merges, deployment, or subscription spending.**
