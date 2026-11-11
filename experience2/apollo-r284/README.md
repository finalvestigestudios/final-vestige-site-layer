# Apollo Experience 2.0 — R284 native source custody (STAGING / HARD HOLD)

Issue #150: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150
Commercial coordination #820: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820
Original Research Desk PR #158: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158

This branch is stacked on isolated R283, independent of frozen homepage PR #49, the lead homepage lane, and the original Research Desk branch. No WordPress or live changes.

## Actual change
R283 had working chronology focus and a source catalogue, but no native claim-to-specific-source-to-claim roundtrip. R284 links each evidence plate directly to its corresponding catalogue record and adds a return link. The six pairs across two rendered instances use normal hash anchors and work with JS disabled; catalogue targets have unique IDs, tabindex=-1 and visible keyboard/forced-color focus. Touch controls have a 44px minimum height. Claims, review-pending state, source-dependency warnings, integrity digest and NASA destinations are unchanged. No media, maps, speculative locations, new scripts, merchant links or tracking were added.

Print hides the navigational jump/return controls but retains the three NASA source URLs and now prints the full free-investigation permalink.

## Official source and rights references checked Nov 11, 2026
- NASA Apollo 1 mission history: https://www.nasa.gov/mission/apollo-1/ (later institutional summary).
- NASA Safety and Mission Assurance: https://sma.nasa.gov/sma-disciplines/accllp/apollo-1 (later institutional summary; not independent witness).
- NASA Apollo 204 Review Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ (1967 primary investigation, exact ignition source not conclusively identified).
- NASA advertising and brand guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ and https://www.nasa.gov/nasa-brand-center/ (NASA neither endorses commercial offers nor grants blanket rights to insignia/likenesses).
- Original Final Vestige investigation: https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ (verified from live Journal).
Link verification is NOT a stored, cryptographically verified NASA content snapshot, image-rights license, or editorial approval.

## Exact locally executed tests
- PHP syntax PASS.
- Updated SOURCE-CONTROLLED gate experience2/apollo-r281/qa/committed_gate.py: Chromium 10/10 viewport/JS contexts PASS (320,390,768,1440,1920; JS on/off). Sixty native chronology focus and sixty claim-to-catalogue-to-claim paths. Source allowlist/hash-mutation rejection, native disclosures, 200/400% root text, forced-colors, touch, reduced motion, printed NASA and investigation URLs, zero unplanned browser requests or horizontal overflow.
- Separate supplemental R284 independent control: 10/10 contexts, sixty additional roundtrips, R283 original rendered as a negative control with missing source jumps, and actual Chromium print-to-PDF text confirmed source URLs, editorial pending state and investigation permalink. Four 390/1440 screenshot files matched across two runs.
- Committed QA receipt SHA-256: 1469acdcefa0a268e810eb58d1e5e32ab5e89bf3fda78fde1aea9ceaa6e53f90
- Supplemental QA receipt SHA-256: 27dffd862483678e0902a2e20d993798414a50eec5d37b7525e5a01e319b044e
- Source blobs: PHP 7abcb13fc021a717a2831d12c0046224df5242fc; CSS 8303c9fc065e83f099a2ddfc7f43764a4b14c94f; committed QA f472c7c7a5c1b43789bfa7a87442392862455c28.

To reproduce from repository root:
    php -l experience2/apollo-r281/apollo-source-experience.php
    python experience2/apollo-r281/qa/committed_gate.py /tmp/apollo-r284-gate

Supplemental independent test, original R283 fixture, screenshots and exact receipts are included in the downloadable R284 QA archive; supplemental bytes are not claimed as part of GitHub.

## Strict commercial objective and release gates
Candidate funnel: VERIFIED and PUBLISHED Grok Apollo video asset → Evidence Atlas → one free original Apollo investigation CTA → separately disclosed optional Mini Museum guide, if founder-approved and a payable merchant agreement is authenticated → merchant-confirmed paid sale less refunds/fees. Source navigation is a trust and qualified-continuation hypothesis, NOT proof of conversions.

Offer→funnel blocker: Mini Museum payable eligibility, product/offer match, published Grok asset ID and merchant settlement records remain unverified. No new affiliate CTA. Qualified sessions, confirmed leads, sales and realized revenue NOT COMPUTABLE. North-star KPI: net revenue per 1,000 qualified human sessions by 7/30-day cohort (tiny-sample warning).

Grok owns scripts/posts, Praxxis creator review/TASK-008, Claude core production/analytics, founder approvals. No social/CMS/email/merchant/analytics writes or spending.

Status: BUILT + SOURCE-CONTROLLED + LOCAL TESTED, NOT LIVE. No axe-core, independent screen-reader, installed WordPress/Assembler, real browser HTTP/CSP navigation, genuine p75 field LCP/CLS, hosted CI/QD, editorial signoff or founder approval. Actual HTTP navigation was blocked by Chromium with ERR_BLOCKED_BY_ADMINISTRATOR; about:blank set_content observations cannot replace network-based Core Web Vitals. Release HARD HOLD.
