# Apollo R290 — accessible Board authority document-custody round trip (DRAFT / HARD HOLD)

**Scope:** isolated Apollo Evidence Atlas staging; parent R289 (draft PR #2071). Homepage PR #49, canonical Research Desk PR #158, WordPress production/settings, attribution, checkout, Grok's video production and the creator task board remain untouched. The shortcode is still `[fv_apollo_source_experience]`.

## Finding / change

The January 28 EvidencePlate identified NASA's conflicting Board-establishment dates but required visitors to search through the entire experience for the later four-action custody chronology. R290 creates a **native anchor** from that exact claim to the first dated authority record, unique `tabindex="-1"` destinations for all four original records, and return navigation from every record to the same January 28 claim. No JS, API calls, imagery, speculative maps, visitor tracking, merchant link, extra conversion action, or factual changes. In print, internal navigation is hidden while original-source URLs remain legible.

### Primary sources and source dependence

- Original Board narrative: oral establishment dated January 27, 1967; first meeting January 28, written confirmation February 3: https://www.nasa.gov/history/Apollo204/narr.html
- 1967 Board proceedings: Jan 28 initial meeting; Jan 31 receipt/distribution of a memorandum dated Jan 28: https://www.nasa.gov/history/Apollo204/proceed.html
- NASA Safety later summary: dates establishment Jan 28 (later institutional summary, NOT independent witness): https://sma.nasa.gov/sma-disciplines/accllp/apollo-1

Exact dates and record relationships remain **pending independent editorial sign-off**. No conclusive ignition-site claim. Direct NASA links do not imply NASA endorsement or permission for promotional use of its insignia or astronaut likenesses.

## Run deterministic gates (Python Playwright and PHP required)

```bash
php -l experience2/apollo-r281/apollo-source-experience.php
php experience2/apollo-r290/qa/php_gate.php
python experience2/apollo-r290/qa/browser_gate.py /tmp/apollo-r290-QA
python experience2/apollo-r290/build_archive.py /tmp/Apollo_R290.zip /tmp/apollo-r290-QA
```

Browser gate renders **actual PHP** two instances in Chromium at 320/390/768/1440/1920px (JS on/off). Verifies unique IDs; four authority targets per instance; Enter-key claim → native fragment → precise dated record → return-focus behavior (100 roundtrip focus checks); keyboard source navigation, forced-colors focus indicator, reduced motion, touch emulation, root-text reflow, readable no-JS chronology, printing primary-source references, no overflow or requests. Captures deterministic 390px and 1440px screenshots twice; manifest contains SHA-256 of each file. PHP runs 38 assertions including tampered NASA source rejection and a single free investigation CTA. Browser LCP/CLS on locally injected HTML, if observed, are **synthetic only** and are not production Core Web Vitals.

**Unsupported / HARD HOLD:** genuine axe-core package not installed (registry DNS blocked); independent NVDA/VoiceOver, installed WordPress/Assembler + reusable-block acceptance, real HTTP/CSP navigation (`net::ERR_BLOCKED_BY_ADMINISTRATOR`), browser UI zoom, field LCP/CLS, hosted CI, editorial/media-rights review and founder release authorization. Do not construe these as passes. No installed WP, live server, social platform or merchant transactions were touched.

## Conversion-first responsibility / release decision

Published Grok Apollo asset ID and attributable landing traffic not verified. One in-article next action is the **free Apollo investigation** (https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). Any distinct, relevant Mini Museum product guide needs independently verified publisher acceptance, permitted channel, product fit, trusted merchant payment/refund/fee data and founder authorization before activation. Grok owns video/shorts distribution; Praxxis independently reviews creator traffic; Claude owns production engineering/analytics; founder retains all public release and spending approvals.

KPI: *realized net revenue per 1,000 qualified human sessions*, 7/30-day cohorts. Denominator, paid orders, commissions, fees and refunds are not verified here, so commercial CVR/net KPI is **NOT COMPUTABLE**. Outbound clicks and leads are never called sales. Cross references: #150 and #820, charter #818 and TASK-008.
