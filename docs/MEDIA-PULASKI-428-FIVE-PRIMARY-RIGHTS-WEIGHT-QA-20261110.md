# Media recovery engineering — Big Burn / Ed Pulaski, post 428 (2026-11-10)

**READ-ONLY RESEARCH / DRAFT PR #1703. NOT APPROVED FOR DEPLOYMENT, MEDIA DOWNLOAD OR WORDPRESS WRITES.** Site QA PR #154 continues to own the browser collector and six historical P0 slots. Homepage visual work remains outside scope.

## What was verified

- Fresh authenticated, **read-only** WordPress `posts_get(context=edit)`: post **428**, *The Way Out Was Underground*, `publish`, modified **2026-10-29T18:28:59**. All **five** externally sourced `<img src>` strings are exact matches to frozen 2026-10-30 `coverage_269` image slots `428:1–428:5`; five current ALT strings captured. **Historical ALT equality not demonstrated.**
- Independent web image retriever: **four exact originals displayed** (`428:2–428:5`); `428:1` returned an **Internal Error wrapper**, even though University of Idaho's specific catalog record was accessible. This **does not establish HTTP 404** from origin or guest-browser failure. A native direct `HEAD` attempt failed at isolated-runner DNS resolution. No actual response status, image bytes, `naturalWidth`, `currentSrc`, `encodedDataLength`, or page-level LCP/CLS measured.
- **Five authoritative catalog records located**, not guessed: four University of Idaho Library Special Collections entries and the 1905 Sanborn map at the Library of Congress. No source assets copied or cached.

| Slot | Exact original stored URL | Source of archival provenance | Original external retrieval | Rights summary / QA |
|---|---|---|---|---|
| 428:1 | https://objects.lib.uidaho.edu/bigburn/bigburn23.jpg | [University of Idaho Big Burn 23](https://www.lib.uidaho.edu/digital/bigburn/items/bigburn23.html): Barnard-Stockbridge, 8-B498b, Wallace burning night of Aug 20 | **Retriever Internal Error**; guest HTTP unknown | University item says public domain by publication date (PDM); verify before rehosting. Browser priority after original P0 checks. |
| 428:2 | https://objects.lib.uidaho.edu/bigburn/bigburn38.jpg | [Big Burn 38](https://www.lib.uidaho.edu/digital/bigburn/items/bigburn38.html): 8-C05b, charred Placer Creek | Displayed by retriever | Item PDM rights claim; HTML width/height = **1024×1487** (not independently decoded natural dimensions). |
| 428:3 | https://objects.lib.uidaho.edu/bigburn/bigburn10.jpg | [Big Burn 10](https://www.lib.uidaho.edu/digital/bigburn/items/bigburn10.html): 8-X90, elevated post-fire Wallace from Samuel's Hotel | Displayed | Item PDM rights claim; HTML declares **1024×823**. |
| 428:4 | https://objects.lib.uidaho.edu/bigburn/bigburn18.jpg | [Big Burn 18](https://www.lib.uidaho.edu/digital/bigburn/items/bigburn18.html): 8-X545e, Pacific Hotel ruins viewed along Hotel Street | Displayed | Item PDM rights claim; HTML declares **1024×730**. Avoid uncorroborated ALT detail about scattered machinery. |
| 428:5 | https://tile.loc.gov/image-services/iiif/service%3Agmd%3Agmd427m%3Ag4274m%3Ag4274wm%3Ag016871905%3A01687_1905-0001/full/pct%3A25/0/default.jpg | [LOC Sanborn Wallace, 1905, sheet/index](https://www.loc.gov/resource/g4274wm.g016871905/?sp=2) | Displayed | LOC states its online Sanborn collection is **public domain / free to reuse**; credit LOC Geography & Map Division. **Text- and legend-heavy sheet; do not blindly shrink.** |

### High-value visual integrity issue — the map is a two-part technical sheet

Published 428:5 shows a **1905 Sanborn index and individual color-coded buildings/street blocks** on one sheet. At small display widths, its dense building identifiers, scale and key may be illegible. The existing ALT describes it only as a generic map. Proposed ALT (editorial review only): **“1905 Sanborn map sheet for Wallace, Idaho, with the town index above detailed streets and color-coded building footprints.”** Preserve original via full-resolution accessible link/zoom; record the map edition and sheet identity. A 960px *CSS maximum* is not permission to create a lossy 960px derivative that destroys legibility.

### Rights / sizing decision gate

University of Idaho's four catalog entries designate **Public Domain Mark 1.0** based on publication date. This is the library's rights assessment, **not a separately issued commercial license**; preserve Barnard-Stockbridge attribution and contact University of Idaho Special Collections if modification/provenance is in doubt. LOC explicitly describes its online Sanborn set as free to reuse; this does not mean every later annotated derivative is the same historical work.

No image files were downloaded, so **candidate native dimensions and browser decoded dimensions are unknown**. The published HTML attributes for three JPEGs are *not* natural-file measurements. 960px **conditional width limit only**: `targetWidth = min(960, verifiedNativeWidth)`; `targetHeight = round(verifiedNativeHeight*targetWidth/verifiedNativeWidth)`. If native smaller, do not upscale. For text-rich map, preserve full resolution and reading path rather than targeting 960px blindly. Never assert original binary identity from matching filenames alone.

### Staging-only WordPress media workflow

1. Site QA #154: logged-out desktop/mobile Chrome run on all six historical P0 positions first: **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**, then **428:1**, comparing actual rendered `currentSrc`, network status, `naturalWidth/naturalHeight`, source/redirect chain, CSP/CORS and request/response sizes (including Jetpack rewrites); confirm visible error before label “broken.”
2. Preserve the published original URL and original ALT verbatim in rollback evidence, plus CMS post modified/hash. If browser confirms missing content, match primary item identity and photo scene; cite the archival catalog and exact rights rationale (and include author, repository, item ID). Do not reproduce from an unlicensed commercial intermediary.
3. With explicit future rights/production approval only, test one isolated **staging** upload with verified native pixels, <=960px non-upscaled derivative where legible, content hash/SHA-256, correct MIME, `width/height`, descriptive ALT, responsive `srcset/sizes`, and credit/source link. Compare parity at 375/768/1365px including keyboard zoom/text-label readability.
4. Use safe, targeted replacement only after manual approval and stale-post optimistic locking; **do not rewrite entire Gutenberg block trees**. Record previous and replacement attachment ID/URL/blob checksum, attribution, staging screenshot, measured transfer and rollback instructions. No production writes in this sprint.

### Image-weight evidence: do not misstate the 76% claim

Baseline: **61 published posts, 355 inline image references, 288 externally originating slots**. Separate cross-ledger `qa/media-recovery/cross_ledger_43_source_15_oversize_20261109.json` (blob `8526557c7a5138e1ca22a347e3f9839503d48b2c`) identifies **15 WordPress originals >1,500,000 bytes = 47,096,779 stored-original bytes**; five large original PNGs (media 39–43, posts 34–38) have no generated subsizes. These figures are **storage size, not transferred bytes**.

To test the historical **76%** proposed reduction, run identical logged-out, clean-profile, cold-cache captures of selected pages **before and after** on mobile and desktop with matched DPR, viewport, network profile, lazy-load scroll protocol and Jetpack settings. Sum actual completed image response encoded bytes by distinct network request and cache state, not `img` tags, CMS attachment size or HTTP `Content-Length`. Use CDP `Network.loadingFinished.encodedDataLength` plus response URL/initiator where available. When cross-origin `PerformanceResourceTiming.transferSize=0` lacks Timing-Allow-Origin, mark **unmeasurable**, never zero bytes. Report `1 - (cold_image_bytes_after / cold_image_bytes_before)`, per-page and across all 61, with confidence, request count, quality and historical identity parity, LCP/CLS and map label legibility. **No actual 76% reduction has been measured**.

`docs/IMAGE-WEIGHT-WORKLIST.md` returned GitHub 404 on both default and draft branch at the time of this review; above verified register was used instead.

## Immutable audit pointers and current status

- [Five-source primary audit](../qa/media-recovery/pulaski_428_five_ui_loc_rights_live_20261110.json), blob `76385eb1860480693e7906a1d4f5af78995ef8bb`.
- [288-position register, 274 researched, 14 pending](../qa/media-recovery/coverage_274_exact_pr1703_20261110.json), blob `24302a97a5f31037af9711da00bdf255c9184a05`.
- [Fail-closed evidence validator](../qa/media-recovery/validate_pulaski_428_five_20261110.cjs), blob `b3aa1e7e8466f41a58b24791f31b7289d92b51e2`.
- [Deterministic 33-case regression tests](../qa/media-recovery/test_pulaski_428_five_20261110.cjs), blob `c95af2729d52157c7230f4323dac5f5339222699`.
- **33/33 precommit and postcommit V8 regression checks PASSED** against committed source/JSON; native Node CI and logged-out browser checks **not performed**. No live CMS writes, media downloads, cache, homepage changes, deployment, merge or spending.

Next unresearched groups: Frank Slide post 431 (5), USS Tang post 274 (4), Honda Point post 288 (4), Great Baltimore Fire post 190 (1). They remain research tasks, **not proven broken images**.
