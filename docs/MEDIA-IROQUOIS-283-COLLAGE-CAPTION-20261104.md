# Iroquois Theatre post 283 — image custody and historical integrity (2026-11-04)

**Scope:** Media Recovery PR #183; Site QA PR #154 keeps guest-browser checks. NO WordPress production writes, image downloads, homepage design or subscriptions.

## Actual evidence
Authenticated read-only WordPress posts.get(context=edit) confirms post 283 is published, modified 2026-11-02T21:39:57, and its seven image URLs and seven ALT strings match the October 30 frozen qa/media-recovery/parts/03.json (Git blob 49183f66f880f7c4dfd363acca906876877f2e5e). All seven img tags omit both width and height (a potential CLS issue, NOT measured CLS). Seven images refer to seven distinct original hosts. The independent image retriever displayed six exact sources, but was unable to display 283:3 EnidNews CDN; no numeric origin HTTP, guest-browser status, MIME, decode, currentSrc, transfer bytes or intrinsic pixels were captured. Do not call 283:3 a browser 404.

## Critical historical-image and caption findings
- 283:0: Original [Fire Escape Doors Portrait Mode](https://2.bp.blogspot.com/-vFf9zOG42QU/W2shS055U-I/AAAAAAAACc0/uHswGJB19E4OgUANkDatBX7LSCIEswfZgCLcBGAs/s1600/Fire%2BEscape%2BDoors%2BPortrait%2BMode.jpg) is visibly a MODERN annotated collage/diagram with arrows, text and stick figures plus several archival photo insets; the article opening sentence calls it 'a photograph of one of the exits after the fire', and the ALT implies an unmodified archival photograph. This is a concrete visual-trust mismatch. Seek editorial correction, not an automatic image swap. [Knox College / DPLA / Allen A. Green real historical exit photo](https://commons.wikimedia.org/wiki/File:Iroquois_Theatre_fire_-_DPLA_-_c9e2f3b69954059bcfebf35bf12d84b9.jpg) is a DIFFERENT picture.
- 283:2: Foyer composition corresponds to CHM ICHi-36010 via [Northwestern](https://florencekelley.northwestern.edu/historical/iroquois), identified as Nov 23, 1903 dedication souvenir; visually an accompanying version contains Dec 30 1903 caption. Preserve the contradiction for editorial review. [Tacoma Times Jan 5, 1904 edition](https://commons.wikimedia.org/wiki/File:Foyer_of_the_Iroquois_Theatre_(Chicago,_1903)_(hi-res).jpg) is the same composition, NOT identical-binary proof.
- 283:3: Original TownNews photo inaccessible to image retriever, no origin HTTP code. Northwestern CHM ICHi-36007 ruined interior is a related subject only, not exact replacement.
- 283:5: Published MinuteMedia crop depicts main exit from first balcony. [Larger Commons version](https://commons.wikimedia.org/wiki/File:Chicago-iroquois-theater-fire-05-main-exit-from-first-balcony-where-occurred-the-greatest-loss-of-life.jpg) has different framing and CC BY-SA 4.0 listing; item rights and photographer/credit still require inspection.
- 283:6: Exact Northwestern published theater exterior image is CHM ICHi-36009 / Charles R. Clark, but its original archive catalog does not prove the published ALT's 'after the fire' timestamp.
- 283:1 and 283:4: Medium exterior and WTTW original display in text retriever; neither display grants rights to copy/rehost. [WTTW context](https://www.wttw.com/chicago-stories/downtown-disasters/the-tragedy-of-the-iroquois-theater-fire).

## Candidate 960px no-upscale specifications
| Slot | Archival candidate | Catalog original px | Conditional derivative max | Hold |
|---|---|---:|---:|---|
| 283:0 | Knox College / DPLA Allen A. Green historical exit **different photo** | 4118 × 5221 | 960 × 1217 | Commons US PD signal, exact asset/credit review |
| 283:2 | Tacoma Times Jan 1904 foyer artwork **different rendition** | 1920 × 1192 | 960 × 596 | Commons US PD signal, composition/crop review |
| 283:5 | Commons first balcony exit **different crop** | 1181 × 888 | 960 × 722 | CC BY-SA 4.0 listed; underlying work attribution/conditions review |

Candidate dimensions come from catalog pages, NOT decoded production JPEGs. Never enlarge smaller source images; other heights remain unknown.

## Release hold and coordination
Site QA #154 keeps P0 guest-browser source checks 285:5/2, 287:5, 418:1/2, 407:1. Treat 283:3 as P1 browser check, and separately route 283:0 modern-composite miscaption to editorial QA. Require exact actual Image GET status, final host/redirects, mime, currentSrc, decoded natural dimensions, screenshot and CDP transferred bytes. Before any WordPress media/local cache: verify archival identity, item rights, historical caption/ALT, credit, no-upscale max-960 dimensions, stage with immutable asset manifest and screenshots, post diff, rollback, separate approval. No Gutenberg block rewrites based on isolated renderer output.

**Artifacts and tests:** [Seven-image machine-readable ledger](../qa/media-recovery/iroquois_283_visual_custody_20261104.json) commit 96631e6b5ecac8e1607cd015f69b8542a8b9233c; [fail-closed validator](../qa/media-recovery/validate_iroquois_283_20261104.cjs) commit 2af8c15041ba241b3b19cea3230eec374aebec46; [adversarial tests](../qa/media-recovery/test_iroquois_283_20261104.cjs) commit f6be27fa5adb79f238912ef3d3ee124327b4ac53. 40/40 assertions passed on exact committed files in isolated V8 CommonJS compatibility runner; native Node CI and guest browser pending. Source census 61/355/288/13; alleged 42 broken UNVERIFIED, 76% transfer savings UNMEASURED; 0 repairs, WP writes, media copies or spend.
