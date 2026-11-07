# P0 media recovery: Sunshine Skyway image origin migration (2026-11-07)

**Scope:** WordPress post 287, *The Warning Was a Man Waving*, modified 2026-11-02T21:40:01. Exact source inventory and retrieval classifications are in `skyway_287_origin_migration_20261107.json`. This is **not** Site QA's logged-out browser collector or a production update. It addresses one high-value possible broken third-party URL rather than generating speculative replacements.

## Current concrete finding

WordPress still stores image slot **287:5** as:

`https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg`

An independent `web.open` URL retrieval **reported 404 Not Found** on 2026-11-07. A visually related image with the identical filename at the **publisher's CDN host** rendered:

`https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg`

The publisher's [April 10, 2020 article](https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/) attributes the image to **University Press of Florida**. The presence of this publisher-side file is **not a grant of reuse, rehosting or further hotlinking rights**. Old/new binary equivalence is not proven because the old source did not render. The preview appears to show *Summit Venture* and wreckage of the original bridge, not the 1987 cable-stayed replacement. Existing FV ALT says “the later bridge replacement”; queue a human-verified correction, not an automatic image edit.

Other five sources in the same post rendered in the URL viewer, **but this does not prove guest-browser HTTP 200, decoded images, stable rendering or actual transfer bytes**. Four source tags lack explicit HTML dimensions and source slot 0 declares 1024×672; runtime rewriting remains unknown.

## Independently cataloged editorial fallback images (NOT equivalent)

- [Florida Memory RC09236](https://floridamemory.com/items/show/32082), May 9, 1980: black-and-white automobile near the collapse; catalog path `/fpc/reference/rc09236.jpg`. Not visually/binarily proven to match FV slot 287:3. Rights field must be individually reviewed before republication. This is the **car** scene, not an automatic replacement for slot 287:5.
- [Manatee County digital collection item 29937](https://mymanatee.contentdm.oclc.org/digital/collection/p16681coll1/id/29937): archival aerial view of damaged bridge and ship, a **different composition** from the publisher's item. Historical context suitable for an editor-selectable alternative, subject to record rights, creator/date and pixel/attribution review.
- FV's slot 287:4 already cites a [U.S. District Court / Middle District of Florida archival image](https://www.flmd.uscourts.gov/node/913); do not needlessly replace this functioning primary-hosted source.

## Guest-browser evidence and release gate

1. Coordinate with **Site QA PR #154**, which owns the existing logged-out Chrome/CDP collector, to capture the actual post and exact slot 287:5, `currentSrc`, complete redirect chain, response status, MIME, decoded natural dimensions, viewport screenshot and cold-transfer bytes. Feed its existing export through **PR #1395**; no duplicate browser collector in this PR.
2. If the browser confirms a user-visible failure, compare the original publisher photograph to the moved CDN candidate for identity/crop/quality, request or establish documented lawful reuse/attribution, and review the historically inaccurate ALT. If permission cannot be established, choose a legitimately licensed **different** archival image with a new caption and editorial sign-off; do not silently swap scenes.
3. Record master binary/hash only after approved legal acquisition, establish **actual native dimensions**, derive a ≤960px aspect-preserving preview **without upscaling**, preserve credit and original photo context, then stage WordPress media and responsive output under a separately approved release (no live post-block rewrite here).
4. Compare page-specific visitor image transfer and visual appearance before/after using same UA, DPR, viewport, fully scrolled cold cache and network profile; do not report the proposed **76%** as achieved without measurements.

## Baseline scope cautions

- Initial October 30 census: 61 posts, 355 stored inline refs; 288 offsite in Media Recovery vs 286 by Site QA #154 (classification discrepancy).
- Later census: 66 posts, 361 inline refs. These are **different dated cohorts**.
- 13 WordPress originals >1.5MiB total 43,522,829 **stored** bytes, not transferred browser weight.
- Historic report of 42 broken originals: **not proven** by guest-browser evidence.

## QA

Run `node qa/media-recovery/test_skyway_287_origin_migration_20261107.cjs` from a checkout. Offline validator deliberately fails closed on claimed guest-browser results, false 200s, rights clearance, invented 960px sizes and unauthorized WordPress publication. No network or WordPress write is performed.

**No production or homepage changes, no scraping or asset downloads/caches, no subscription spend.**
