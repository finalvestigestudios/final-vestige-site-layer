# Apollo Experience R293 — queued-stylesheet custody, staging-only

**BUILT; LOCAL PHP/CHROMIUM TESTED; NOT DEPLOYED. RELEASE: HARD HOLD.**

This isolated Apollo-only change is stacked on R292 PR #2089 (943c73e257e32d68ed47d26e6df61ba9a0be9abd). Homepage PR #49, Research Desk PR #158, production WordPress, live analytics, Grok/Praxxis task queues, and paid services remain untouched.

## Corrected defect

When WordPress has enqueued the Apollo stylesheet but it has not yet reached done, the previous render fallback emitted a second HTML stylesheet link into body markup. R293 first checks both done and enqueued, and emits the native body fallback **only if no stylesheet has been queued or printed**. A dynamic/no-JS shortcode with no queued stylesheet still receives exactly one fallback link, even if rendered twice. This is a potential duplicate-resource and page-weight reduction, not proven production LCP improvement.

## Test and evidence

Run: python experience2/apollo-r293/qa/release_gate.py /tmp/apollo-r293-gate

The gate uses actual PHP and actual Chromium/Playwright at 320, 390, 768, 1440 and 1920 px with JS disabled/enabled, real fragment focus, unique IDs, no unexpected requests and no horizontal overflow. The extended independent local archive suite checks 12 PHP cases (including the prior R292 negative control), 10 Chromium contexts and 2 actual printable PDFs preserving NASA URLs. Existing R290 PHP checks pass 38/38.

**Unresolved:** Browser HTTP navigation is blocked by ERR_BLOCKED_BY_ADMINISTRATOR, so no real HTTP/CSP acceptance or navigation LCP/CLS. Genuine axe-core is unavailable due to npm DNS failure; NVDA/VoiceOver and installed WordPress/Assembler acceptance remain untested. Local document rendering and screenshots are not production field evidence or WCAG certification. Hosted CI, independent editorial/source/media rights review and founder approval are required before merge or deployment.

## Provenance, acquisition and commerce

The Apollo historical data, source hashes and NASA allowlisted URLs are unchanged. Original Board narrative: https://www.nasa.gov/history/Apollo204/narr.html ; original proceedings: https://www.nasa.gov/history/Apollo204/proceed.html ; NASA advertising restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Do not infer NASA endorsement or permission to commercialize media. No speculative geographic pins or unlicensed imagery.

Controlled conversion hypothesis: verified Grok Apollo asset ID/UTM -> source Atlas -> original free investigation -> only if independently approved and appropriately disclosed, a related payable item -> independently verified paid transaction, fees and refunds -> realized net revenue per 1,000 qualified human sessions (7/30-day cohorts). **No Grok Apollo publication, merchant acceptance, affiliate sale, confirmed lead, visitor attribution, or net revenue is verified here.** Grok owns distribution, Praxxis external review, Claude production analytics, founder production/spend approvals. Coordinate Issue #150 and commercial charter #820/#818; do not alter TASK-008 or published website.
