# EX2 flagship archival transfer admission — November 6, 2026

**Review only. Release HOLD.** Stacked on draft PR #1207 at exact base `994286a0a9c732131035ea09e16f0bfeb28740ac`. Never install, merge or publish without founder approval and existing QD/CI gates.

## Actual defect closed in source

Prior guest browser admission recorded image responses but did **not** require either flagship archival image to exist, decode or transfer successfully. A fixture with missing Apollo and Franklin images could satisfy all prior `report['checks']` conditions. That made it possible to overlook a broken opening/evidence image while reading otherwise healthy DOM/CTA receipts.

The new `archival_delivery` check requires, at **390px and 1440px**, for both identified plates:
- A matching `img` element and meaningful alt text.
- A nonzero decoded `naturalWidth` and `naturalHeight` after bringing lazy images into view.
- An actual browser response for the `currentSrc` selected by `srcset`.
- HTTP 2xx, nonempty response body, and SHA-256 evidence. No image or response = FAIL, never PASS.
- Source/CDN URLs in report are **query/fragment stripped** to avoid disclosure of private preview tokens. Raw URLs remain in memory only for matching.

This asserts **delivery**, not image identity or reuse rights. Apollo `S67-19766` and the Franklin Commons reproduction still require source-custody verification against exact files; the existing NYPL capture remains separately rights-gated. Do not mistake successful transfer for legal clearance.

## Native evidence

Tested in local Chromium with two tiny **synthetic** PNG image bodies, route-fulfilled at `synthetic-archive.test`; these are NOT archived NASA/Franklin objects. Eight native image tests PASS (healthy, responsive query redaction, missing Apollo, missing Franklin, HTTP 404, zero-body, missing alt, missing network receipt). Existing seven smoke tests PASS after updating the fixture expectation: synthetic homepage without image elements must fail archival qualification. Total **15/15 native tests PASS**. Exact GitHub source blob hashes confirmed against native-tested local files.

No live homepage screenshots, WP Playground/Assembler rendering, Jetpack subscriber delivery, Lighthouse, field CWV, Safari, or axe signoff were obtained from this run. The tool still fails closed when axe is unavailable. The synthetic fixture must never qualify a real deployment.

## Conversion relevance and ownership

**Offer:** Existing 52-page Seven Day Focus Fieldbook. **Step:** credible evidence → historical homepage → contextual lead CTA → independently confirmed signup → verified purchase. **Blocker:** broken or unverified archival images on responsive entry screens degrade trust, yet were not required by the prior browser gate. **Change:** real decoded-image and exact response-byte admission. **Evidence:** 15 passing native tests, six negative image controls. **Owner:** EX2 homepage QA; Site QA independently reviews; Claude owns revenue attribution and production engineering. **Commercial conversion:** not measured and not claimed.

## Next decisive action

Run the complete source-controlled seven-chapter homepage inside isolated WordPress Playground with the actual Assembler theme and the strengthened admission harness. First inspect existing live Page 6 and preserve its 72 Margins, current published seven chapters, Jetpack/Focus signup and any other live content. The WordPress.com Personal plan has no native one-click staging clone; `vestigefinal-tezws.wpcomstaging.com` is not a separate environment. Isolated staging does not certify WP.com Atomic/Jetpack host behavior. Real guest CTA, 200% zoom, browser accessibility, source-rights and measured performance remain HOLD gates. Frozen PR #49 is untouched.
