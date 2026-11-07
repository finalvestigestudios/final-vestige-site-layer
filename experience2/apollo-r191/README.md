# Apollo R191 — print source custody + contrast (STAGING ONLY)

Issue #150 / cross-reference #820. Parent: R190 draft PR #1411 at `654b36da7a3af538504be518d4fae3a7ff161ec6`. Never merge, activate, or deploy without governed release approval. No homepage PR #49, Research Desk PR #158 or WordPress content/settings edits.

## Reproduced defect

Chromium print-media of R190's closed native `<details>` controls hides the NASA source URLs, notwithstanding the preexisting `@media print details{display:block}` styling. Printing a source-led investigation therefore loses its original-source custody. Further, several dark-theme text colors inherited into the print style produce pale text on white pages.

## Actual component

`build_r191.py` checks all four R190 input SHA-256s, validates exact already-published NASA link destinations, then generates a standalone R191 `[fv_ex2_apollo_atlas]` staging plugin. It appends an **eight-record print-only source and rights index** outside collapsed `<details>`, listing the canonical NASA archival and Review Board URLs in visible text, and forces readable black ink in print. No media files, new analytics, merchant links, fabricated geospatial content or script dependency; the index is hidden on screen but visible in print and if CSS is unavailable. The eight original native source disclosures remain fully interactive on screen. Missing/tampered HTML/CSS fall back to the readable original investigation; optional JS corruption never suppresses history.

## Local reproduction

From a checkout containing the stacked R183–R190 source branches:

```sh
python3 experience2/apollo-r191/build_r191.py
python3 -m unittest discover -s experience2/apollo-r191/qa -p 'test_*.py' -v
python3 experience2/apollo-r191/qa/chromium_print_gate.py /tmp/apollo-r191-chromium
php -l experience2/apollo-r191/dist/fv-ex2-apollo-r191.php
node --check experience2/apollo-r191/dist/assets/campaign-handoff.js
```

**Locally executed 2026-11-07:** Python/PHP 10/10 PASS; real Chromium/Playwright 12 contexts, 144 assertions per run, two runs, all 12 screenshot SHA-256 hashes matching. Source-equivalent executable files were verified with Git blob IDs against the new PR. Browser widths: 320, 360, 390, 768, 1440, 1920 px; no-JS, keyboard, touch, reduced motion, forced colors, 390/1440 print-media. PHP WordPress-function shim exercised the actual generated shortcode output, not just an independent HTML mock. This is **not installed WordPress**. Direct external/localhost Chromium navigation is blocked in the execution environment, so no actual cache, CDN or cross-session assertion has been made. LCP from `about:blank` / `set_content` is unavailable (null); controlled CLS samples = 0 but not real-page Core Web Vitals. Genuine axe-core and actual screen-reader testing remain outstanding.

## Historical and legal provenance

- [NASA Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): no specific ignition source conclusively established.
- [NASA advertising guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/): do not claim NASA endorsement; commercial astronaut likeness/branding restrictions can apply.
- NASA image catalogs are linked rather than embedded. S67-19766 association elsewhere remains unverified; no speculative map pins.

## Offer → funnel step → blocker → change → evidence → owner

| Offer and step | Blocker | Change / test | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Potential Apollo educator dossier → purchase | No independently verified purchasable, rights-cleared Apollo SKU, checkout or fulfillment | Verify inventory and merchant-confirmed orders before adding a sale CTA | COMMERCIAL HOLD | Founder / Claude commerce |
| Grok history video → Atlas | No independently verified published Apollo `asset_id`/UTM link | Align with TASK-008 without taking over Grok/Praxxis queue | UNVERIFIED | Grok / Praxxis |
| Atlas → investigation | Printed evidence omitted source custody; low-contrast print | R191 printable eight-source index, readable contrast | OFFLINE PHP+CHROMIUM PASS | Apollo |
| Confirmed orders → net revenue | No verified Apollo paid orders, fees/refunds or qualified-human cohort denominators | Seven/thirty-day merchant/source reconciliation | NOT COMPUTABLE | Analytics / Claude |

Only visitor action remains **Read original investigation**; a hypothetical dossier is not an approved sellable offer. No new purchase or affiliate claim. KPI when evidence permits: realized net revenue per 1,000 qualified human sessions, from unique Grok asset ID through merchant confirmation with fees/refunds. Content views and link clicks are not sales.

**Release HOLD:** installed nonproduction WordPress/Assembler/Gutenberg, print-to-PDF source link testing with real browser navigation, genuine axe-core, screen readers and print physical validation, CDN/CSP, official-source and rights review, exact-head CI, independent QA and founder approval. No change to production or any active homepage branch.
