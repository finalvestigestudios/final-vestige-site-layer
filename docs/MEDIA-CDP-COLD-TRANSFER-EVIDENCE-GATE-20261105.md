# Media Recovery — cold image-transfer CDP evidence gate (2026-11-05 Pacific)

**Independent media scope:** Draft PR #183 only. This is a source/test change to the offline request-ID attribution engine. It does **not** change Site QA #154, the interim homepage design, WordPress, image assets, licenses, subscriptions or third-party CDN behavior.

## Verified defect, concrete fix

The existing [`request_id_wire_core.cjs`](../qa/media-recovery/request_id_wire_core.cjs) could report positive, savings-grade article-image bytes for **eight invalid evidence cases**: missing `was_cached`, missing `from_disk_cache`, missing `from_service_worker`, disagreeing CDP/DOM image MIME, missing or zero intrinsic image height, and missing or disagreeing DOM MIME. Although its matching CDP request ID was real in the synthetic fixture, it could not prove a *fresh, correctly decoded image of that type*. This overstates confidence in cold-visit byte measurement and downstream methodology for the reported 76% weight reduction.

**Fix:** require `natural_height>0`, a positive width, a present image/* DOM response MIME, exact normalized response MIME agreement between the decoded slot and its CDP Image row, and all three cache booleans explicitly `false` (unknown must NOT be treated as uncached). The existing request-ID, image-source, encoded byte, HTTP 200, rights and no-write gates remain intact. An ordinary uncached JPEG is still accepted.

### Evidence and tests

- Previous source blob: `cb7e3e21e190db93fe7d7e3cda1fd98feba2f408` at prior media HEAD `c98bc465e3322cea19e7256b8f8ab9c8bf545b5b`.
- Corrected source commit `757766163778854895ecad12628c9820fa774869`; source blob `3c5b3cb50ac6d793415c232ad0df1898af8d9c04`.
- Expanded test commit `fe9032c9235aa6524779c8b3e92b69ea603c4064`; test blob `c8af5f3ccae9fb4d0a9f8ad06847e82754629dfa`.
- [Machine-readable before/after negative controls](../qa/media-recovery/cdp_trust_gate_20261105.json): **eight cases that previously returned fictitious 5,000 image-transfer bytes now return null / `complete:false`**; one legitimate 5,000-byte positive control still passes.
- **31/31 tests passed** when the exact committed JS source and test blobs were replayed in isolated V8 with a constrained fixture-URL `sameSource` shim. Native Node integration CI and a real guest Chromium evidence capture **have not been executed**; do not call this an end-to-end production validation.

A result from these synthetic fixtures is **never a real visitor transfer measurement**, nor a demonstrated 76% improvement.

## Site-wide, P0 and performance evidence (no fresh origin HTTP)

The existing frozen 2026-10-30 census is **61 published articles / 355 stored images / 353 distinct image URLs / 288 external-origin references**. The previously reported **42 broken original images are not browser verified**, and the alleged **76% transfer-weight saving has no complete before/after CDP measurement**. The 13 WordPress original media files over 1.5 MiB account for **43,522,829 stored bytes**, not measured visitor transfers.

The current high-priority Site QA browser order remains `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1` (Three Mile Island, Sunshine Skyway, Scotch Cap, Hebgen Lake). Their **exact original URLs and older independent-retriever wrapper statuses** are pinned in [the six-source ledger](../qa/media-recovery/source_chain_gate_safety_20261105.json). Wrapper 400/403/404/500 responses are not browser/origin HTTP statuses; actual final Image HTTP, `currentSrc`, decoded pixels and transferred bytes remain null.

**Best near-term first-party performance candidates after the P0 restoration queue:** five oversized inline PNG originals in posts 34–38 (1672×941 each, 13,267,538 combined stored bytes, no WP subsizes recorded), conditional **960×540** derivatives; two direct large Malbone Street JPEG originals (post 621) also warrant inspection. Large Vasa originals use Jetpack `fit=1024` and cannot be assigned original-file download weight. Item-level rights/credit, actual binary dimensions and cold browser byte counts must precede release. No derivative may exceed **960px width or upscale the master**.

## Restoration/caching/WordPress decision path — NOT authorization

1. Site QA #154 runs its existing logged-out CDP browser workflow and retains raw JSON and screenshots. Run the existing [guest adjudicator](../qa/media-recovery/adjudicate_p0_guest_evidence_v1.cjs) against that evidence, not the older tool-wrapper codes.
2. For browser-confirmed missing images, compare the exact photographic scene against Navy/Coast Guard, USGS, Florida Memory, NASA, NARA or other primary records. Rights and attribution are **HOLD** until cleared per item; different scenes require editorial review.
3. If rights and identity are approved later, obtain the source legitimately, record source page/master SHA-256 and dimensions, prepare a visually checked max-width 960px no-upscale derivative, and preserve the original URL and attribution. A staged derivative is not an automatic permission to cache or republish.
4. WordPress Media Library upload and a narrow, reversible original post-slot adjustment require separate explicit production authorization, and visual before/after guest checks (historical identity, alt, caption, LCP/CLS). No Gutenberg block-wide rewrites.
5. Compare paired cold browser runs at matching viewport/Chrome/cache profile using both strict request-ID scope and the offline [CDP comparator](../qa/media-recovery/compare_cold_image_wire_v1.cjs). Report **laboratory pair** deltas only; never promote them to site-wide 76% or field-user improvement without complete replicated measurement.

## Safe handoff

Media Recovery owns this CDP attribution correction on draft PR #183. Site QA #154 continues its existing browser collection and no duplicate collector was created. **Production images restored: 0; production writes: 0; media downloads/copies/uploads: 0; subscription spend: 0.**
