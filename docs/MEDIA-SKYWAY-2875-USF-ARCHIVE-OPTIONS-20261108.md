# Sunshine Skyway 287:5 — ranked source and licensing recovery (2026-11-08 UTC)

## Concrete read-only result
The frozen WordPress source `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg` returned a **404 in the independent web retriever**. The publisher's `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg` rendered an image in that retriever. Both share the original filename, and the April 10, 2020 publisher article displays the latter and credits **University Press of Florida**. This is a strong *publisher relocation* candidate, not a proved exact binary match or a visitor-browser 404. No image binary was downloaded, mirrored or hashed.

**Historical integrity:** The source image shows the destroyed original Sunshine Skyway span and a ship, not the completed 1987 replacement bridge. The published ALT's “old wreckage and later bridge replacement” must not be carried forward unexamined. Suggested editorial ALT *only if the relocated photo is approved*: “Wreckage of the Sunshine Skyway Bridge following the May 9, 1980 collision.” Photo capture date not established.

## Replacement options by suitability and rights
1. **Publisher relocated file** — `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg`. Highest scene continuity and same filename, but **University Press of Florida** rights not granted; hotlinking not approved, so **no silent src substitution**.
2. **USF Libraries / George Skip Gandy IV, Gandy 21_0982**, `https://digitalcommons.usf.edu/gandy/4754/`. Dated **Jan 28, 1982**, view of damaged bridge piers beside surviving span and a passing ship. A new, relevant archive alternative but *not* the 1980 photograph. The index mentioned **CC BY 3.0**, while the retrieved catalog text did not expose a license block: require item-level confirmation before upload. Catalog lists a **10.6 MB full-resolution file**, **not visitor wire bytes**.
3. **USF Libraries / George Skip Gandy IV, Gandy 21_0950**, `https://digitalcommons.usf.edu/gandy/4724/`. Also dated **Jan 28, 1982**, catalog explicitly identifies **CC BY 3.0**, but the abstract describes a damaged bridge pier while the catalog ALT describes a vessel bow. Flag the contradictory record for visual/catalog reconciliation before any use. Catalog lists **8.5 MB original** (not FV page traffic).
4. **Florida Memory RC09236**, `https://www.floridamemory.com/items/show/32082`. Dated **May 9, 1980**, accident aftermath with car near collapsed span. Not the publisher photo, and catalog's rights are not sufficient to authorize rehosting. Rights **HOLD**.

## Machine record and tests
- `qa/media-recovery/skyway_2875_source_candidate_decision_20261108.json` — exact source and currently retrieved publisher URL, two method-labeled web-wrapper observations, four archive options, lineage/copyright/visual differences, explicitly null native pixel sizes and visitor status, and authorization flags.
- `qa/media-recovery/validate_skyway_2875_decision_20261108.cjs` — offline, fail-closed source/license/960px/no-upscale validator.
- `qa/media-recovery/test_skyway_2875_decision_20261108.cjs` — native Node regression suite with malicious/invalid evidence injections and conditional geometry checks.

## Safe release plan
Site QA #154 owns existing guest Chrome/CDP collector. Its P0 queue remains **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. Only a real full-scroll guest Chrome run can certify broken images and actual transferred bytes. If 287:5 fails, preserve full original Gutenberg markup, source URL and before screenshot; seek item-level reuse license and any required hotlink permission; visually compare historic scene/crop/date and repair ALT; for permitted media only, produce a derivative of **min(native width,960)**, preserve aspect ratio, no upscaling; verify bytes and pixels in private staging; require separate publication approval; retain one-click original URL/revision rollback and desktop/mobile after screenshot. No unlicensed image scraping/cache and no WordPress production write.

**Why not measure 76%?** Historical 61/355 and mixed-date 66/361 are source cohorts, not page-transfer audits. To substantiate a site-wide reduction, compare the same fully enumerated image slots with CDP actual encoded bytes under matching cold-cache settings, decoded pixels and browser conditions; an all-green browser image census is a prerequisite.

**Safe boundaries:** No production assets or pages touched, no new homepage work, no new crawler, no image downloads, no subscription spend. This complements #183 source ledgers and #154 Site QA rather than duplicating either.
