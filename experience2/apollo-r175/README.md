# R175 — Apollo 1 catalog-status truthfulness (review only)

**2026-11-06 | BUILT, GITHUB COMMITTED, OFFLINE CHROMIUM-TESTED; STAGING HOLD**

## Verified issue and correction

The original Research Desk in PR #158 presents `NASA S67-19766 · NASA` as an unqualified photo identifier on Record 01. R174's source-rights review correctly marked its **photograph-to-catalog match NOT VERIFIED on the linked NASA page**, but the unqualified original label remained visible. NASA's linked *Apollo 1 Crew Honored* page identifies the crew's January 1967 training photograph but does not establish that specific catalog ID. This is an unverified match, **not proof the ID is incorrect**.

R175 adds a visible, screen-reader-readable notice adjacent to the record label: **“Reported catalog ID: S67-19766. Not verified on the linked NASA archive record.”** It changes no historical conclusion, photographic content, outbound link, CSS outside its own component, analytics, merchant configuration or WordPress document.

Original R174 candidate Git blob: `b23879150024b3b667679ff4dd7faae1e37cfc07` (`experience2/apollo-r174/research-desk-provenance-candidate-UNPUBLISHED.html`). Source-drift fails closed, six media records and all 14 original links remain unchanged, exact original content is recoverable by reversing the one intended replacement. CSS is scoped and optional; text remains legible without CSS or JavaScript. No paid media-use clearance is implied.

## Reproduce after checking out this draft branch

Run `python -m unittest discover -s experience2/apollo-r175 -p 'test_*.py' -v`. In the complete checkout, the test discovers the actual R174 HTML and verifies the exact pinned SHA; a local evidence-bundle run uses only the separately identified controlled fixture.

Generate a proposal (never auto-write to WordPress):

`python experience2/apollo-r175/verified_catalog_label.py experience2/apollo-r174/research-desk-provenance-candidate-UNPUBLISHED.html /tmp/apollo-r175-proposed-only.html`

Run offline Chromium using genuine PR #158 source-ledger CSS/JS (NOT installed WordPress):

`python experience2/apollo-r175/staging_browser_acceptance.py experience2/apollo-r174/research-desk-provenance-candidate-UNPUBLISHED.html /tmp/apollo-r175-browser`

For independent genuine axe-core accessibility QA, use the same command with `--axe-js /absolute/path/to/official/axe.min.js`. No axe-core dependency was present in the run environment, so **axe-core is NOT EXECUTED here**; do not call these tests WCAG acceptance. Do not vendor third-party JS into production or introduce another analytics script. Screen-reader/manual QA remains outstanding.

## Test evidence and limitations

Local fixture: **8 unit methods PASSED, 1 real-repository integration method SKIPPED** because only R174's laboratory fixture was present; 8 Chromium contexts, six widths 320/360/390/768/1440/1920 with 103 assertions in supplementary witness, full page screenshots and repeated matching hashes, native `<details>` keyboard + touch, reduced motion, forced colors and no-JS. A second, source-controlled browser QA script also ran six widths successfully with 0 browser errors and optional genuine axe hook not exercised.

Fixture-only measured LCP 40–96ms, CLS 0.00542–0.04841 **after scripted filter interaction**; those CLS values are not production field metrics and cannot be read as a real-user CWV failure. User-initiated filter reflow needs native installed-page follow-up. No CDN/NASA-image acceptance, WordPress Gutenberg serialization, authenticated staging CSP check, screen-reader study, actual production LCP/CLS, or hosted exact-commit CI evidence.

## Conversion and release contract (#820)

**Audience:** educator/researcher arriving from a potential Grok Apollo long-form or Short. **Source proof:** NASA archive and Apollo 204 Review Board, not an unsupported catalog number. **Single visitor action:** Read original investigation. **Hypothesis:** accurately labeled sources reduce confusion and improve qualified continuation, not proven revenue. The hypothetical educator dossier is not a verified paid FV SKU. No affiliate or checkout CTA is introduced.

Before commercial activation: authenticate existing relevant product SKU/rights/price/fulfillment/merchant acceptance; founder approves any live release separately; link Grok asset_id/UTMs to qualified sessions and confirmed purchases, net refunds/fees, in seven/thirty-day cohorts. Until those merchant records exist, realized net revenue per 1,000 qualified sessions = **NOT COMPUTABLE**.

**STRICT HOLD:** draft PR only. No homepage #49 edits, Research Desk #158 edits, WordPress writes, deployment, creator posting, subscriptions, paid services or third-party tracking. Issue #150 owns Apollo release; #820 owns qualified traffic and revenue attribution. Grok handles creator scripts/distribution; Praxxis handles independent creator review; Claude handles production engineering; founder retains release approval.
