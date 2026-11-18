# Media Recovery — responsive Jetpack source identity guard (2026-11-18, 03:30 PST)

## Defect and corrective change

The prior `slot_parity_61_20261117.cjs` source identity function recognized a direct image origin being transformed into an `i0.wp.com` proxy, but **rejected** a legitimate `srcset` selection when both the authored `img src` and the browser's `currentSrc` were already Jetpack URLs with different resize parameters. The old comparison incorrectly expected a second `/i0.wp.com/` segment embedded in the CDN path. This is a false HOLD, not a proven broken image: it prevents existing Site QA measurements from being accepted for many responsive images.

The corrected `qa/media-recovery/jetpack_source_identity_20261118.cjs` is a small, **offline**, fail-closed upstream identity comparator now imported into the existing historical `slot_parity_61_20261117.cjs` consumer. It resolves the original upstream host and *exact encoded path*, accepts variations only among supported Jetpack transform parameters (`resize`, `fit`, `w`, `h`, etc.), and preserves original publisher query values. It rejects changed publisher/path, unrecognized query arguments, credentials, non-HTTPS URLs, encoded-path deviations and repeated parameters. It does **not** change the existing decoded-raster, no-upscale, network-byte, SHA-256, visual-parity and missing-image gates.

[Machine-readable five-slot source ledger](../qa/media-recovery/responsive_identity_5slot_evidence_20261118.json) pins exact historical URLs for Malbone Street 621:0 and 621:1, Three Mile Island 285:5, Scotch Cap 418:1 and USS Tang 274:6. Hypothetical `?w=960` test variants are explicitly **synthetic**: no browser's `currentSrc` has been observed in this sprint. On **2026-11-18**, an independent public web retriever returned HTTP **404** for the exact USS Tang 274:6 original publisher URL. The Jetpack guest response is **unknown**. Prior 285:5 HTTP 404 and 418:1 HTTP 403 observations are source-reader results, not guest-browser proof.

## Relevance to overall image worklist

The immutable November 17 inventory included **66 published posts / 361 inline slots**. The query-width audit flagged **56 `img src` URLs** over a nominal 960px Jetpack bound, across **24 posts**; **35 of 56 have `srcset`**. They are *potential* misclassification cases when the selected browser URL differs, not 35 confirmed false negatives or failures. Malbone's two large originals are **4,798,395** and **5,553,669 stored bytes**, not measured visitor transfers. The 20 WordPress originals over 1.5 million decimal bytes total **64,385,752 stored bytes**. The former 61-post worklist was reviewed at commit `f69a12cd9241ea0f39cfcb74c669bb6f7fb10357`; it is no longer present on current `main`.

The **42 reported broken external-source images** remain unverified in logged-out Chromium. The asserted **76% visitor image-bandwidth reduction** remains unmeasured and must not be reported as achieved. A source URL returning 404, 403, a retriever timeout, or a successful archival catalog page is never a substitute for the *actual delivered Jetpack/currentSrc HTTP response* and decode.

## Site QA #154 handoff — no duplicate collector

Continue using Site QA's existing browser collection, not a new crawler. Prioritize six P0 suspected broken images **285:5, 285:2, 287:5, 418:1, 418:2, 407:1** and Tang **274:6**. For responsive first-party performance, measure **621:0–5** next: obtain currentSrc, final numeric GET status/redirect chain, MIME and decode, response-body SHA-256, **encoded** width/height (not density-corrected `naturalWidth`), exact cold unique image transfer bytes, screenshots, text/infographic legibility, viewport/DPR and LCP/CLS at equal test conditions. Treat source index and exact post revision as frozen. The new matching code is only an intake gate for Site QA evidence, **not** an independent verification of the browser trace.

For an actual failed image, seek **the same original archival photograph/crop**, not a merely similar scene. Current candidate crosswalks include official [USCG Scotch Cap portrait](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/), [USGS Hebgen Lake catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959), [Florida Memory collections](https://floridamemory.com/), and the [Navy NHHC image catalog](https://www.history.navy.mil/our-collections/photography.html). Exact accessions, rights/copyright, source credit, binary identity and crop, native width/height and SHA-256 must be checked *per asset*; an official source does not automatically authorize every copy. No unlicensed source scraping or image mirroring.

## Conditional WordPress cache / rollback acceptance

Only after independent failure or actual transfer evidence and item-specific reproduction rights: download one expressly authorized master into a controlled staging workspace; record canonical catalog URL, accession, copyright/license/credit, SHA-256, original and cropped geometry. Prepare a derivative **width = min(960, verified native width)** with proportional height, no upscaling; preserve historical caption/ALT, license credits, readability and responsive output. A 600px archive preview remains 600px. Stage the new attachment privately with an old/new URL-ID mapping, preserve the original article and its revision for a reversible rollback, compare identical guest-device cold traces/screenshots, and request a separate release approval. Do **not** make risky Gutenberg block rewrites or any production WordPress writes.

## Verification

Run in a native Node environment:

```sh
node --test qa/media-recovery/test_jetpack_source_identity_20261118.cjs
node --test qa/media-recovery/test_slot_parity_61_20261117.cjs
```

The first 24 tests **passed with native Node 22.16.0 against an exact byte-matched copy of the committed helper/test source**. The second historical suite and full repository CI have **not run** in this sprint; they must remain release gates. The existing Site QA collector, homepage design and production WordPress remain untouched. Draft PR #2747 stays HOLD/unmerged/undeployed, zero downloads, media rehosting, subscription spend or live changes.
