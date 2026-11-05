# P0 external-image browser disposition gate — Nov 4 PST / Nov 5 UTC (source only)

**Scope:** Media Recovery draft PR #183 only. No homepage visual design, Site QA #154 scripts, WordPress production post/media write, third-party image download/cache, unlicensed use, or subscription cost.

## What changed

- `qa/media-recovery/adjudicate_p0_guest_evidence_v1.cjs` is a **read-only adjudicator** for the existing Site QA-compatible Chromium CDP probe output, not another browser probe. It merges the two already-pinned P0 source ledgers and requires each of six exact WordPress image URLs to agree with that published source record.
- It uses the existing `browser_probe_core.cjs` and `image_census_coverage_core.cjs` identity checks. A label of **BROWSER_CONFIRMED_BROKEN** needs a verified, fully scrolled `finalvestige.com` article, an exact stored/currentSrc image identity, a true zero-pixel decode, the correct Chrome Image request ID, and an independent matching final request error/status/MIME. **BROWSER_VERIFIED_LOADED** needs image decoding, final URL identity, 200 image response, fresh CDP encoded bytes and all three cache flags explicitly false. Missing, duplicate, partial-page, redirect-ambiguous, cached, or contradictory evidence yields **PENDING_GUEST_BROWSER**.
- The output never approves replacement, caching, copyright clearance or WordPress writes. Even a broken image with screenshot evidence remains **rights_release:HOLD**. An external web retriever wrapper 400/403/404/500 **is not a browser or publisher-origin HTTP result**.
- `qa/media-recovery/p0_guest_browser_disposition_pending_20261105.json` is an auditable six-URL static snapshot. **All six visitor statuses and encoded byte counts are NULL, and the full six-slot browser census is incomplete.** Its wrapper observations were inherited from prior source ledgers, not freshly measured.

## Six priority positions and exact published original URLs

| Slot | Article | Original URL | Old retriever wrapper | Verified visitor status |
|---|---:|---|---:|---|
| 285:5 | Three Mile Island | `https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg` | 404 | NULL |
| 285:2 | Three Mile Island | `https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg` | 500 | NULL |
| 287:5 | Sunshine Skyway | `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg` | 404 | NULL |
| 418:1 | Scotch Cap | `https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG` | 403 | NULL |
| 418:2 | Scotch Cap | `https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg` | 403 | NULL |
| 407:1 | Hebgen Lake | `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg` | 400 | NULL |

These are the six previously published URLs, **not new download attempts**. Source ledger blob SHA-1s are stored in the static JSON. Other images in the 61-article/355-reference baseline are not silently counted as verified.

## Candidate and rights gates

- **285:5:** Commons 819×614 Three Mile Island scene is a *different-angle, unverified* substitute for the aerial-caption slot. Do not publish under the current ALT without exact historical comparison and reuse confirmation; never enlarge to 960.
- **285:2:** NARA 540034 is an alternate control-room photograph, **not** an exact rendering of the UCS panel; diagram/content equivalence is unproven. Conditional proportional 960×647 if selected with fresh editorial approval.
- **287:5:** Florida Memory item 131903 (H. Milo Stewart, 1987) depicts the old and new Skyway, but is not a proven same-photo replacement. The secondary Commons rendition is 600×595; no upscaling. Primary reproduction terms **HOLD**.
- **418:1:** Official USCG image identifier 2002905913 / VIRIN 210330-G-DE713-0002.JPG is a historical portrait, not storm debris. Catalog calls it public domain/cleared for release with attribution/DoD caveats; master pixels and exact binary not yet verified.
- **418:2:** USCG Scotch Cap debris source filename is identified, but exact original image accession, dimensions and rehosting terms remain **HOLD**.
- **407:1:** USGS 1959 Hebgen fault-scarp archive identifies a relevant source; actual original binary, pixel dimensions and rights need item-level inspection. Do not treat an octet-stream retriever error as browser failure.

**All candidate derivatives:** min(960, original verified intrinsic width) pixels, aspect ratio preserved, no upscaling; original checksum, accession/source URL, creator, publication credit, contextual ALT and permission recorded before *offline staging*. Before any future WordPress media upload or post edit, require explicit release authorization and a reversible original-to-new-media mapping; keep rollback URL, original markup, and prior screenshot. No automatic post-block rewrite.

## Running the existing verification workflow

1. In a network-enabled, logged-out Chromium environment, run the **existing** `node qa/media-recovery/browser_probe_chrome.cjs`, then `--desktop`; preserve the unmodified emitted JSON and screenshots. Do not add a competing site crawler or modify Site QA #154's draft.
2. Run `node qa/media-recovery/adjudicate_p0_guest_evidence_v1.cjs` with **no argument** to print the provisional six-source/pending report; feed an existing probe JSON as its single argument for independent browser adjudication. A partial probe intentionally exits nonzero.
3. Prioritize a true broken source, matching original archival item and copyright permissions first. Only after a rights-cleared replacement is staged and manually previewed should an authorized publisher make a reversible CMS change. Verify no-JS/mobile/desktop legibility, image decoding, credits, and cold browser network results.
4. Use the *separate existing* `compare_cold_image_wire_v1.cjs` for **before/after fully loaded** images; it must not misclassify a broken baseline as 0 transferred bytes and invent a 76% saving. Baseline 61 articles/355 slots, 288 external origin references, 13 WP originals >1.5 MiB = 43,522,829 **stored** bytes, and five 1672×941 PNGs = 13,267,538 **stored** bytes; none proves visitor transfer.

## Checks and limits

Committed source blob: `cdc68df6fcc9e7c72e340cad935ec75de831fa52`. Committed test blob: `3fb4db0d3d3dc83255b6ef629cd80c8436a8c333`. **22/22** native local Node tests passed against those exact changed code/test blobs using compatibility shims for two pre-existing helpers. **22/22** isolated V8 test cases also passed with the *actual GitHub-fetched* existing identity and census helper modules (URL polyfill for the isolated environment). Native Node full-repository integration/CI and genuine Chromium networking remain outstanding. No real browser break/fix or 76% transfer reduction has been measured in this run.

**Ownership handoff:** Site QA #154 still owns real browser/screenshot evidence. Media Recovery #183 owns archival/rights proof, performance acceptance, and safe release-gate engineering. Interim lead owns homepage design.