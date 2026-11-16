# Apollo Experience 2.0 — R407 source-grounded chronology + fail-open Research Desk

**DRAFT / PRODUCTION HARD HOLD. This is a source-controlled WordPress staging *candidate*, not a deployment.** Only new `experience2/apollo-r407/` files. It stacks on R406 #2735 and leaves homepage #49, PR #158, previous Apollo branches and Grok/Praxxis TASK-008 untouched.

## What is built

- New default-OFF `[fv_ex2_research_desk_r407]` shortcode. Requires both explicit `FV_R407_ENABLED=true` and `FV_R407_STAGING_PAGE_ID` matching the current singular staging page. No production fallback to the prototype, no CMS settings/content writes.
- **ChronologyRail**, static accessible native HTML. Four NASA-grounded markers: Jan 27, 1967, 23:30:55 GMT recorded power interruption; approximately 23:31:04.7 GMT fire report; approximately 23:31:19 GMT vessel rupture; December 1967–February 1968 *later* boilerplate flammability tests. The power interruption does **not** establish one ignition arc. No interpolated measurements, animation, geographic pins or speculative relationship edges. Each event links to the exact corresponding record in the six-record Research Desk. Native anchors work without JS.
- An early **source-custody + commerce gate** checks immutable PR #158 NASA template/CSS identities, original R404 accessibility CSS, and both exact R407 assets; also verifies six evidence cards, six explicit limitation notices, NASA source links, unchanged uncertainty boundaries and exactly one offsite-FV action: the existing **free Apollo investigation**. It refuses added imagery, scripts, unreviewed outbound commerce and offsite replacement CTAs. Fail-open is just a contextual link to the already published investigation.
- Updated optional Search+SourceDrawer progressive enhancement. Corrects R406's unguarded malformed `aria-controls` selector: broken markup in one panel must not abort initialization of subsequent independent desks. Server IDs are unchanged by JS; fragment links reveal filtered records and open nested native disclosures. Escape/clear, keyboard/touch/focus management and no-JS remain supported.
- A deterministic offline `qa/assemble.py` refuses absent or mutated PR #158/R404 assets and **does not create an output directory** until the entire dependency set matches. This is not a WP installer.

## Exact source IDs

| Imported source | PR | Git blob SHA-1 |
|---|---|---|
| `templates/ledger.html` | #158 | `403d128c57b9bc82dac7c619651689070edef86c` |
| `assets/source-ledger.css` | #158 | `b8cf00afeceba115a9e9d19044fc11dcf2890cbe` |
| `assets/research-desk-resilient.css` | #2728 / R404 | `2c99fdeecd4d4245908c0f52f6a679c6f5d7718a` |
| `assets/research-desk-r407.js` | R407 | `222e084d4d5cba5b979037df2018d82946fa9a75` |
| `assets/chronology.css` | R407 | `d60a1c52dca1a6b82f15cb6009a1a876a2ad33b2` |

NASA primary report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; later test history: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ . Media guidance: https://www.nasa.gov/nasa-brand-center/images-and-media/ . No NASA photographs, trademarks, identifiably depicted people, audio, logos, embedded media or implied commercial endorsements were added. NASA source links are informational rather than merchandise associations.

## Local tests actually executed (2026-11-16)

- `php -l staging-shortcode.php` and `php qa/test_contract.php`: **21/21 PASS** (normal structure and ten adverse source/commerce changes, native server IDs, stage fail-open and immutable new file identities).
- `python qa/test_assemble.py`: **3/3 PASS** negative and local immutable SHA tests. Real assembly is **blocked** because full unmodified PR #158 and R404 dependency trees are not present in this local runtime. No fabricated files were substituted into a package.
- `python qa/test_browser.py`: **6/6 Chromium methods PASS**, including malformed-first-instance isolation, a second valid instance, searchable evidence, keyboard clear, deep-link recovery, no-JS complete content, chronology anchors and no map pins. **9 screenshot contexts**, 320/390/768/1440/1920px plus touch/no-JS/reduced motion/forced colors/root-font 4x; all 0px horizontal overflow. Browser fixture uses **synthetic text**, not NASA's actual PR #158 template; PHP source namespacing and actual R407 JS/CSS are used.
- **No installed WordPress staging, actual HTTP/CSP, real LCP/CLS, genuine axe-core, native browser zoom, independent VoiceOver/NVDA, QD, hosted exact-head CI or founder release approval.** Browser `set_content` performance cannot be represented as actual navigation or production CWV. UI metrics reported as **null**.

## Conversion-first offer/funnel decision

**One path only:** Grok-owned (not independently confirmed published) Apollo long-form asset → evidence-led ChronologyRail and Research Desk → **free original Apollo investigation CTA** → future separately founder-authorized paid educator dossier *only once* genuine SKU, commercial rights, checkout, fulfillment and refund handling are independently verified. Do not add a product pitch inside the event timeline. No affiliate or paid CTA was activated.

OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER:

1. **Educator dossier** → confirmed paid order → no verified payable SKU/rights/checkout → withhold paid CTA → **HOLD** → Founder/Claude.
2. **Grok Apollo film** → qualified human landing visit → actual asset_id, posted URL and UTMs unavailable → no traffic attribution asserted → **UNKNOWN** → Grok/Praxxis.
3. **Evidence Desk** → free Apollo investigation → malformed ARIA could block later desks, source links could be silently changed → stage-guarded CSS/JS, source+CTA contract and ChronologyRail → **PASS local synthetic / HOLD staging** → Apollo QA / QD.
4. **Paid order** → realized net revenue/1,000 qualified human sessions → 7-/30-day qualified sessions, confirmed merchant orders, fees and refunds unavailable → no made-up metric → **NOT COMPUTABLE** → Claude/Commerce.

Measurement must preserve approved #820 UTMs and business events, but **this component adds no scripts or measurement events**. Source-of-truth issues #150, #818 and #820; TASK-008 remains Grok/Praxxis-owned. No social, WordPress, email, affiliate, analytics, checkout or spending actions.

## Release gates and reproduction

1. Fetch exact original PR #158 and R404 source into local read-only trees, then run: `python qa/assemble.py --pr158-root /path/to/pr158/research-desk --r404-root /path/to/apollo-r404 --out /tmp/fv-r407-candidate` and verify full PHP contract against real template. Never use fixture content in staging.
2. On the explicit staging page, inspect true delivered final HTML and CSS/JS responses, HTTPS/CSP, dynamic-shortcode lifecycle, caching, competing assets, real WordPress styles, no-JS, source links, CTA/redirect and responsive layouts.
3. Run genuine checksum-verified axe-core, independent screen readers, 400% native zoom and performance LCP/CLS/INP at browser navigation; review QD and hosted CI against exact GitHub HEAD.
4. Maintain **HARD HOLD** until founder explicitly approves independent release governance. No PR merges and no WordPress installations were performed.
