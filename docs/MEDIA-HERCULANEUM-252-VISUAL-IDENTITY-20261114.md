# Media QA — Herculaneum papyri #252, source and caption identity (2026-11-14)

**Scope:** authenticated read-only WordPress post #252, published and modified 2026-11-14T18:44:18 (WordPress local time); six stored off-site Wikimedia Commons `<img src>` references. No browser HTTP status or bytes observed. Isolated from Site QA #154 and homepage design.

## Three verified subject-description mismatches — editorial review, no CMS edits

| Slot | Stored caption/ALT characterization | Cataloged subject | Correction proposed only |
|---|---|---|---|
| 252:1 | Historic view of papyrus rolls | **Ground plan of Villa of the Papyri showing tunnels** from 1908 *Herculaneum, Past, Present & Future* | Identify it as a villa ground plan, not a photograph of scrolls |
| 252:4 | Preserved Greek writing on carbonized papyrus fragment | **Hand-drawn facsimile** of PHerc. 1425 by Giuseppe Casanova, c. 1807 | Call it a historical drawing/transcription, not an ancient fragment photograph |
| 252:5 | Digitized ancient papyrus text | **Handwritten copy** of PHerc. 1005, col. 5, Casanova (attribution qualified), 1803–1806 | Identify the early nineteenth-century copy, not a direct scan |

Catalogs (exact same file identities, not substitutes):
- https://commons.wikimedia.org/wiki/File:Herculaneum,_past,_present_and_future_(1908)_(14596218878).jpg
- https://commons.wikimedia.org/wiki/File:Herculaneum_papyrus_1425.png
- https://commons.wikimedia.org/wiki/File:Tetrapharmakos_PHerc_1005_col_5.png

## Six-item rights, dimensions and conditional WordPress plan

| Slot | Catalog native px | Maximum width <=960 px, no upscale | Cataloged right / release gate |
|---|---|---|---|
| 252:0 | 2006×1740 | 960×833 | 2021 research photograph **CC BY 4.0**; complete named-author credit, linked license and change disclosure if transformed |
| 252:1 | 3334×948 | 960×273 | 1908 public-domain-era book scan via Flickr Commons, **no known restrictions** assertion; confirm image/jurisdiction reuse and inspect fine ground-plan legibility |
| 252:2 | 876×552 | **876×552 native** | 1908 book illustration, Commons public-domain historical work; no upscale |
| 252:3 | 2000×1432 | 960×687 | British Library manuscript photograph, Commons PD-marked but **US PD tag missing**; check exact rights and reproduction terms |
| 252:4 | 500×740 | **500×740 native** | c. 1807 two-dimensional hand-drawn transcription, Commons PD-Art; review jurisdiction, retain text readability |
| 252:5 | 467×179 | **467×179 native** | c. 1803–1806 handwritten transcription, Commons PD-Art flags missing US PD tag; do not upscale |

Additional catalog URLs and exact stored origin URLs are in `qa/media-recovery/herculaneum_252_six_visual_identity_20261114.json`. **Historical/archival custody alone does not authorize WordPress rehosting.** A CC BY 4.0 photo is not unconditionally public-domain. In particular, a modern photo of historic paper and an early-modern handwritten facsimile are not interchangeable.

**Staging only after P0 logged-out browser evidence and rights review:** If a specific image is actually broken, verify the *same exact cataloged work*, permission, attribution, binary identity, sha256, visitor visibility and natural pixels; make a 960px-or-native derivative preserving aspect and fine print (DPR review), stage WordPress Media Library cache/responsive `srcset` under a new item with reversible mapping and unchanged captions pending separately approved corrections. Compare cold mobile/desktop transfer bytes, image integrity, layout shifts and LCP against a same-device baseline. Do not bulk rewrite Gutenberg or hotlink/scrape unlicensed files.

Historical baselines remain **61 posts / 355 stored images**, 42 reported broken **not visitor-confirmed**, claimed 76% visitor weight reduction **not measured**, and 16 >1.5 decimal MB first-party originals totaling 49,107,665 **stored bytes** (not page-transfer bytes). Site QA #154 retains exclusive ownership of the six-P0 browser collector.

**Safety:** Zero production writes, assets downloaded/copied/cached, homepage edits, deployments, merged code or spending. Offline validator rejects invented network/binary evidence, unauthorized rehosting flags, source swaps, subject mismatch suppression and 960px upscaling.
