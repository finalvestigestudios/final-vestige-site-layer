# Black Tom 256 — seven-image archive custody, rights, and no-upscale review (2026-11-02)

**Scope:** isolated recovery engineering on draft PR #183. Frozen authenticated post-256 source (2026-10-30, part 05 Git blob `9b16b828342a9ac338f3e65610fd3d8d508355e9`) lists seven exact offsite Commons Special:Redirect images. This run did not make a fresh WordPress source request. No production edits, image downloads, rights approvals, browser claims or spend.

## Confirmed source facts

All **7/7 canonical Commons file catalog HTML pages** were readable using an independent web retriever on 2026-11-02. Attempts to open **the seven exact published Special:Redirect binary URLs** returned **tool URL not accessible** without a numeric origin HTTP response. This is not evidence of seven broken public images. The visitor-browser HTTP status, `currentSrc`, decoded pixels, request IDs, transfer bytes and screenshots remain unknown. Source-to-catalog titles match, but no binary hash/crop comparison was performed.

| Slot | Catalog master px (not rendered pixels) | Conditional ≤960-wide derivative | Archival lineage / right-to-rehost review |
|---|---|---|---|
| 256:0 | 800×528 | 800×528 | Wikimedia Commons (source cited to New Jersey City University historical project); **HOLD** |
| 256:1 | 8385×11736 | 960×1344 | Library of Congress, Geography and Map Division, Sanborn Map Company; **HOLD** |
| 256:2 | 800×537 | 800×537 | Wikimedia Commons (source cited to New Jersey City University historical project); **HOLD** |
| 256:3 | 800×545 | 800×545 | Wikimedia Commons (source cited to New Jersey City University historical project); **HOLD** |
| 256:4 | 5766×4141 | 960×689 | Library of Congress, Bain News Service, LC-DIG-ggbain-22370; **HOLD** |
| 256:5 | 412×720 | 412×720 | Evening Star / Chronicling America (Underwood & Underwood photographers); **HOLD** |
| 256:6 | 800×535 | 800×535 | Wikimedia Commons (source cited to New Jersey City University historical project); **HOLD** |

**High-value technical finding:** Commons redirects request `width=1280` for all seven images, but **five master files are already narrower than 960px** (four 800px photographs and one **412px** newspaper image). Do **not** enlarge them to 960/1280 or claim browser-side upscaling without a real browser capture. The Sanborn map is a **tall 8385×11736** archive original (Commons lists 10.35 MB **master storage**, not the page's actual transfer); a proportionate 960×1344 thumbnail needs an optional link to the full archival viewer because its labels will be too small at that width. LOC Bain glass-negative master 5766×4141 could yield 960×689, conditional on inspecting actual pixels.

**Primary archival identifications:** Slot 256:1 [LOC Sanborn 2010588272](https://www.loc.gov/item/2010588272/) (LOC Geography and Map Division notes free use absent a specific rights advisory). Slot 256:4 [LOC Bain News Service 2014702309](https://www.loc.gov/item/2014702309/) / LC-DIG-ggbain-22370 (LOC states **no known restrictions**, not a positive blanket license). Slot 256:5 originated in the [August 2, 1916 *Evening Star*](https://chroniclingamerica.loc.gov/lccn/sn83045462/1916-08-02/ed-1/seq-4/) (Underwood & Underwood; Commons marks US public domain). Slots 256:0/2/3/6 are four distinct Commons photo titles whose upstream custody is attributed only to a historical New Jersey City University page and a generic government author; that is **not an item-level archival accession or a verified original creator**. Commons claims U.S. public-domain status for the 1916 works; preserve attribution/territorial rights review.

**Chronology and historical truth:** Preserve 1916 aftermath versus original 30 July incident. A [separate Coast Guard Black Tom article](https://www.mycg.uscg.mil/News/Article/4152594/espionage-act-and-the-origins-of-port-security/) supplies independent context/imagery, **not the same photograph** and not a silent substitute. Published 256:4 ALT says the diver is *preparing* to recover shells, while LOC says *recovering*; treat that as an editorial review suggestion, not a content rewrite. Slot 256:5 is a newspaper photograph/reprint, not a contemporary modern child portrait.

## Safe cache / performance decision

1. Keep all exact seven published image references until Site QA #154's existing guest-Chromium harness establishes an actual broken source. **P0 285:5, 287:5, 418:1–2, 407:1 remain ahead of this post.** No duplicate browser tool or Site QA draft changes.
2. For any *proven* failure, require item-specific rights and primary source match, original crop and figure-label review, credit and ALT review. Inspect the licensed binary and hash before a **no-upscale max-960px** draft derivative is prepared. Preserve map detail via link to catalog rather than silently cropping.
3. Cache only after independent authorizations; stage WordPress media privately and capture before/after real uncached CDP image request bytes, decoded geometry and mobile/desktop screenshots. Reproduction and WordPress production publishing are currently **HOLD**.
4. The frozen baseline remains **61 articles / 355 stored slots / 288 external-origin slots / 13 WordPress originals >1.5 MiB**; the reported **42 broken** and **76% reduction** are not verified by browser evidence. There are **0 production replacements**.

Machine packet: [Black Tom source archive audit](../qa/media-recovery/black_tom_256_archive_20261102.json). Regression: `node qa/media-recovery/test_black_tom_256_20261102.cjs`, 30/30 isolated V8 checks passed before committing; native Node/CI and public visitor-browser checks are outstanding.
