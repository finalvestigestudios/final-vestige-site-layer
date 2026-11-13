# Apollo R327 — reader-to-source-to-investigation acceptance (STAGING ONLY)

**Built and locally tested, NOT LIVE.** Isolated on a branch stacked over Apollo R326 PR #2293. No runtime PHP/CSS/JS changes, production WordPress writes, releases, affiliate activations, merchant changes, publishing, Grok queue writes or spending. Frozen homepage PR #49 and Research Desk PR #158 remain untouched.

## Engineering contribution

The source-controlled QA script at qa/journey_gate.py executes the complete **evidence plate → NASA documentary-source catalogue → single free investigation decision → 1967 authority-chronology record → original plate** pathway. It checks native fragment focus and disclosure auto-reveal, not just static link attributes. It also enforces three documentary records versus four contextual NASA image accessions, no invented geospatial connections, no implied commercial rights, no unauthorized sale/subscribe link, no NASA endorsement, and at least 40px external link targets in the offline fixture.

**Execute:** python experience2/apollo-r327/qa/journey_gate.py. Prerequisites: Python Playwright, system Chromium at /usr/bin/chromium, PHP and Node. HTML is produced by the existing R320 late-shortcode test harness with current staging CSS/JS injected locally. This is NOT an installed WordPress test.

**Pinned Git blobs:** PHP 91745c286b2f23fb8a93058afb58905a2756714e; CSS 550e1dc6ac869ebbda1b371343a6cdd91f8608f4; JS f85617e5f12ba747908ac507261f69c377369de7. Fail if any differs.

**Executed:** 14 actual Chromium responsive contexts (320, 360, 390, 768, 1024, 1440, 1920px × JavaScript on/off), 2 forced-color keyboard cases, 1 CSS-off/no-JS case: PASS. Four reproducible screenshots and JSON receipt. LCP/CLS are offline PerformanceObserver fixture data only, NOT production Core Web Vitals. Genuine axe-core, screen readers, Safari/Firefox, installed WordPress/CDN, native browser HTTP/CSP and hosted CI NOT EXECUTED / NOT VERIFIED. Local HTTP browser navigation is administrator-blocked.

## High-intent cohort and single proposed conversion bridge

**Audience:** educators and careful Apollo history viewers who want original evidence and teaching-ready documentation, not generic space merchandise.

Grok's future *authenticated* Apollo long-form/Shorts asset → NASA-linked Evidence Atlas → ONE existing free Apollo 1 investigation → independently verified, founder-approved Apollo teaching kit ONLY if a real payable, rights-cleared SKU and checkout are authenticated.

**Hypothesis only:** visible document custody and an honest uncertainty trail may improve downstream qualified purchase propensity. No paid offer or published Apollo asset has been authenticated in this lane. No paid CTA was introduced, and nothing here generates an analytics event, lead, sale or affiliate commission.

| OFFER → FUNNEL | BLOCKER → ACTION / EXPERIMENT | PASS/FAIL EVIDENCE · OWNER |
|---|---|---|
| Apollo teaching kit → paid order | Rights/checkout/SKU missing → authenticate actual product before paid link | HOLD · Founder/Claude |
| Grok Apollo film → Atlas | Published asset_id, platform placement, actual landing URL missing → resolve through existing TASK-008, do not take Grok queue | UNVERIFIED · Grok/Praxxis |
| NASA proof → free investigation | Native source return + focus route → new browser replay | LOCAL PASS, NOT WP VERIFIED · Apollo QA |
| Orders → realized net revenue | Qualified human denominator, settled orders, fees and refunds unavailable → reconcile 7/30-day cohorts | NOT COMPUTABLE · Claude/Commerce |

KPI is **merchant-verified realized net revenue per 1,000 qualified human sessions**, accompanied by actual confirmed purchase rate, orders/customers, fees/refunds, lead-to-paid where independently observed, attribution gaps and tiny-sample warnings. Pageviews, email leads, clicks and prints are not sales.

## Release hold / owner boundaries

Research Desk PR #158 records 02 and 03 appear to lead with NASA photo-accession pages while labeled as Board/documentary findings; separately linked Board report is documentary proof. Research Desk owner must substantiate or revise its own source classification; R327 does not modify PR #158.

HARD HOLD until genuine axe-core and independent screen-reader review; non-Chromium QA; installed WordPress/Assembler/CDN and native HTTP/CSP acceptance; NASA media-rights/editorial signoff; real Grok campaign; actual sellable offer; QD review; hosted CI on exact HEAD; and founder release authorization. No live changes or spending.

Coordination: Apollo #150; revenue #820; charter #818; TASK-008 in existing Grok/Praxxis Drive. 