# Apollo Experience 2.0 R248 — WordPress head-order fix / release HOLD

**2026-11-09 PT. Source-controlled staging only.** Parent R247: `fea82ffd0459d5d609c8abac5784af4bb5f7186b`. Frozen homepage PR #49, original Research Desk PR #158 and Grok TASK-008 are unchanged.

## Measurable defect

The R247 shortcode injected the trusted CSS into the page whenever `wp_style_is(..., 'done')` was false, **even when evaluated before WordPress `wp_head`**. WordPress could then also print the independently queued stylesheet, duplicating CSS. A duplicate stylesheet increases DOM/CSS weight without adding historical or commercial value and can complicate style precedence.

R248 conditions the once-only inline fallback on `did_action('wp_head') > 0` (with a conservative compatibility fallback for minimal legacy test shims). Before head: enqueue stylesheet and emit **zero** inline copies. After head and before stylesheet printing: **one** trusted inline copy. Already printed: no inline copy. Missing/modified CSS is skipped; missing/modified evidence template fails to the original investigation. Both source and optional assets continue to use exact Git blob seals.

## Reproduction and evidence limits

- Source: `final-vestige-ex2-research-desk.php`, `qa/r248_wordpress_head_order.py`.
- Exact-source regression is committed and is designed to run against the six original NASA records in a full repo checkout; **not executed in this workspace** because the full exact historical HTML/CSS/JS was not locally mounted.
- Local isolated **synthetic six-record fixture**, with explicitly test-only pin substitution, executed the **exact updated PHP bytes** under simulated WordPress head-order cases: before head (0 inline CSS), after head (1), already printed (0), source mutation and missing HTML fallback.
- Real local Playwright/Chromium synthetic PHP-to-DOM: 320/390/768/1440/1920px × JS-on/off, 10 contexts/run × 2 independent runs = 20, with native keyboard/touch disclosure, optional search, 6 records, link custody, no horizontal overflow, no external requests, 4/4 identical screenshot pairs; receipts byte-identical.
- Regression sensitivity: temporarily removing the new guard made the **before-head** test fail. Temporary regression mutation is not committed.
- Does **not** establish genuine axe-core, installed WordPress/Assembler, browser-interface zoom, screen-reader compatibility, network image rights, hosted CI, production LCP/CLS or verified commercial success. Do not promote this synthetic-browser evidence into real-site acceptance.

## Flagship visitor experience and conversion hold

One qualified audience: Grok long-form space-history/documentary viewers seeking genuine Apollo primary evidence. One original free next action: **Read the Apollo 1 investigation**, after the NASA-anchored Research Desk/Atlas source trail, with source limitations and chronology intact. The Apollo 204 Board says an electrical arc was the most probable initiator, **not a conclusively identified ignition source**: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/

**Conditional commercial hypothesis only:** space-history artifacts at Mini Museum, never inside the primary NASA source narrative; no paid CTA until founder/Commerce validates FV-specific approved partner eligibility, approved creative rights, context-appropriate FTC disclosure, checkout fulfillment and merchant-reported settled conversion. NASA branding must not imply endorsement: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

A published Grok Apollo immutable asset ID, post URL, rights/placement and actual UTM landing link have not been verified; Praxxis/Grok retain TASK-008. No addition to their queue. Claude retains core WordPress/analytics production; founder retains publication/spending/merchant release authority.

**Success measurement contract:** qualified human sessions from actual `utm_source / utm_campaign / utm_content=asset_id` → landing → free investigation CTA → optionally merchant CTA after authorization → verified paid order or merchant-confirmed affiliate commission → refunds/fees/costs → realized net revenue/1,000 qualified human sessions (7/30-day cohorts; tiny-N warning). Missing settled transactions and attributed qualified-session denominators mean KPI **NOT COMPUTABLE**, not zero. No custom measurement script installed.

## Blocked release gates

Exact-original NASA template browser run, full WordPress/Assembler integration with nested reusable blocks, genuine axe-core, keyboard/screen-reader independent QA, source/imagery commercial clearance, R198 ancestry issue, green hosted CI, independent site QA, and founder staging/release sign-off. **NO merge, deploy, CMS setting/content change, creator posting, affiliate activation, email, analytics vendor or spend.**

See Issue #150 for Apollo implementation and Issue #820/#818 for founder's commerce rules.
