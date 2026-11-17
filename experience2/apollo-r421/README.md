# Apollo Experience 2.0 — R421 / source receipts (STAGING ONLY; release HOLD)

**Purpose:** This additive experience gives educators and high-intent research readers a portable, text-only provenance receipt for each of three original Apollo source questions. It intentionally is *not* an e-commerce product or a new newsletter opt-in. It gives one relevant next action to the existing [free Apollo 1 investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). A rights-cleared individual teacher or institutional educational dossier remains **proposed, unpriced and unverified**, not advertised as sellable.

## Exact source custody and editorial integrity

`staging-source-receipts.php` reads the *actual* R420 `fv_r420_cases()` backed by R419's photo/date source concordance, R418 chronology and R411 six-record NASA catalog. It pins the upstream R420 PHP Git blob `e3f1c9897e453512569a0fdd937c01e3b6e7f783` and exact reviewed local CSS/JS blobs. R420 further pins R419, which pins R418 and R411; R418 pins R415 and R411. None of those existing files is edited. A failed integrity check, unapproved page, missing dependency or nonstaging environment serves only a safe link to the existing article.

Each plain-text receipt separates the **contemporary historical finding** from **what the evidence cannot show**, identifies its **photograph date**, links directly to the **NASA historical article** and a **separate photo catalogue** (no photo reproduction). Cases address (1) unresolved January 1967 original ignition, (2) a January 2017 museum photo not proving 1967 hatch use, and (3) later **102 deliberate CM ignitions** that cannot determine the initial accident spark. Never depict these dates as one continuous footage record. The curated atlas remains a *non-geographic source crosswalk* with zero fabricated maps, pins or relations.

Authoritative sources: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/), [NASA historical report on 102 later ignitions](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/), and [NASA Brand Center](https://www.nasa.gov/nasa-brand-center/). NASA permits links to public pages subject to non-endorsement; every potential photo/likeness reuse must be individually evaluated. No NASA logo, image, audio, historical document reproduction or endorsement is included. Exact R411/R419 references remain unaltered.

## Component and interaction

- New shortcode `[fv_ex2_apollo_source_receipts_r421]` requires `FV_R421_ENABLED === true`, `FV_R421_STAGING_PAGE_ID` matching the actual queried singular page, and `wp_get_environment_type() === 'staging'`.
- All three full receipt texts exist in a keyboard-focusable `<pre>` element without JavaScript, accessible links and native `<details>` for finding/limitation checks.
- Tiny optional JS progressively reveals three **Copy receipt** buttons, calls only the browser clipboard API, confirms success only when the promise resolves, and announces failure with an accessible selectable-text fallback. No external JavaScript, network, consent data, cookies or analytics events.
- Strictly scoped CSS supports 320–1920px, 400% font enlargement, keyboard focus, touch, forced colors, reduced motion and print. Multiple shortcode instances receive independent IDs; no new inputs/forms or tracking.

## Executed independent local validation (not installed WordPress)

Run with PHP 7.4+ and Python 3 plus Playwright/Chromium and BeautifulSoup, from this directory with the **exact** upstream `apollo-r411`, `apollo-r415`, `apollo-r418`, `apollo-r419`, `apollo-r420` siblings present:

```sh
php -l staging-source-receipts.php
python qa/test_contract.py
python qa/test_browser.py
python qa/release_gate.py  # intentionally exits 2, HARD HOLD
python qa/package_evidence.py
sha256sum QA/Apollo_R421_Local_Evidence.zip
```

Native Python assertions exercise actual PHP source output, upstream/CSS/JS tamper rejection, disallowed production/wrong page, valid NASA destination classes and one article CTA. Playwright uses real Chromium via `page.set_content()` on PHP-generated HTML; it does **not** navigate an installed staging site. Screen captures and machine-readable browser scenarios are in `QA/`. This runtime disallows Chromium `goto` even to local HTTP (`net::ERR_BLOCKED_BY_ADMINISTRATOR`), so navigated LCP/CLS and genuine axe-core were **not measured**; CDP accessibility tree is not a substitute for axe/assistive-technology review.

**Never claim** WordPress/Assembler/Jetpack compatibility, genuine axe, field CWV, content licensing, CI green, social posts or paid orders without separate receipts. Hosted CI on the exact new HEAD, actual WordPress staging, keyboard/touch on real devices, NVDA/VoiceOver, paid SKU/fulfillment/rights, per-asset Grok campaign link and founder approval all remain independent release gates.

## Conversion-first owner plan (source of truth #820 / charter #818)

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Original Apollo educator dossier (proposed, not sellable) | Purchase → fulfilled item | No approved rights manifest, verified active price/SKU/checkout/fulfillment | Withhold paid CTA; approve actual offer first | **HOLD** | Founder + Claude / Commerce |
| Real Grok Apollo long-form or Short | Platform asset → qualified landing | No proven published asset ID and exact allowed website destination | Coordinate only through Praxxis/Grok TASK-008; preserve founder posting approval | **UNVERIFIED** | Grok / Praxxis |
| Free source receipts → original investigation | Evidence confidence → intent continuation | Users may not know which claims an archival photo actually supports | Copy-ready citation receipts, links, one contextual free article CTA | **PASS offline fixture only / STAGING HOLD** | Apollo experience / independent QD |
| Confirmed paid order | Net revenue per 1,000 qualified humans, 7/30-day cohorts | No qualified unique sessions, merchant orders/settlements/refunds/fees | Claude acceptance/reporting with appropriate privacy and consent; no duplicate tracking | **NOT COMPUTABLE** | Claude / Commerce |

Only a completed sale independently evidenced by the merchant and netted for fees/refunds counts as commercial success; `copy` events, page visits, platform views, subscribers, affiliate outbound clicks and checkout starts do not.

## Ownership and release boundaries

New code only in `experience2/apollo-r421/`, proposed atop R420 draft PR #2817. No homepage PR #49 or lead homepage branches, no mutation of R158 Research Desk, Grok/Praxxis Task Drive, WordPress content/settings, analytics, merchants, affiliate links, social posts, email or production. Hard HOLD until independently reviewed staged installation, true browser HTTP/axe/LCP/CLS results and explicit founder production release authorization. Resolve upstream R417 source-versus-tested discrepancy separately before integrated release.
