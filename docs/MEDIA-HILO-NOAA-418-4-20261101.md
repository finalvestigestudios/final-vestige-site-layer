# Post 418:4 — NOAA archival ID recovered for final 1946 tsunami P0 provenance gap

**Date:** 2026-11-01. **Isolation:** draft Media Recovery PR #183. No WordPress, images, homepage, subscriptions or QA PR #154 code altered.

## New identity evidence

Post [418](https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/) stores image **418:4** as `https://www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg` and ALT “Tsunami water inundating the Hilo waterfront in April 1946, with a person visible near the advancing water.”

The publisher's [2009 article](https://www.hawaiimagazine.com/three-tsunamis-that-changed-hilo-and-hawaiis-big-island/) links this exact photograph, renders through an independent image viewer, and describes the wave cresting over **Pier 1 in Hilo Harbor**, with an arrow pointing to a man. That URL is NOT confirmed as an image loading in a guest browser.

A new official NOAA catalog lead is [Historic Coast & Geodetic Survey image **theb2705** / **pl23_theb2705.jpg**](https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg), credited **NOAA**, dated **April 1946**, description **“Tsunami inundating Hilo, Hawaii. Note man on pier”**. The indexed catalog advertises a **265 KB download**, NOT a measured article transfer or original file hash. The official catalog web-retriever failed with 503 (load balancer) and 405 (www host) on direct open; these are **retriever-wrapper responses**, not proof of origin failure.

The [University of Washington 1946 photo index](https://earthweb.ess.washington.edu/tsunami/general/historic/images_46.html) independently describes the same **Pier No. 1 / arrow / man** photo and credits **NOAA/EDIS** via the former National Geophysical Data Center; its account identifies the ship **SS Brigham Victory** as the vantage point. This is **strong source-scene evidence**, not an exact pixel/binary/crop hash match. The catalog accession closes the last *context-only* official-record lead in the 36-image P0 candidate inventory, taking it from **35/36 to 36/36 source-candidate leads**—not 36 working images, not 36 rights-cleared files.

## Rights and safe recovery

[NOAA's reuse guidance](https://oceanservice.noaa.gov/about/faq.html) states that NOAA-origin imagery is generally public domain absent contrary credit; source credit, no implied government endorsement and third-party/photo-of-identifiable-person checks remain applicable. HAWAIʻI Magazine hosting/credit alone is not license evidence. Historic C&GS provenance supports further item-level review, **but rights clearance and production caching remain HOLD** until the exact master binary, catalog restrictions and any recognizable-person/publicity concerns are verified. Never copy the magazine's image simply because a NOAA version may exist.

The conditional conversion rule is **width=min(960, verified original width)**, preserve aspect ratio, no upscaling or content-altering crop, then appropriate first-party WordPress Media Library metadata/credit and responsive variants *only with separate publication authorization*. No source pixels, dimensions or performance bytes were invented, no image binary downloaded.

## Evidence acceptance / coordination

1. Site QA #154 owns logged-out browser acceptance: actual post 418:4 currentSrc, final network URL, HTTP/MIME, naturalWidth, cache state, transfer bytes, exact-element screenshot.
2. Media Recovery owns catalog/pixel-hash/rights comparison and future cache proposal; no duplicate Site QA scripts or branch edits.
3. Browser source-status 42 and claimed image-transfer 76% still unverified; the frozen 61-post / 355-image / 288-external / 13-oversized-original inventory remains unchanged.

Machine-readable source facts: `qa/media-recovery/hilo_noaa_theb2705_418_4_20261101.json`. Fail-closed validator and 19 `node:test` cases: `validate_hilo_noaa_418_4.cjs`, `test_hilo_noaa_418_4.cjs`. Those tests must be executed natively and re-read from GitHub before any merge.
