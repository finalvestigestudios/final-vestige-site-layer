# CDP media weight integrity: resource-type spoof and cross-post profile mixing (2026-11-03)

## Finding and safety objective

Media Recovery PR #183's `evaluate_image_wire_20261103.cjs` could previously count a record that asserted HTTP 200, `image/*` and decoded pixels **without asserting it came from a CDP Image request**. A Fetch/XHR of an image-looking URL is not evidence that the historical article <img> loaded. Separately, 61 article pairs could be captured at different viewport/network profiles; before and after conditions were compared within an article, but not across all articles. Both are **synthetic reproducibility flaws**, not findings of broken live FinalVestige images.

The isolated fix requires each supplied request to identify `resource_type: "Image"` and rejects records of other or unknown CDP types. It also compares the complete browser `conditions` object across the entire multi-post cohort (browser, version, viewport, scale, network profile, cache mode and locale), rather than only within individual posts. Mixed mobile and desktop captures should be evaluated as **separate complete cohorts**, not combined into one site-wide savings percentage.

## Verification

The existing synthetic regression runner plus three new adversarial mutations completed **33/33 isolated V8 CommonJS-shim assertions**. The new cases explicitly show that a Fetch/missing resource-type record and a 61-post aggregate whose second article alone uses 1920px (both before and after) return `INSUFFICIENT_DATA`. No real browser/network measurement was taken. Native Node and real guest Chrome CI remain **pending**, and no new claim that 76% was saved can be made.

Source commit `ab30956f3a800dafdf438f3d529c5c8b3d309f4d`; regression commit `18185241b67068225f1cab85aa9c8c8848cc61a9`. Machine record: [`qa/media-recovery/cdp_cohort_type_integrity_20261103.json`](../qa/media-recovery/cdp_cohort_type_integrity_20261103.json).

## CDP collector and staging contract

For each recorded network request, preserve its browser-assigned `request_id`, `resource_type` from `Network.responseReceived.type` (must be `Image`), request and final URLs, terminal HTTP response status, MIME, `Network.loadingFinished.encodedDataLength`, cache/service-worker signals and completion/retry flags. Retain image element `currentSrc`, intrinsic decoded dimensions, and post:slot association in the collector's companion evidence. Do not assign a historical image to an unrelated request merely because paths or filenames match.

The aggregation still does **not** prove the before and after photos show the same historical scene. A 960px/no-upscale derivative requires original archival identity, picture/crop inspection, correct ALT/caption, item-level licensing and credit; approval to cache as WordPress media must be documented separately. This sprint grants **no publishing permission**.

The frozen Oct 30 inventory is 61 published posts / 355 source slots / 288 third-party up-stream references; 13 WordPress original files exceed 1.5 MiB. Earlier 67.06% refers to *original storage bytes*, not downloaded bytes. The reported **42 broken photographs** lack a sitewide verified guest-browser census and the claimed **76% reduction** lacks matched real cold CDP transferred-byte measurements. Both figures remain unverified. No WordPress production write, offsite media copy, homepage edit or spend occurred.

Site QA PR #154 owns independent guest-browser P0 image diagnosis (285:5, 285:2, 287:5, 418:1–2, 407:1); this is strictly an aggregation/release-proof fix, not a rewrite of Site QA's existing browser drafts.
