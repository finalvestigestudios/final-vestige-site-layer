# Final Vestige media: Forrestal post 289 — source identity and coverage, 2026-11-10

**Draft, evidence-only. No deployment, WordPress edits, homepage design, image mirroring or purchases.**

All six originally published URLs and ALT text were joined exactly against the October 30 frozen inventory (61 articles, 355 inline slots, 288 external-origin slots). Five original image URLs rendered in an independent image retrieval service; one, the media.defense.gov training photograph, returned a *retriever* 403. None are legitimate guest Chrome HTTP/decode results, therefore neither failures nor successes are claimed for website visitors.

| Slot | Retrieval-only observation | Source identification | Maximum width result | Release |
|---|---|---|---|---|
|289:0|Rendered|[Commons A-4 fire](https://commons.wikimedia.org/wiki/File:USS_Forrestal_A-4_Skyhawk_burning.png), unknown author/USGov PD assertion|960x763|HOLD|
|289:1|Rendered|Forbes-hosted 1967 fire photo; [Navy USN 1124794](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/usn/USN-1120000/USN-1124794.html) is a DIFFERENT image alternative|Native pixels unknown|HOLD|
|289:2|Rendered|Sina-hosted elevated aft-deck image, exact Navy accession unknown|Native pixels unknown|HOLD|
|289:3|Rendered|Chinese-hosted monochrome hose/debris scene, may overlap #289:1 but identity unproved|Native pixels unknown|HOLD|
|289:4|Retriever 403 ONLY|[DVIDS 6947585](https://www.dvidshub.net/image/6947585/farrier-firefighting-school), 2021-08-11 Navy training, J. Keith Wilson|960x639|HOLD|
|289:5|Rendered|[DVIDS 985674](https://www.dvidshub.net/image/985674/uss-forrestal-memorial-ceremony), 2013-07-26 Paul Anderson memorial portrait, David Todd|960x1446|HOLD|

Three historical integrity boundaries: 2021 training and 2013 memorial images must not be described as 1967 fire photographs; Navy archive USN 1124794 is an editorial alternative only, not proven pixel-identical to the Forbes/China photos; Commons PD label for an unknown author does not independently prove federal employment. DVIDS marks its two Navy items public domain while referring readers to its copyright guidance; review individual attribution and use conditions before any caching/rehosting.

Updated frozen external inventory: **181 researched, 107 still pending, 186 source-evidence records, 288 total**. Six new records, no other 282 rows changed. Historical 42 purported broken images remain guest-unverified. Claimed 76% image-wire saving remains unmeasured; 15 WordPress originals over 1,500,000 bytes total 47,096,779 stored-original bytes, not user-transfer bytes.

**Conditional caching and WordPress plan, not authorized:** Site QA first runs its existing browser collector on P0 slots 285:5, 285:2, 287:5, 418:1, 418:2, 407:1, then six post-289 sources. Preserve full image network URLs/currentSrc and uncached cold load/decode. For a confirmed visual failure, secure item reuse rights plus approved exact scene/crop, hash a permitted archive binary, stage 960px-wide max/no-upscale quality reviewed derivative (do not force 960px height on portrait), carry photographer/credit, then obtain editorial approval for a reversible per-block WordPress change with before/after screenshots. No automated Gutenberg rewrites or mirroring. Prove weight changes only with equivalent cold-cache same-photo transfer totals.

Source pins: frozen part 03 blob 49183f66f880f7c4dfd363acca906876877f2e5e; prior 175 register blob ef3c35dcbfc2834d8b7547e5a72a0625428a259e; six-source audit blob a12e3b9ce0aab87c17cc7525c86d1482cb0d62f8. Site QA #154 owns visitor-browser testing and has not been modified.

## Native test fixture custody

This branch deliberately does not duplicate PR #183's full `parts/03.json` inventory. Instead `qa/media-recovery/forrestal_289_exact_source_fixture_20261110.json` contains the six literal unchanged post-289 rows copied from that frozen inventory, with its exact upstream Git blob `49183f66f880f7c4dfd363acca906876877f2e5e`. Validator CLI and test suite read the local six-row fixture, so native Node tests do not depend on a file absent from PR #1703. No changes to PR #183 or Site QA #154.
