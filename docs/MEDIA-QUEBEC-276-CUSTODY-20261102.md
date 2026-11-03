# Media Recovery: Quebec Bridge post 276 (2026-11-02)

**Source-only engineering in draft PR #183; no WordPress writes, downloaded/rehosted images, subscriptions, or homepage edits.** The six exact external image URLs/ALTs are pinned to `qa/media-recovery/parts/04.json` blob `6df3251e5a67a971d87a516a1ba4a0cc32f51f96` (original 2026-10-30 authenticated source snapshot); no new live CMS read this batch.

## Retrieval results for the exact six published image URLs

| Slot | Host / picture | Independent retrieval on November 2 | Original recovery and no-upscale geometry |
|---|---|---|---|
| 276:0 | Picryl, 1907 first span | `web.open` IMAGE_DISPLAYED | [British Library HS85/10/18815 via Commons](https://commons.wikimedia.org/wiki/File:Quebec_bridge_(HS85-10-18815).jpg), F. E. Cudworth, 1907; 2780×2180 original → conditional 960×753; same item catalog, not binary hash verified |
| 276:1 | HistoricBridges, wreckage | IMAGE_DISPLAYED | Current publisher same scene; original maker and reproduction rights unclear. Stored 1024×832 dimensions are not verified master dimensions; permission HOLD. |
| 276:2 | Smithsonian `NMAH-AC1026-0000002` | `web.open` TIMEOUT, separate `web.image` displays exact URL | [NMAH.AC.1026](https://sova.si.edu/record/nmah.ac.1026) exact delivery identifier, pixel geometry unknown; Smithsonian metadata CC0 does **not** license photos. |
| 276:3 | Quebecblogue JPEG | web wrapper `520`, no numeric origin status | Original archival owner, rights and geometry unknown; no safe identical alternative established. |
| 276:4 | Picryl, collapsed 1916 span | IMAGE_DISPLAYED | PICRYL cites Commons; 2048×1536 derivative → conditional 960×720; Commons lists a 12000×9000 TIFF for this photo, **not** an appropriate web master. Exact rights/binary identity pending. |
| 276:5 | HistoricBridges completed span | IMAGE_DISPLAYED | Publisher same scene; rights need approval. Stored 1024×607 geometry is not verified intrinsic master. |

**Retrieval-tool results are not visitor-browser HTTP codes.** Browser response, currentSrc, final redirect, MIME, naturalWidth, actual image transfer bytes, download hashes and screenshots all remain unknown (`null` in the audit). No image counted broken for visitors. Smithsonian image query succeeds where exact `web.open` times out: this is precisely why wrapper errors are not proof of breakage.

## Rights, chronology, and safe restoration plan

- [British Library / Commons HS85/10/18815](https://commons.wikimedia.org/wiki/File:Quebec_bridge_(HS85-10-18815).jpg) records creator F. E. Cudworth, original 2780×2180 (7.18 MB storage), public-domain rationale Canada and US, and custodian. No assumption of publication approval. The ALT phrase 'shortly before' is more precise than the catalog's date of 1907; editorial check recommended.
- [Smithsonian NMAH archival conditions](https://sova.si.edu/record/nmah.ac.1026) state that image reproduction may require permission/fees despite CC0 metadata; no payment authorized.
- [HistoricBridges reuse-contact policy](https://historicbridges.org/info/contact/index.php) requests contact for photography on websites or in published work; avoid unlicensed mirroring.
- Distinguish the [August 29, 1907 and September 11, 1916 bridge failures](https://legacy.csce.ca/en/historic-site/the-quebec-bridge/). Do not swap 1907 wreckage for 1916 submerged center span, or conflate two different camera angles in 1907.
- Site QA PR #154 retains its P0 browser queue: **285:5, 287:5, 418:1–2, 407:1**. Post 276:2/3 are next-tier browser candidates. Need logged-out actual Chrome/mobile HTTP/MIME/decoded dimensions/CDP encoded bytes and before/after screenshot, including any runtime Jetpack source changes.
- After an actual failure is established, require exact photo/crop, individual rights and photographer attribution, archived source link, 960px/no-upscale original geometry, staged derivative, and authorized editor review before any targeted WordPress Media Library upload or block edit. No default permission to mirror or download; no automatic publication.

## Reproducibility and outcome

[Machine audit](../qa/media-recovery/quebec_276_source_rights_20261102.json), [offline fail-closed validator](../qa/media-recovery/validate_quebec_276_20261102.cjs), [23 mutation tests](../qa/media-recovery/test_quebec_276_20261102.cjs). **23/23 passed in isolated V8 against exact GitHub-committed files**; native Node CI and real guest Chrome not run. Original frozen inventory identity validated six of six. 61 posts / 355 images / 288 external-origin / 13 WordPress originals >1.5 MiB. 42 reported broken unverified; 76% wire-weight reduction unmeasured; zero WordPress repairs.
