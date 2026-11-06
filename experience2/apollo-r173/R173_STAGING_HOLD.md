# R173 — Apollo Research Desk source-role clarity | STAGING HOLD

**Engineering purpose:** The original PR #158 Research Desk captions six NASA archive photo identifiers alongside written technical findings. Those are different evidence types. R173 explicitly separates a photograph's archival identity from the Apollo 204 Review Board or NASA institutional history article used for the written claims.

## Actual source and exact custody

- Source branch: `feature/experience-2-source-ledger-pilot-20261030`; original Research Desk template blob: `403d128c57b9bc82dac7c619651689070edef86c`.
- R173 HTML: exact original six-card template plus one visible source-guidance aside and six source-role notes. A source-to-candidate removal roundtrip was byte-identical; all original ordered href destinations, captions, article copy, card IDs, search data, links, and the single **Read original investigation** action remain unchanged. No new scripts, links, forms or map pins.
- Scoped optional stylesheet included separately; without CSS/JS the proof notes and links remain readable. Native `<details>` works via keyboard/touch without custom JavaScript.
- Original Research Desk PR #158, frozen homepage PR #49, WordPress Page 2017, analytics scripts, merchants and Grok production are **unchanged**. This is additive code on a branch stacked on R172 PR #1297; do not merge or deploy.
- This derived Research Desk template must be reviewed and packaged as a **standalone staging plugin candidate** by Claude separately; this PR does not enable the `[fv_ex2_research_desk]` shortcode on the site.

## Independent local browser witness (representative fixture only)

A Python source-custody transform and Playwright acceptance runner are included in the companion downloadable evidence package, not this PR. Six unit tests passed; deliberate malformed source/CTA mutations were rejected; Chromium ran 12 contexts at 320, 360, 390, 768, 1440 and 1920px with JS enabled/disabled, search, keyboard-native details, mobile touch emulation, reduced motion and forced colors. **124 assertions**, no page errors, no observed horizontal overflow; 6 screenshots repeated with exact matching SHA-256 hashes. The local test fixture is NOT this exact PR #158 template. The source-derivation itself used the real PR #158 GitHub blob with exact structural and round-trip checks.

**Missing:** real installed WordPress staging, real image/CDN delivery, genuine axe-core, manual screen reader, real-page LCP/CLS, production CSP and exact-head hosted CI. No claims of production CWV or commercial outcomes.

## Flagship / source and rights

Flagship remains Apollo 1 for Grok long-form and Shorts **subject to Grok's independent editorial ownership and asset evidence**; Praxxis reviews creator material. The October 1966 training image and 2017 exhibit images are NOT second-by-second photographs of the January 27, 1967 fire. NASA Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA advertising restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . These references do **not** establish paid advertising rights to astronaut likenesses or NASA branding.

## OFFER → FUNNEL → BLOCKER → CHANGE → PASS/FAIL → OWNER

| Offer / funnel | Blocker | Controlled change | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Teacher-ready Apollo evidence kit → paid order | No verified rights-cleared, sellable Apollo SKU, delivery, margin or checkout | Authenticate actual inventory and purchase route before any commercial CTA | BLOCKED, no paid conversion claimed | Claude/Commerce + founder |
| Grok Apollo long-form → Atlas | Published asset ID and qualified-session evidence not verified | Reconcile permitted asset ID/UTMs through TASK-008 and #820 | UNKNOWN | Grok/Praxxis |
| Research Desk → original investigation | Photo IDs could look like proof for fire timing/oxygen | Explicit six-card custody, optional native source explanation; keep single existing CTA | BUILT and OFFLINE TESTED; site STAGING HOLD | Apollo |
| Investigation → paid offer | No approved matching SKU | No purchase link inserted; respect narrative/commerce separation | COMMERCIAL HOLD | Founder/Claude |
| Paid orders → net / 1,000 qualified human sessions | Merchant-verified orders, refunds, fees and source-denominator unavailable | #820 7/30-day cohort reconciliation; small sample warnings | NOT COMPUTABLE | Analytics |

**Hypothesis (unmeasured):** Clear claim-to-source roles reduce trust friction and improve qualified readers' ability to reach the investigation. The only next action is **Read original investigation** until there is a verified matching product.

## Release gates

Requires independent editorial check of all six NASA photograph identities/dates, commercial-use rights adjudication if imagery becomes promotional, staging packaging + source consistency, axe-core/manual screen reader, installed-page touch/keyboard/no-JS, actual responsive image delivery, CSP/LCP/CLS, exact-head CI and founder-approved release. No permissions to change live site or launch a paid offer. Refs #150 #820 #818 and independent PR #158.
