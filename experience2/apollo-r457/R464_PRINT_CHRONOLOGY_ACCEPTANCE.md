# Apollo R464 — chronological source custody in print and PDF

**Status: DRAFT / production HARD HOLD.** Issue #150; commercialization #820 / #818. Isolated child of R463 PR #3049. Does not edit frozen homepage PR #49, Research Desk PR #158, WordPress, Claude's analytics, Grok's content queue, or Praxxis handoffs.

## Actual change

- The three NASA chronology moments now render semantic `<time datetime>` values with **month-only** precision for the January 1967 crew photo (`1967-01`) and day precision for the January 27, 1967 fire and January 27, 2017 tribute opening. Date parsing rejects invalid values and inappropriate precision without inventing a portrait day.
- Existing native `details` source drawers often print closed, silently omitting all three chronology citations. New print-only HTML retains source kind, full **clickable** NASA URI and explicit uncertainty in PDF exports, even with JavaScript disabled or a screen filter active.
- Long source labels include `<wbr>` opportunities while the underlying `href` remains unchanged. This repairs **320px no-CSS progressive-degradation overflow** observed in adversarial local Chromium QA.
- Nine distinct NASA URLs (six archival cards plus three chronological references) and one free FV investigation URL survive the PDF export. No NASA images, speculative geographic pins, additional CTA, signup, tracking, checkout, analytics, affiliate, sale or new service.
- R461 committed PDF checks updated to match the new nine NASA + one free link custody. New R464 source-controlled Chromium smoke tests semantic dates, PDF links, keyboard disclosures, no-JS, 320–1920px, filtered-print restoration. The larger R464 local acceptance harness and R462 missing-asset suite were also executed.

## Official sources, uncertainty and media permissions

- [Apollo 204 Review Board — NASA](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) — most probable electrical arc, **not a conclusively identified single spark**.
- [Apollo 1 crew photograph retrospective — NASA](https://www.nasa.gov/image-article/apollo-1-crew-honored/) — January 1967 without a proven day or accepted S67-19766 ID mapping.
- [Apollo 1 crew tribute — NASA](https://www.nasa.gov/history/apollo-1-crew-honored-in-new-tribute-exhibit/) — 2017 museum event, **not a 1967 fire photograph**.
- [NASA advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) — editorial source access does **not** establish image resale, likeness permission, promotional use or endorsement.
- The KSC-20170124-PH_KLS01_0129 link mapping is still unverified. Keep source acceptance HARD HOLD; do not fabricate the archive ID, historical date, licensing or geographic metadata.

## Executed local acceptance, November 18, 2026

- `php -l` PASS; 26/26 source/security tests PASS; 6/6 optional-file contract tests PASS.
- R464 expanded, *local* Playwright/PyMuPDF: **64/64 PASS**, across seven widths 320–1920px, JS enabled/disabled, keyboard, touch, forced colors, reduced motion, device scale 200%, filtered print, five tagged PDFs with ten unique link destinations, five print screenshots. R464 executed twice: PNG/PDF artifact SHA-256 files identical.
- Inherited: 21/21 browser, 14/14 print, 45/45 print filter, 43/43 amended PDF link, 96/96 progressive missing-CSS/JS, and 14/14 chronology smoke, locally PASS. R462 previously found genuine no-CSS 320px overflow; fixed with <wbr> and rerun **96/96 PASS**.
- Existing local Playwright set_content renders genuine PHP output; **NOT** installed WordPress. Even local `page.goto(http://127.0.0.1)` returns `ERR_BLOCKED_BY_ADMINISTRATOR`. Hosted staging navigation, real axe-core, navigated LCP/CLS, p75 field CWV, screen readers, exact-head CI and independent QD are NOT VERIFIED. Do not infer performance from static screenshots.
- No deploy/merge/release authority. Explicit founder approval required.

## Conversion-first funnel

**High-intent segment:** classroom educators and homeschool teachers evaluating source-based Apollo history activities. **Actual sellable offer:** none independently verified; a proposed original educator dossier is a **product hypothesis**, not a purchase option.

**OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER**
1. Original rights-cleared educator product → paid checkout → verified SKU, consumer purchase, delivery, refunds/rights missing → withhold paid CTA → HARD HOLD → Founder/Claude Commerce.
2. Grok published Apollo long-form/Shorts → qualified human website landing → actual published asset_id, UTM, destination, guest-phone proof missing → request evidence through existing TASK-008 without creator interference → UNKNOWN → Grok/Praxxis.
3. Evidence Atlas → printable lesson provenance → free investigation → the three chronology NASA links were lost in default print/PDF and unstyled 320px could overflow → nine NASA links and one relevant free CTA preserved → 64/64 local PASS, hosted HOLD → Apollo QA.
4. Independently verified order → refund/fee-adjusted net revenue per 1,000 qualified human sessions (7/30-day cohorts) → no qualified denominator, settlement, fees, refunds or orders → NOT COMPUTABLE → Claude/Founder.

Hypothesis: independently inspectable print citations reduce educator trust friction and improve qualified progression. No sale, confirmed lead, attributed session, lift or realized revenue established.
