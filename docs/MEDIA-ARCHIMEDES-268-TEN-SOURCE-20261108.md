# Archimedes Palimpsest post #268 — ten-image rights and visual-integrity recovery (2026-11-08)

**Scope and truthfulness:** On October 30 the authenticated source census captured **10/10 offsite image sources** for post #268 in `qa/media-recovery/parts/04.json` (Git blob `6df3251e5a67a971d87a516a1ba4a0cc32f51f96`). This run did **not** re-read WordPress and cannot assert current publication state. On November 8 the independent web retriever failed to show all ten exact binaries (six Commons redirect tool-inaccessible results, three official project JPEG wrapper 403 results, one project JPEG tool-inaccessible). These are **retriever wrapper outcomes, not visitor HTTP**. Every actual HTTP, currentSrc, transfer-byte and natural decoded-image field remains null. The original reported 42 broken images and 76% site-wide savings remain unproven.

## New high-value licensing distinction

The official Archimedes Palimpsest **Image Bank** says its scholarly image datasets are **CC BY 3.0 Unported**: https://archimedespalimpsest.org/digital/image-bank.php . Five *specific* Commons folio images here, however, have Flickr-reviewed **CC BY 2.0** statements on their Commons file pages, while some of their embedded project metadata says **CC BY 3.0** and/or mentions copyright retained by the private manuscript owner. This is an attribution/source-custody reconciliation, **not blanket PD**. Capture exact work, author, link, license, attribution, changes and any rights restrictions before localizing. The four static narrative images on the project's `/assets/img/` path are **not necessarily part of that Image Bank license**; retain full rights HOLD.

Commons original page records:
- 268:0 https://commons.wikimedia.org/wiki/File:Archimedes_Palimpsest.jpg — US-public-domain claim, **665×448** original. Existing `width=1280` query exceeds native width. Do not upscale; conditional **665×448**.
- 268:2 https://commons.wikimedia.org/wiki/File:002r-001v_Arch13r_Sinar_uvblue_norm8_Euchologion_up_(9737603804).jpg — CC BY 2.0 display, 10,880×8,160; conditional **960×720**.
- 268:3 https://commons.wikimedia.org/wiki/File:017r-016v_Heiberg-UV-blue_(9737623542).jpg — CC BY 2.0 display, 2,040×2,720; conditional **960×1,280**.
- 268:5 https://commons.wikimedia.org/wiki/File:017r-016v_Arch07r_Sinar_pseudo_no-veil_(9734386225).jpg — CC BY 2.0 display, 8,160×10,880; conditional **960×1,280**.
- 268:6 https://commons.wikimedia.org/wiki/File:028v-021r_Arch08r_XRF_FeFront_registered_(9734104759).jpg — CC BY 2.0 display, 8,160×10,880; conditional **960×1,280**. Existing source requests `width=1280`; no source/image changes approved.
- 268:9 https://commons.wikimedia.org/wiki/File:176r-173v_Hype03r_Sinar_LED445-735_pseudo_(9734660151).jpg — CC BY 2.0 display, 6,600×9,500; conditional **960×1,382**.

The remaining four project-hosted images (268:1, :4, :7, :8) have unknown intrinsic dimensions and per-file reuse rights. Their primary project context is https://www.archimedespalimpsest.org/about/imaging/capture.php . Document exact image-file custody, rights, crop/scene content, captions and width before any derivative. Preserve technical differences between UV, XRF iron maps and Hyperides folios; these images cannot be interchanged merely because they look similar.

## Safe implementation and acceptance sequence

1. Site QA #154 owns existing logged-out Chrome full-scroll collector. Check six original P0 slots **285:5, 285:2, 287:5, 418:1, 418:2, 407:1** first. Then examine 268's ten sources, recording exact source and browser `currentSrc`, redirect chain, final status/MIME, uncached requestId encoded bytes, natural dimensions, screenshots, and alt/visual identity on desktop + mobile.
2. For each *genuinely* broken image, choose identical-item original from the catalog, not a different folio or spectrum. Require completed attribution and editorial rights approval, binary hash, image/crop review. Conditional candidate <=960px preserving aspect ratio with no upscaling; text/diagram legibility must survive at mobile width. Do not automate downloads or cache sources until each is cleared.
3. If later approved, create independent locally cached WordPress Media image(s), record both original and derived SHA-256, exact catalog/credit and rollback reference, stage in separate tiny code/media change, and compare before/after cold CDP transfer. Avoid Gutenberg block rewrites, metadata loss, lost captions, or site theme/homepage changes. **No production writes are authorized this sprint.**

This clean offline audit neither duplicates Site QA's collector nor changes its draft #154, nor duplicates the P0 #1655 or Palomares #1683 candidate ledgers. All rights/rehost flags remain false. No binary downloads, no scraping, no WordPress writes, no paid services.
