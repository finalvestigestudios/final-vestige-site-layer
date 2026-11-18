# Apollo R465 — source acceptance and commercial-rights boundary

**DRAFT / production HARD HOLD.** Isolated child of R464 PR #3054. Issues #150, #820, charter #818. Does not alter homepage PR #49, Research Desk PR #158, Claude analytics, WordPress, Grok or Praxxis.

## Fixed: identifier-derived dates were being presented as verified

`KSC-20170124-PH_KLS01_0129` was previously given **24 January 2017** despite its NASA Images catalogue link being inaccessible. R465 now renders the date **unverified**: its day/month were inferred from the proposed ID, not accepted photographic metadata. The January 1967 NASA crew portrait exists, but the specific `S67-19766` archive-ID association remains under review.

**NASA source acceptance (checked 2026-11-18)**

| ID | Source status | Factual source/credit |
|---|---|---|
| S66-58038 | ACCEPTED | 18 Oct 1966 training photo, NASA/JSC: https://www.nasa.gov/image-detail/amf-s66-58038/ |
| S67-15717 | ACCEPTED | 3 Jan 1967 spacecraft preparations, NASA/JSC: https://www.nasa.gov/image-detail/amf-s67-15717/ |
| S67-21294 | ACCEPTED | 28 Jan 1967 aftermath, NASA/JSC: https://www.nasa.gov/image-detail/amf-s67-21294/ |
| KSC-20170124-PH_KLS01_0090 | ACCEPTED | 24 Jan 2017 tribute, NASA/Kim Shiflett, producer KSC: https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/ |
| S67-19766 | HOLD: ID mapping | NASA confirms crew portrait in January 1967, but not this ID mapping: https://www.nasa.gov/image-article/apollo-1-crew-honored/ |
| KSC-20170124-PH_KLS01_0129 | HOLD: catalogue, image identity and date | Candidate NASA Images URL cannot be independently retrieved; do not infer facts from proposed ID |

NASA: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Source retrieval is **not** paid-product media licensing. NASA does not endorse FV. Astronaut-likeness, logos, third-party material and promotional use require review. No imagery is embedded.

## Interaction / custody

New “NASA ID confirmed (4)” filter provides a clear research-only subset; five filters support touch and keyboard and preserve no-JS complete meaning. Source cards display individual source status, specific credit where verified, and separate commercial-reuse HOLD. Printed PDFs retain **six archival plus three chronology NASA URLs** and exactly one free investigation link. No geo pins, merchant CTA, analytics, form, or image assets.

## Executed vs blocked

- **Local PASS:** PHP lint; 25/25 source/security checks; 73/73 source-controlled Chromium smoke; 178/178 extended local Chromium/PDF checks across 320–1920, JS on/off, touch, keyboard, forced colors, reduced motion, print/PDF; inherited 43/43 R461 and 64/64 R464 PDF suites after updating stale label checks. PNG/PDF artifact SHA-256 byte-identical over two runs after metadata normalization.
- **Hosted HOLD:** not installed in WordPress staging. No genuine axe-core run, navigated LCP/CLS, field p75 CWV or manual screen-reader evidence. `qa/r465_hosted_gate.py` requires an approved **nonproduction** HTTPS host and SHA-pinned local axe-core, otherwise exits with HOLD_NOT_RUN. Independent QD, green exact-head CI and founder production approval outstanding.

## Conversion-first route and accountable owners

**Grok verified Apollo documentary / immutable asset ID** (not authenticated; Grok/Praxxis) → **Apollo Atlas trusted source/print inquiry** (local PASS, hosted HOLD; Apollo QA) → **one contextual free Apollo investigation CTA** → **separately approved, rights-cleared original educator product** (no verified SKU/checkout/fulfillment; Founder/Claude HOLD).

Qualified-human UTM sessions, confirmed leads, merchant-paid orders, fees/refunds, 7/30-day cohorts and realized net revenue per 1,000 sessions remain **NOT COMPUTABLE**. No clicks, lead events or attributed visits are claimed as sales. No live writes, merge, deployment, promotion, posting, affiliate activation or spending.
