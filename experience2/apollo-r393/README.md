# Apollo Experience 2.0 / R393 — Source graph and chronology acceptance

**Draft only; production HARD HOLD.** Stacks exclusively on Apollo R392; does not edit homepage PR #49, Research Desk PR #158, Grok/Praxxis TASK-008, WordPress, commerce, analytics or any live website.

## Reproduced defect

The inherited R392 semantic gate validates six exact NASA records against the SHA-pinned R377 research ledger but only checks that source-index and chronology links point to any existing target. In real Chromium local fixtures, moving the later flammability test record into an earlier timeline phase, swapping otherwise valid source links, hiding the free CTA, or breaking its accessible name all passed R392.

R393 fixes these verification gaps without visitor-facing changes. The read-only topology inspector checks exact A/B publisher ownership, six source index destinations and accessible labels in order, three chronology rail destinations and labels in order, correct record-to-phase membership, associated heading references, visible/operable NASA source links, native disclosures and the single free-investigation CTA. It combines with R392's sealed NASA claim, rights, uncertainty and destination checks.

The staging_gate.py entry point reuses inherited staging_smoke.py and substitutes the combined verifier for both JavaScript and no-JavaScript acceptance. It preserves existing HTTPS allowlist, GET/HEAD-only network boundary, WebSocket denial, SHA-pinned delivered CSS, genuine axe-core prerequisite and browser evidence generation.

## Executed tests, local only

Run the inherited R389 PHP fixture contract to generate experience2/apollo-r393/QA/local-php-fixture.html, then:

    python experience2/apollo-r393/qa/test_topology.py
    python experience2/apollo-r393/qa/package.py

Actual Playwright Chromium local fixture: ten viewport/input contexts across 320–1920px, 59/59 assertions. Twelve deliberate tampering cases passed the old R392 inspector but were rejected by R393. Keyboard/touch/no-JS native details, forced colors, reduced motion, large-font layout and a Chromium accessibility-tree link check passed. Fixture LCP was 64–164ms in nine contexts that returned data; no-JS LCP unavailable; CLS=0 in ten. These are NOT installed staging or field CWV. Inherited tests: staging hostname 7/7, mocked network boundaries 23/23, read-only 50/50. The deterministic archive contains three screenshots, JSON results and SHA-256 manifest, and passed a byte-identical double build.

**Not verified:** real WordPress/Assembler staging, genuine axe-core, actual browser HTTP/CSP, independent screen readers, 400% native browser zoom, hosted exact-head CI, paid merchant checkout, or any revenue metric. No source photo/logo rights conveyed; no invented geospatial pins. Never treat fixture assertions as release approval.

For approved staging only:

    python experience2/apollo-r393/qa/staging_gate.py --url https://APPROVED-STAGING-HOST/apollo/ --approved-staging-host APPROVED-STAGING-HOST --axe-script /reviewed/axe.min.js --axe-sha256 REVIEWED_SHA256 --output-dir /tmp/apollo-r393-stage

## Provenance and conversion

NASA 1967 Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
NASA post-fire testing retrospective, 2018-02-14: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/
Rights and non-endorsement: https://www.nasa.gov/nasa-brand-center/images-and-media/

The six questions use TWO publications. The 102 deliberate tests occurred in December 1967–February 1968, AFTER the January 1967 fatal fire; the Board did not conclusively identify its ignition source.

One planned funnel: Grok-approved Apollo long-form asset_id/organic UTMs → verifiable gallery → one free Apollo investigation CTA → only AFTER a licensed, sellable, checkout-verified educator kit exists, an approved contextual product offer. No sale, lead, qualified session, affiliate conversion, net revenue or conversion lift is claimed. Owner: Apollo QA for this gate; Claude for production commerce/analytics; Grok and Praxxis for creator handoff/review; founder for production, posting and spending.

Coordination: GitHub issues #150, #820 and business charter #818. Production release requires independent QD, exact-head CI, installed staging, accessibility proof and founder approval.
