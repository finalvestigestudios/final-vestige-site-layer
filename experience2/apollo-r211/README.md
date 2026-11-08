# Apollo Experience 2.0 R211 — NASA photo/report cross-check (DRAFT / STAGING HOLD)

**Scope:** isolated `experience2/apollo-r211/`, stacked on exact R210 SHA `c417f6063a5ba480fc7783bd62f021c6b3e5c1a8`, draft PR #1559. No modification of homepage PR #49, original Research Desk PR #158, WordPress production/staging content/settings, affiliate offers, emails, social distribution or measurement scripts.

## Source evidence and final correction

NASA's S67-15717 **image-detail page** has two separate date surfaces: caption `S67-15717 (1967)` and explicit metadata **`Taken January 3, 1967`**. The original Apollo R210 date was accurate; an initial R211 staging idea relied only on the year-only caption, but a second direct-page review revealed the day-specific Taken field. This prototype's final source custody retains Jan 3 as the photo date and cites the **image-detail Taken field**, not just the gallery caption. Separately, the Apollo 204 Review Board report dates **command-module altitude-chamber removal** to January 3. They corroborate the date but **do not establish that the photograph depicts chamber removal**, the exact sequence of operations, or fire conditions.

Primary sources (checked 2026-11-08):
- NASA photo catalog image detail, `Taken January 3, 1967`: https://www.nasa.gov/image-detail/amf-s67-15717/
- NASA Apollo 1 image gallery, year-only caption: https://www.nasa.gov/gallery/apollo-1/
- NASA Apollo 204 Review Board, January 3 chamber removal: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- NASA advertising/nonendorsement limits: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

R211 adds both direct NASA citations, an accessible chronological **date-source cross-check**, corrects the gallery/custody explanation, and machine-readable source-record and custody-ledger metadata with explicit independent `date_source_url` and `event_source_url`. No new media embedding, fictional geographic pins/edges, extra JavaScript or paid CTA.

## Source reproduction

R210 generated stage assets are required. Hard SHA-256 pin: R210 `manifest.json` must be `ff13886f46237b08e71d6b68cb13f8d712941cea6e99b1130c7e8de9736a3e7b`; each R210 asset must also match its manifest. Generated R211 `dist/` is excluded from commits.

```sh
export FV_APOLLO_R210_DIST=/absolute/path/to/R210/dist
python3 experience2/apollo-r211/build_r211.py
php -l experience2/apollo-r211/dist/fv-ex2-apollo-r211.php
python3 experience2/apollo-r211/qa/gate_r211.py /tmp/apollo-r211-A
python3 experience2/apollo-r211/qa/gate_r211.py /tmp/apollo-r211-B
```

## Actual local test scope and limits

The real Playwright/Chromium 144 test suite uses PHP shortcode-shim HTML, 11 browser contexts per run from **320 to 1920px**, keyboard/Enter and native disclosures, touch, JavaScript-off, reduced motion, forced colors, 200%-CSS-zoom simulation, closed-answer print visibility and late-render fail-open fallback. It captures screenshots **before** touch interactions to prevent nondeterministic touch-hover state. The fixture-only buffered PerformanceObserver records LCP and CLS. Negative-mutation checks guard false photo-date claims, missing proof, duplicate CTA, dead fragment, fabricated geo and false NASA endorsement.

**Do not equate fixture tests with installed WordPress/Assembler, live link navigation, real 200% browser zoom or production CWV.** Genuine axe-core, NVDA/VoiceOver, installed staging/shortcode acceptance, exact-head CI, independent QA, canonical R198 chain reconstruction and founder release authorization remain **NOT VERIFIED**. No media commercialization rights are approved.

## Conversion-first lane

Grok (once a real asset ID and publication link are verified) → Apollo Atlas → independently sourced photo/Board date clarification → source-comparison exercise → **Read original investigation** (the existing free CTA) → proposed educator dossier **only after** teacher demand, rights, an actual approved SKU, checkout/fulfillment and founder approval. The proposed dossier is **not presently for sale**. This branch adds no new paid CTA, no affiliate links, no marketing scripts, and no asserted conversions. Net revenue per 1,000 qualified human sessions is **NOT COMPUTABLE** without source-of-truth qualified sessions and merchant-confirmed paid orders less refunds/fees.

Grok owns content/distribution; Praxxis owns creator QA and TASK-008; Claude owns production website/analytics; founder retains release/spend approval. Cross-reference engineering #150, business measurement #820 and charter #818.

**Release gate: STAGING HOLD.**
