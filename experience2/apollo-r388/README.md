# Apollo Experience 2.0 / R388 — publication-level evidence custody

**BUILT; locally PHP/Chromium TESTED; NOT installed WordPress staging, LIVE, merged, licensed, or founder-approved. HARD HOLD.** This isolated Apollo component sprint builds only on R387 draft PR #2638. Do not merge an unreviewed stack. Homepage PR #49, Research Desk PR #158, homepage lead branches, Grok media production, and Praxxis TASK-008 are out of scope and unchanged.

## Integrity finding and correction

Six evidence cards came from only two original NASA publications, but there was no direct publication-to-question index. A reader could see five repeated Board links and wrongly count them as five independent documents. R388 adds a native no-JS **Source Custody Index** with two explicitly named publications: **A** (1967 Apollo 204 Review Board, 5 of 6 questions) and **B** (NASA's 2018 retrospective, one question about the 102 deliberate December 1967–February 1968 test ignitions). Exactly six in-page deep links target uniquely generated card IDs; duplicate shortcodes on one page receive unique link targets. No JS, map, NASA media copy, sales CTA, or third-party request is added.

The underlying original NASA record links, six source disclosures, print mirror, six stated limits, one existing free investigation CTA, and production-disabled fail-closed custody remain intact. Reviewed CSS SHA-256 is sealed in PHP. Source-only R388 change, with no WordPress installation or writes.

## Reproduce, from checkout root

```sh
php experience2/apollo-r388/qa/contract.php
python3 experience2/apollo-r388/qa/browser.py
python3 experience2/apollo-r388/qa/package.py
```

Requires PHP CLI, Python Playwright, PyMuPDF and local Chromium at `/usr/bin/chromium`. Source custody test fixture is sealed against `experience2/apollo-r377/custody.json`. Local tests run **48/48 PHP assertions**, **302/302 Chromium assertions** in **10 contexts (320–1920px)**, keyboard/Enter/touch/no-JS, forced-colors, reduced-motion, 4× root-font stress, no horizontal overflow and a five-page printed source PDF with exactly six custody roles and six limitations. Local Playwright uses `set_content` on PHP-rendered fixture; the installed WordPress/Assembler and its actual `wp_enqueue_scripts` transport **were not tested**. HTTP navigation to `127.0.0.1` returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`; no false hosted/CSP claims. Local PerformanceObserver LCP/CLS values are fixtures, not production CWV. Genuine axe-core unavailable because no package present and DNS fetch unavailable; screen readers and native browser 400% zoom not tested. Hosted exact-HEAD CI not established.

## Historical sources / usage rights

- NASA-hosted [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): original investigation, source of ignition not conclusively identified.
- NASA [2018 retrospective on 102 deliberate later tests](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/): post-accident tests, not the January 1967 fire.
- [NASA images/media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/): source linking does not license NASA photographic marks or imply endorsement. No NASA photos or logos reproduced.

## Conversion-first and owner boundaries

One intended path: **Grok/Praxxis-approved Apollo long-form/Shorts → publication-custody index/gallery → [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → *future, separately approved and independently verified* educator product**. Verified payable Apollo SKU, rights, merchant checkout, refund policy, delivery and affiliate eligibility not shown. No purchase CTA until founder/Claude confirm. Grok owns immutable asset IDs and platform distribution; Praxxis reviews creators; Claude/Commerce validate consent-aware campaigns and confirmed paid orders. Qualified sessions, confirmed leads, merchant settlements, fees/refunds, 7/30-day cohorts and net revenue per 1,000 qualified human sessions **cannot currently be calculated**. Clicks are not orders.

## Release HARD HOLD

Install only after explicit staging approval. Require independent QD, actual Assembler WordPress test including multi-shortcodes/reusable/template parts, genuine axe-core and manual screen readers, native 400% zoom, HTTPS/CSP/network stylesheet timing, exact-head hosted CI and founder approval. No production merge, staging write, merchant/analytics/email/social/publishing/spending actions carried out by this PR. Record exact HEAD, tests, blockers in issue #150 and cross-link #820.
