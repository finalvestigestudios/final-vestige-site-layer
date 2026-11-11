# Apollo Evidence Atlas R292 — direct NASA source route and measurable border contrast

**DRAFT STAGING / HARD HOLD / not approved for production.** This isolated Apollo-only branch is stacked on draft R291 (PR #2083, exact parent `a50e23afe37f02b6481f9ea9a91a0ff018371013`). It does not touch homepage PR #49, Research Desk PR #158, the homepage lead's branch, production WordPress/settings, Grok content/posting, analytics, checkout, merchant offers, emails or paid services.

## Reproduced accessibility problem and reader-path change

R291's component border token `#665b49` against its source-gallery background `#20252a` was only **2.323:1** (sRGB/WCAG contrast formula). The borders distinguish archival cards and source boundaries, so a conservative WCAG 1.4.11 3:1 non-text visibility target is appropriate. R292 changes the **scoped component** `--line` color to `#81745f`. Actual Chromium computed-style checks record minimum **3.381:1** across the examined fixed dark card surfaces (3.595 on EvidencePlate, 3.381 on gallery). This does not constitute an axe-core or complete WCAG audit.

An early native in-page link now takes source-intent visitors directly from the introduction to the **existing focusable first NASA catalogue entry**, without needing to scroll through the chronology and Board-authority reconciliation. The record's existing return link navigates back to EvidencePlate 1. The route works with JS disabled, for keyboard and touch, and across repeated shortcode instances without new IDs or Tab stops. It adds **no outbound commerce, second investigation CTA, new NASA record, map pin, media, script or network request**. The single narrative continuation remains the free Apollo investigation.

## Historical custody and rights

The NASA primary [Board narrative](https://www.nasa.gov/history/Apollo204/narr.html) distinguishes January 27 oral authorization and February 3 written confirmation. The [1967 proceedings](https://www.nasa.gov/history/Apollo204/proceed.html) place the meeting on January 28 and receipt of a January 28 memorandum on January 31. The [later NASA safety summary](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) uses a different establishment date. R292 changes **no historical text, dates, source-URL allowlists, SHA-256 evidence seals, or editorial status**. NASA [advertising restrictions](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) still apply. No photographs, insignia or astronaut likenesses introduced.

## Execute source-controlled QA from repository root

```sh
php -l experience2/apollo-r281/apollo-source-experience.php
php experience2/apollo-r290/qa/php_gate.php
python experience2/apollo-r290/qa/browser_gate.py /tmp/r292-inherited-r290
python experience2/apollo-r291/qa/source_controlled_gate.py /tmp/r292-inherited-r291
python experience2/apollo-r292/qa/source_controlled_gate.py
# Extended R292 Playwright/print audit is included in the deterministic evidence archive.
# Strict HTTP/CSP/axe gate should fail closed when navigation or axe are unavailable:
python experience2/apollo-r290/qa/http_axe_gate.py /tmp/r292-http
```

Local results: PHP syntax PASS; inherited PHP 38/38 PASS; inherited R290 Chromium 10/10 PASS; inherited R291 Chromium 10/10 PASS with 2 PDFs; new committed R292 Chromium 10/10 PASS; extended R292 Chromium 10/10 PASS, widths 320/390/768/1440/1920, JS on/off, focus/return, keyboard, touch-emulation, forced colors, reduced motion, 200–400% text resizing, 2 Chromium printed PDFs, 2 reproducible screenshots. R291 insufficient border contrast is a negative control. Offline document rendering is **not** installed WP or field Core Web Vitals. The strict HTTP/CSP/axe test exited **2/BLOCKED**: `ERR_BLOCKED_BY_ADMINISTRATOR`, axe-core unavailable, LCP/CLS unmeasured. No manufactured pass.

Outstanding: genuine axe-core; independent VoiceOver/NVDA; installed WordPress/Assembler including synced blocks and shortcode style preflight; actual HTTP+CSP; Firefox/Safari and browser-UI zoom; hosted exact-head CI; navigation and real-user p75 LCP/CLS; editorial NASA/source/rights acceptance; and founder release authorization. The next step is a governed staging validation, **not** deployment.

## Conversion-first custody (Issue #820 and charter #818)

Grok actual published Apollo long-form/Shorts asset ID + landing URL must be verified independently in existing TASK-008 handoff. Controlled path: creator asset with valid actual UTM → source-first Apollo Atlas → primary NASA record → **one** free Apollo investigation → *only if independently approved and buyer-relevant*, separately disclosed Mini Museum guide → merchant-verified paid order → refund/fees-adjusted realized net. The offer's affiliate acceptance, allowable claims, product fit, attribution and settlement remain unverified. No conversion lift, paid sale, confirmed subscriber or net revenue is established from this browser QA. Governing KPI: independently verified realized net revenue per 1,000 qualified human sessions in 7/30-day cohorts, with low-sample warning.

Ownership: Grok produces/distributes, Praxxis independently reviews social and attribution inventory, Claude owns production analytics/commerce, Apollo owns this evidence experience, founder controls releases/spend. Do not overwrite others' queue or frozen homepage branches.
