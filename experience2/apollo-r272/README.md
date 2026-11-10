# Apollo Research Desk R272 — reusable-block asset preflight (DRAFT / HARD HOLD)

**Scope:** Experience 2.0 #150; Research Desk PR #158; conversion #820 / charter #818. This additive WordPress plugin is *not* installed, activated, merged or cleared for release. Parent is R271 PR #1962. Frozen homepage PR #49 and the independent lead-homepage lane are untouched.

## Found defect and narrow change

The actual PR #158 `fv_ex2_rd_assets()` only calls `has_shortcode()` on the top-level singular post's `post_content` at `wp_enqueue_scripts` priority 20. A Research Desk shortcode held exclusively inside a separately stored, published WordPress `core/block` reusable block is not present in that string. Therefore the markup can be server-rendered but its CSS/JS can be missed (candidate for unreadable/mobile-awkward presentation, not loss of primary sources).

`rd-reusable-preflight.php` attaches at priority 21, *before the page head*, recursively scans only parsed block reference pointers in the singular post or other published `wp_block` records, and enqueues the **original** Research Desk handles and original plugin paths once. It never renders blocks, modifies saved posts, writes WordPress settings, adds JavaScript analytics or inserts an offer. Its read-only scan is bounded by 32 unique refs, 8-depth recursion, and a 500-node budget. On a missing plugin, source hash drift, invalid ref or cycle it does not load optional assets; the original server-rendered evidence remains available.

Original CSS SHA-256: `38676056e2aee5e3db285072bd847b5b5438832d76d9c451e4f56d27134ee291`; original JS SHA-256: `22a9ab56f3265aece14f76f1cab557ecfb096530e4802fa4dcbc0960fe34533d`. These are guardrails, not proof of downstream NASA image rights.

## Executed, reproducible local QA

- `php -l rd-reusable-preflight.php`, `php -l qa/preflight_gate.php`: PASS.
- `php qa/preflight_gate.php`: **20/20** API-shim scenarios PASS, using the unchanged original PR #158 functions and R270 filter; includes direct shortcode, referenced reusable and nested reusable blocks, multiple refs, wrong-type/draft/missing refs, cycles, depth cap, duplicate enqueue, authentic source, and a negative control that reproduces the original asset-discovery gap before R272 repairs it.
- `python qa/browser_gate.py <outdir>`: **10/10** authentic-source Chromium contexts PASS per run at 320, 390, 768, 1440, 1920px × JS enabled/disabled; checks 27 unique IDs, 39 NASA anchors, 3 unchanged free-investigation links, accessible names from genuine Chromium CDP AX tree, keyboard/no-JS native disclosures, independent JS search, no horizontal overflow, and no external requests.
- Three local independent browser runs produced the **same receipt SHA-256** `1415fe6224ae6974e2ce9fb6af0a1a2434204e3f4a79b8bea9716d2c39dc1f0c`; screenshots at 390/1440 with JS on/off match between runs.
- All four underlying original PR #158 Git blob IDs and the R270 filter blob are verified before the browser runner can start. Exact original Research Desk files reside on the R271 parent branch, not copied or modified in R272.

**Limitations:** the PHP tests simulate WordPress's APIs and block parser, and Playwright runs `set_content()` offline. No installed WordPress/Assembler site, full Gutenberg block parser/cycle semantics, reusable-pattern frontend HTTP/CSP, theme interactions, independent screen reader, genuine axe-core, browser-UI zoom or field/p75 LCP/CLS is established. Do not report a production or CI pass. Dynamic theme parts and block patterns that are generated only at render time remain outside this preflight's discovery reach.

## Evidence and rights custody

The original 6-record Research Desk remains unchanged. NASA's Apollo 204 Board found the most probable initiator was an electrical arc, but **no single ignition source conclusively identified**: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA disallows misleading commercial endorsement and certain uses of agency identifiers/astronaut likenesses: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Do not invent Atlas pins, historical edges or image licenses.

## Commercial gate — offer → funnel step → blocker → experiment → evidence → owner

| Offer / funnel | Blocker | Proposed verification | Evidence today | Owner |
| --- | --- | --- | --- | --- |
| Optional disclosed Mini Museum guide → merchant purchase | Approved affiliate eligibility, checkout, settlement, refunds/fees missing | Reconcile signed merchant arrangement + verified orders | **COMMERCIAL HARD HOLD** | Founder / Claude commerce |
| Grok Apollo long-form → Evidence Atlas | No authenticated published Apollo asset ID and native clickable link in TASK-008 | External-owner read-only matching | **NO VERIFIED MATCH** | Grok + Praxxis |
| Atlas / Research Desk → original free article | Stored reusable block can miss CSS/JS pre-head | R272 source-pinned preflight | **LOCAL PHP/CHROMIUM PASS; WP UNTESTED** | Apollo independent lane |
| Paid orders → realized net revenue/1k qualified human sessions | Qualified-human source cohorts and paid reconciled orders absent | Native/consent-safe existing measurement, 7/30d cohorts | **NOT COMPUTABLE (not zero)** | Claude analytics / founder |

The only editorial CTA remains the original free Apollo investigation. The separately reviewed buying-guide postscript is nonactivating. No new analytics, payment links, social posts, CMS writes, paid calls, emails or public deployment are permitted by this PR. All release gates require exact-head CI, native WordPress/Assembler, independent axe/AT/browser zoom, HTTP/CSP and performance, source/rights, merchant and founder acceptance.
