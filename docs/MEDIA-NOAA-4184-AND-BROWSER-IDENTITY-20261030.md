# Media Recovery — NOAA Hilo photograph and visitor-image proof integrity

Date: 2026-10-30. Scope: 418:4 (the last previously unmatched external P0 image) and a conservative browser-probe URL-matching correction. This is an unpublished media-engineering draft, separate from Site QA PR #154 and interim homepage design. No WordPress production edits, copying, republishing, paid services or post rewrites.

## Original URL and authoritative scene identification

- Published article: https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/
- Exact stored JPEG: https://www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg
- HAWAI‘I Magazine's Nov 25, 2009 article identifies it as NOAA's 1946 Hilo Harbor Pier No. 1 wave photograph, with a person marked by an arrow: https://www.hawaiimagazine.com/three-tsunamis-that-changed-hilo-and-hawaiis-big-island/ . The linked magazine JPEG visibly rendered through the web viewer on 2026-10-30, not in Final Vestige's page browser.
- NOAA's indexed Photo Library record pl23_theb2705.jpg (Apr-46, Hilo, credit NOAA) describes the pier, inundation and man: https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg . One direct viewer attempt received 503: this does not establish a browser image outage.
- NOAA's official Hawai‘i Boater’s Hurricane and Tsunami Safety Manual reproduces the same distinctive photographic scene with arrow-marked person: https://repository.library.noaa.gov/view/noaa/41185/noaa_41185_DS3.pdf (PDF zero-based page index 36; printed page 33). Its caption credits NOAA/NGDC AND the Pacific Tsunami Museum. The PDF page was inspected as an actual screenshot; its presentation includes a wave emblem and a different crop.
- A USGS publication identifies the pier photograph and credits NOAA/EDIS: https://pubs.usgs.gov/gip/7000036/report.pdf .

Evidence tier: strong depicted-scene and source-caption correspondence, not checksum/binary identity. This closes a candidate identity gap: tiered source candidates now cover 36/36 third-party images within the 43-slot six-post P0 queue. The 36/36 does NOT mean rights-approved, browser-working, or locally repaired photographs. See qa/media-recovery/noaa_4184_20261030.json for all exact URLs and unverified fields.

Rights HOLD: NOAA and Pacific Tsunami Museum co-credits alone do not prove complete redistribution rights. Verify per-item restrictions, attribution and nonendorsement before authorizing a copy. Intrinsic image dimensions are unknown: proposed target width is min(960px, measured source width), no upscaling, preserve aspect ratio and historical 1946 credits. After approval only: file SHA-256, rights memo, optimized WebP/JPEG visual QA, WordPress new-media staging with cache headers/srcset, and a separate precise post-edit proposal. No bulk scraping or rewriting.

## Browser evidence hardening

The earlier probe correlated Gutenberg image URLs only by literal origin/path. Commons Special:Redirect/file links can instead load from upload.wikimedia.org/wikipedia/commons hash/thumbnail paths. The new imageIdentity resolver recognizes only strict Commons canonical file titles and well-formed CDN paths, rejecting spoof hosts, mismatched filenames and unrelated Wikimedia namespaces. It does not assert byte identity or image rights.

Crucially, an ALT-only match is now UNVERIFIED even when the different loaded image has nonzero naturalWidth; a duplicated stored URL cannot be mapped to one rendered DOM element twice. These close two false-success pathways while enabling the 118 stored Commons redirect URLs to be tested more meaningfully. No live-browser status has been gathered by this patch.

Native Node regression evidence: the existing twelve test cases plus fifteen new Commons/ALT/duplicate cases and seventeen independent NOAA source/rights gate cases = 44 tests. Run: node --test qa/media-recovery/test_browser_probe_core.cjs qa/media-recovery/test_browser_probe_commons.cjs qa/media-recovery/test_noaa_4184.cjs .

Release blockers remain: actual logged-out Chrome requests/currentSrc/naturalWidth/screenshots in FinalVestige.com, actual visitor transfer bytes and stable before/after mobile profile, exact original binary identity, per-item licenses, production WordPress integration and separate release authorization. Reported 42 broken images and 76% image-weight savings are still unverified. The 13 Media Library originals >1.5 MiB are ORIGINAL STORAGE BYTES, not page bytes.
