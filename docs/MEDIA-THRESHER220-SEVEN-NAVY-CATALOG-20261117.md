# Thresher 220: complete seven-slot Navy archival custody audit

**November 17, 2026, 12:26 PT. Read-only, isolated P1.** No homepage-design changes. The exact seven historical post-220 image URLs were retrieved from the pinned WordPress authored-source snapshot `qa/media-recovery/parts/05.json`, commit `4366489a68620d26592d8438b4402feb453c3166`, Git blob `9b16b828342a9ac338f3e65610fd3d8d508355e9`. Its post revision is October 29, 2026 18:25:46. The live guest page was inaccessible to independent reader, so this is **not** a fresh WordPress or guest-browser census.

All **seven exact authored Commons Special:Redirect/image URLs** were inaccessible to the public retriever without a numerical origin HTTP result, but **all seven corresponding Commons file-description HTML catalogs loaded**. This is **not seven confirmed broken visitor images**. No guest `currentSrc`, request status/MIME, decoded pixels, screenshot, or CDP encoded wire bytes is available. Neither a no-access web tool result nor Commons HTML availability proves the live image itself is working/broken.

## Source / candidate matrix

| Slot | NHHC official identifier | Commons catalog native geometry | Conservative ≤960px *long-side* treatment |
|---|---|---|---|
| 220:0 | NH 97545 | [4918×6136](https://commons.wikimedia.org/wiki/File:USS_Thresher_(SSN-593)_bow.jpg) | 769×960 |
| 220:1 | NH 97552 | [740×574](https://commons.wikimedia.org/wiki/File:USS_Thresher_(SSN-593)_launching.jpg) | 740×574 |
| 220:2 | NH 97310 | [578×737](https://commons.wikimedia.org/wiki/File:USS_Skylark_(ASR-20).jpg) | 578×737 |
| 220:3 | NH 97567 | [740×532](https://commons.wikimedia.org/wiki/File:USS_Thresher_(SSN-593)_watertight_door.jpg) | 740×532 |
| 220:4 | unverified | [1700×1349](https://commons.wikimedia.org/wiki/File:Bathyscaphe_Trieste2_2.jpg) | 960×762 |
| 220:5 | NH 97570 | [739×574](https://commons.wikimedia.org/wiki/File:USS_Thresher_(SSN-593)_brass_pipe.jpg) | 739×574 |
| 220:6 | NH 97557 | [740×576](https://commons.wikimedia.org/wiki/File:USS_Thresher_(SSN-593)_rudder_sunk.jpg) | 740×576 |

Exact authored redirects, Commons catalog URLs, credited NHHC historical catalog URLs, catalog native dimensions and source status are in [the JSON manifest](../qa/media-recovery/thresher220_navy_seven_catalog_20261117_1226pt.json). Six Navy accessions established: **NH 97545, NH 97552, NH 97310, NH 97567, NH 97570, NH 97557**. The remaining **Trieste II** (slot 220:4) is described on Commons as a **mid-1964** configuration sourced via NavSource, with U.S. Navy attribution but **no verified official Navy accession**. Do not substitute a January-1964 Trieste II photo or imply binary/frame identity.

All seven Commons descriptions claim public-domain U.S. Navy government-work status, **not blanket authorization to download or rehost without reviewing individual record/source context**. Two important geometry findings: the 4,918×6,136 bow photo produces **769×960** under a strict long-edge limit, not a 960×1,198 over-height derivative; the 1,700×1,349 Trieste II photo produces **960×762**. Five other native Commons scans are already smaller than 960px on both axes, so **do not upscale**. Numbers reflect catalog metadata only, not generated images or actual browser transfers.

## Reversible WordPress media plan (NOT execution)

Retain Site QA #154 as sole logged-out Chromium owner. After its six higher-priority P0 slots, cold-visit the Thresher article on desktop/mobile, scroll lazy images, record authored URL versus `currentSrc`, redirect/final image response status and MIME, decode/natural pixels, unique request-ID encoded bytes, and viewport screenshots. If any image truly fails, first confirm same picture/crop and per-item rights + attribution, source checksum, and native dimensions. Only then prepare an approved WordPress Media Library staged replacement with original/source URL backup, a ≤960px long-edge no-upscale file, accurate `width/height/srcset/sizes`, editorial ALT/credit, screenshot parity and tested rollback. Avoid Gutenberg block mass rewrites. If images already work, measure actual wire bytes before considering optimization. No production writes or media downloads permitted in this batch.

Historical 61 posts/355 authored image refs are a different cohort than the later 66 published WordPress posts; 42 reported failures remain visitor-browser unconfirmed; the 76% reduction is not measured; the 20 >1.5 MB originals total 64,385,752 **stored** bytes, not actual transmitted bytes.

## Offline QA

`node --test qa/media-recovery/test_thresher220_navy.cjs`
`node qa/media-recovery/validate_thresher220_navy.cjs qa/media-recovery/thresher220_navy_seven_catalog_20261117_1226pt.json`

Tested 27 cases in isolated V8; native Node and repo CI must verify the committed files before merge. The validator fails closed on missing/changed source slots, fabricated HTTP successes/failures, unsupported rights, invented accession, wrong 960px geometry or unauthorized writes/spend.
