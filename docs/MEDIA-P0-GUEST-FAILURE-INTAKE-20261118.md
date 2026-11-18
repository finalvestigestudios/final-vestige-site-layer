# P0 guest-failure intake and image recovery handoff — 2026-11-18 04:29 PST

## Concrete new engineering work

**Separate broken-image recovery from bandwidth parity.** The existing `slot_parity_61_20261117.cjs` requires every *before* image to decode with HTTP 200; therefore it cannot intake a real **broken before** image and healthy replacement after. This is appropriate for its bandwidth/visual-parity purpose, but not for a broken-image recovery queue. The isolated `qa/media-recovery/guest_failure_intake_20261118.cjs` handles **failed, rendered or unknown** guest observations without modifying or duplicating Site QA's browser collector.

The companion machine ledger `qa/media-recovery/p0_seven_guest_failure_queue_20261118.json` holds **seven exact VIEW-derived Jetpack and original URLs** and archival provenance/rights, grounded in the Git blob `9eab2382f827e09ec1060d50c4c57135d16655b5` (six P0 priority slots) and `daf131578622af7f1e24da275d919a86d0ab6a27` (Tang). Source-original independent retriever results are **five numeric 403/404** and **two tool errors with no numeric origin status**. Tang 274:6 original returned **404** again to the public retriever on 2026-11-18; its Jetpack guest result is unknown. Attempts to retrieve the published Jetpack URLs using the public web retriever returned tool-inaccessible errors, **not** verified guest HTTP failures.

| Priority | Source slot and archival recovery lead | Recovery state |
| --- | --- | --- |
| P0 | 285:5 Three Mile Island; Wikimedia federal-photo *different frame* candidate | Exact-frame and rights HOLD; proposed 960px only, not an approved derivative |
| P0 | 285:2 TMI control panel; UCS/NRC credit source | Origin tool wrapper error, rehost rights HOLD |
| P0 | 287:5 Sunshine Skyway; publisher source and official Florida Memory accession crosswalk in prior audit (RC09236 etc.) | Publisher original 404, Florida Memory alternatives different/unconfirmed frames; rights HOLD |
| P0 | 418:1 Scotch Cap; USCG official VIRIN `210330-G-DE713-0002` | Source original 403; USCG catalog item rights/credit and exact raster HOLD |
| P0 | 418:2 Scotch Cap debris; Coast Guard Museum 600×463 preview | Source original 403; never upscale; reuse and crop HOLD |
| P0 | 407:1 Hebgen Lake; official USGS original/public-domain record, J. R. Stacy credit | Original S3 web retriever error, actual Jetpack guest state UNKNOWN; master SHA/dimensions HOLD |
| P0+ | 274:6 USS Tang; Navy NHHC accession candidate `80-G-227989` | Original publisher 404; same-pixel/crop and item rights HOLD |

## New fail-closed evidence contract

`validateQueue()` requires all seven pinned slot IDs, exact encoded Jetpack-to-origin URL identity, source result type distinctions, *unknown* guest values, unapproved rights/rehosting and ≤960px **no-upscale** proposed geometry. No upstream source-origin 403/404 automatically becomes a browser-failure claim.

`evaluate(queue,traces)` accepts optional **existing Site QA #154** logged-out Chromium observations and returns only `FAILED_NEEDS_INDEPENDENT_REVIEW`, `RENDERED_NEEDS_INDEPENDENT_REVIEW` or `UNKNOWN_NEEDS_SITEQA_CAPTURE`. Traces need post URL, original authored src, actual `currentSrc`, request/final URL and redirect chain, numeric HTTP or documented network error, decode, MIME, pixel dimensions when decoded, screenshot SHA-256, request ID, cache-disabled state and viewport/DPR. The validator rejects image swaps, 404+decoded contradictions, wrong redirect destinations, stale source identity, untracked evidence, proposed license grants and unauthorized writes.

These are self-reported trace fields, **not independently authenticated HAR evidence**. Site QA must verify that HAR, screenshots, encoded raster measurements and image pixels correspond to the same session/page revision before confirming a broken or restored image. This is a bounded intake schema, not a crawler and not a release tool.

## Performance and corpus boundaries

Historical October 30 source worklist (Git blob `9cdf7af84175883775aaebf55ffa5ca77b33e423`) covers **61 posts / 355 inline images / 288 offsite source references**. Site QA #154's earlier aggregate reported **286**, with the two-reference discrepancy limited to the subsequently changed posts 285 and 291; not a browser finding. The newer pinned WordPress VIEW census covers **66 posts / 361 inline image slots / 294 third-party-origin references**. Those two cohorts must not be conflated.

The proposed **76% visitor image-bandwidth reduction has not been measured**. Twenty originals above 1.5 million decimal bytes total **64,385,752 stored bytes**, which is **not** the sum of visitor GET transfers. The 56 over-960px Jetpack query-bound URLs across 24 posts are authored URL requests; 35 have responsive `srcset`, so actual `currentSrc` and cold transferred bytes require independent browser checks. The broken-image queue is a separate investigation and must never convert these stored/query quantities to claimed network savings.

## Safe media staging, conditional on proof and rights

Once Site QA verifies an actual visitor failure, first locate an **exact archival frame and crop** at USCG, USGS, Navy NHHC, Florida Memory or the holder's original archive. Verify item-specific copyright/reproduction restrictions, nonendorsement, photographer/credit, accession and source file hash; an authoritative repository is not blanket rehost permission. Compute a derivative at `min(960, verified master width)` with proportional height, no upscaling; preserve readability (especially maps and captions), original ALT/citation context and image identity. Record original-versus-staged binary SHA-256, metadata, attachment ID and rollback mapping. Use only a controlled, **private** WordPress media staging plan after a separate authorization; never rewrite live Gutenberg blocks or alter the homepage.

Before any approval, obtain cold logged-out desktop/mobile **before/after** image request IDs, `currentSrc`, MIME, decoded pixels, encoded raster size, unique GET transfer bytes, LCP/CLS and comparison screenshots. Recheck guest navigation and alt/caption integrity. Site QA #154 continues to own its existing browser collector; interim lead retains homepage design. **No production WordPress writes, rehosting, media downloads, merges, deployments or subscription spending are authorized by this PR.**

## Validation

The new module and its 29-test suite were executed with **native Node** locally using byte-matched files. `node --test qa/media-recovery/test_guest_failure_intake_20261118.cjs` gave **29/29 PASS**. Git blob readback confirms module `fc5a439e11653c51edfd2a75c62fbfed68516dbe`, tests `52e69a7fd8da50f25d2c2d4c882ef846fc10ecf5`. This does **not** constitute a native run of the entire repository, nor CI or real guest-browser verification.

Run the zero-trace ledger check in a native Node checkout:

```sh
node -e "const {evaluate}=require('./qa/media-recovery/guest_failure_intake_20261118.cjs'); const q=require('./qa/media-recovery/p0_seven_guest_failure_queue_20261118.json'); console.log(JSON.stringify(evaluate(q),null,2))"
node --test qa/media-recovery/test_guest_failure_intake_20261118.cjs
```

**Release state: HOLD.** The reported 42 missing images and 76% savings remain unverified, and seven priority image replacements remain rights/image-identity blocked.