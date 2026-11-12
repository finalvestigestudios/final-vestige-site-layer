# Apollo 1 Evidence Atlas — R298 staged accessibility correction

**Status: source-controlled draft only. No homepage #49, Research Desk #158, WordPress, tracking, merchant, posting or production change.** Base is draft R297 head `407d9bbdebaa3e5e29520cc13e34cf32bcbb0f5d`. Official NASA links and their dependency/rights notices, three chronology plates, four Board authorization acts and single free investigation continuation are unchanged.

## Defect and correction

Actual Chromium accessible-tree inspection of the **original R297** two-shortcode fixture showed six indistinguishable `Inspect the source and custody record` disclosures and duplicate Board-authority and date-summary controls. Adding `aria-label` to `<summary>` failed to change the native `<details>` group's exposed name in Chromium. R298 instead adds **real text** inside each `<summary>` using visually-hidden, still-accessible spans: document title and per-shortcode instance for claim drawers; per-instance suffixes for the remaining two disclosures. If CSS fails, the contextual text simply becomes visible. This avoids a JS dependency and makes ten disclosure labels distinct in a two-instance page.

## Execute from repo's `experience2/` directory

```sh
php -l apollo-r281/apollo-source-experience.php
php apollo-r296/qa/compact_source_contract.php
php apollo-r295/qa/memo_custody_contract.php
python apollo-r296/qa/php_cache_gate.py
python apollo-r296/qa/compact_browser_contract.py
python apollo-r298/qa/disclosure_contract.py
python apollo-r298/qa/artifact_qa.py
python apollo-r298/build_archive.py
```

Real Chromium fixture checks run at 320, 390, 768, 1440, 1920 pixels with JS on/off, reduced motion, touch and native keyboard Enter/Space. This R298 local run passed **10/10** Chromium contexts, **10 unique accessible disclosure identities**, **20 disclosure keyboard toggles**, inherited PHP historical custody **21/21**, and CSS/cache **25/25**; inherited R296 Chromium **10/10**. The unmodified R297 negative control fails the new suite on duplicate summary names at 320px with JS disabled. Five local no-JS screenshots and a 13-page PDF with 64 hyperlink annotations are reproducible. The PDF's Chromium clock metadata is normalized before digesting; archive byte output is fixed-timestamp and digest checked.

**Remaining hard hold:** genuine axe-core, independent screen reader, actual browser HTTP/CSP, installed WordPress/Assembler, production/field LCP/CLS/INP and exact-head hosted CI are unverified; Chromium fixture PerformanceObserver results do **not** certify field CWV. Official-source NASA linking is not NASA endorsement or clearance for marketing, media resale, astronaut likenesses or insignia. Editorial review and founder authorization remain required.

## Conversion mandate

One relevant path: verified published Grok Apollo long-form asset *(asset_id/link unverified)* → Atlas chronology → NASA evidence → existing free Apollo investigation → only a separately approved rights-cleared educator evidence product if merchant/offer/buyer fit and checkout can be authenticated. No paid Apollo SKU, confirmed orders, qualified-human sessions, fees/refunds or merchant settlements were verified. Keep outbound clicks distinct from actual paid conversions. Measure authenticated net revenue per 1,000 qualified-human sessions in 7/30-day cohorts once data exists. This work improves accessibility and trust, **not proven sales**. Grok/Praxxis retain creator ownership; Claude owns production analytics; founder owns release and commercial approval.
