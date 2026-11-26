# Media Recovery: 56 Jetpack query-width risks — November 18, 2026, 02:28 PST

## Scope, sources, non-claims

This is an **offline, source-only audit**, not guest-browser performance evidence. Nine immutable November 17 authenticated WordPress VIEW slices contain 66 published posts and 361 inline image slots; media crosswalk identifies 20 WordPress originals larger than 1.5 MB decimal. Original 61-post worklist was read from commit f69a12cd9241ea0f39cfcb74c669bb6f7fb10357 (docs/IMAGE-WEIGHT-WORKLIST.md). Site QA draft PR #154 remains the browser-evidence owner; Media Recovery draft PR #2747 does not duplicate its collector. Interim lead owns homepage design.

The machine ledger (qa/media-recovery/jetpack_56_bound_audit_20261118.json) preserves **56 exact published img-src URLs** requesting Jetpack resize/fit width over 960 pixels across **24 posts**. Of those 56: 40 first-party originals through Jetpack; 16 third-party images through Jetpack; 35 have authored srcset and 21 lack it. There are 30 parseable resize/fit bounds at/below 960; 275 other slots have no parseable Jetpack resize/fit pair, many of them direct third-party URLs. **A query parameter is not decoded raster size**: in particular fit represents a bounding box and srcset can override img src with a different browser currentSrc.

## Highest potential impact: Malbone post 621

Published article https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/

- Slot 621:0 specifies resize=4000,3000 on media ID 1257 (4,798,395 stored original bytes); original: https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg
- Slot 621:1 specifies resize=5667,3831 on media ID 1258 (5,553,669 stored original bytes); original: https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg
- Slots 621:2 through 621:5 each request nominal 1600x1200 on infographic PNGs. Their typography may need full-res output for legibility; no blind 960px downscale.

**Both large originals have srcset/sizes and may be served much smaller in an actual browser**. The two stored originals total 10,352,064 bytes, **not** proven bytes downloaded by a visitor. Verify the selected currentSrc, decoded bytes/raster, exact image identity, browser dimensions, alt/caption fidelity, and cold mobile/desktop transfer before recommending changes.

All **11** of the 20 originals >1.5 MB that exactly match current inline img src URLs have Jetpack bounds above 960, totaling 38,480,915 stored bytes. The remaining nine originals have no exact inline img src match but could be featured images, srcset-only candidates, backgrounds, or used elsewhere. Neither cohort can be credited toward a 76% bandwidth reduction without real before/after browser evidence.

## Existing broken image queue remains ahead

The six priority suspected failures from Site QA #154 remain P0, including Three Mile Island 285:5 (encoded SayMedia source), Sunshine Skyway 287:5 (publisher origin), Scotch Cap 418:1 and 418:2 (Coast Guard origins), Hebgen Lake 407:1 (USGS origin) and Three Mile Island 285:2 (UCS publisher wrapper). An independent public retriever again observed the Skyway publisher origin as HTTP 404 on November 18; its Jetpack URL was tool-inaccessible. **Neither establishes a visitor-visible 404.** Navy USS Tang 274:6 is another source-level 404 candidate. None of the alleged 42 broken images is yet confirmed in guest Chromium.

## Browser handoff and safe remediation

Site QA, using its existing guest Chromium collector: after the six P0 slots, capture Malbone 621:0–5, Vasa 299:0/1/7, Halifax 269:1 and single-PNG posts 34–38. For each, record exact rendered currentSrc, GET/redirect HTTP status, content-type, decode, response-body SHA-256, encoded raster width/height, unique cold transferred bytes, desktop/mobile screenshots, LCP/CLS and legibility. Preserve old-source evidence to compare a staged alternative.

Do not optimize a file solely because its original WordPress media record is large. For an actual broken image, first locate *the same* archival photograph/crop in an authoritative Navy, Coast Guard, Florida Memory, USGS or comparable primary archive, with item-level rights, copyright/public-domain assessment, credit, native dimensions and SHA-256. Different frames are context alternatives, not drop-in replacements. For a rights-cleared performance optimization, target width min(960, native original width), preserve aspect/no upscale, exact caption/ALT/credit and responsive behavior. Plan WordPress **staging-only** cached media with old/new URL ID crosswalk and rollback. Explicit production release required; no bulk scraping, unlicensed mirroring, risky Gutenberg rewrites, homepage changes or paid services.

## Repeatable offline integrity tests

Node command: node --test qa/media-recovery/test_jetpack_56_bound_audit_20261118.cjs

Node command: node qa/media-recovery/validate_jetpack_56_bound_audit_20261118.cjs qa/media-recovery/jetpack_56_bound_audit_20261118.json

Validator loads nine exact Git blob SHAs and the pinned oversized-media crosswalk, independently reconstructs all 56 rows, and rejects an altered URL, wrong attachment mapping, invented guest status/bytes, fictitious rights approval, or production authorization. The source inventory is as of November 17 and does not establish the complete current site after that date. The 76% reduction and reported 42 failures remain unverified.
