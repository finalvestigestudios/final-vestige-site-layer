# Apollo Experience 2.0 R230 — Research Desk shortcode lifecycle

**Draft / staging-only / no installation / no production release.** Parent is Research Desk draft PR #158 at `250d7f05a4de037e73826dcf0cfaef0ec4c29383`; isolated from Atlas draft #1685 and frozen homepage #49.

## Concrete defect addressed

The original [Research Desk adapter](final-vestige-ex2-research-desk.php) relies on the top-level singular post containing `[fv_ex2_research_desk]` before `wp_enqueue_scripts`. Dynamic/reusable/nested block rendering can call that shortcode after the head has been emitted, leaving its CSS unprinted. Rendering more than one shortcode repeats fixed IDs, causing label, ARIA and fragment collisions.

`fv-ex2-r230-runtime.php` is a **mutually exclusive replacement candidate** (do NOT activate it alongside the original). It pre-enqueues assets for ordinary shortcodes, enqueues at the point of render for nested blocks, emits a single approved external CSS link if the head has already printed, and only recovers the optional external JavaScript after the footer. It assigns a distinct identifier namespace to each second-and-later instance and rewrites all matching internal references. It never changes the bundled six NASA records, their source URLs, dates or limitations. A missing/empty template returns the original free Apollo investigation link, with no JavaScript requirement.

## Local test evidence — honest boundaries

The independent local evidence package from this sprint executed the **actual R230 PHP file** with a PHP WordPress-function shim and a **synthetic six-card fixture matching the R158 ID/data-attribute contract** (the fixture is *not* the exact GitHub R158 template). Five PHP cases passed: normal preflight, nested shortcode with late CSS, duplicate shortcode IDs and single asset injection, post-footer optional JS recovery, missing-template fallback. Actual Playwright Chromium passed 10 viewport/JS contexts (320, 390, 768, 1440, 1920 CSS px, JS on/off); keyboard and touch native disclosures, independent two-instance search filters, no-JS full record visibility, zero offsite requests, reduced motion, forced colors, no duplicate IDs or horizontal overflow. A 256 CSS-px reflow fixture also passed (simulates the *layout width* after 400% zoom at 1024px, **not actual UI browser zoom**). Two executions generated 10/10 identical screenshot hashes and identical deterministic receipts.

The JS inside the local fixture is a **behavioral copy of the original R158 filter, not a byte-identical R158 JS file**. Synthetic CSS was used. This is component acceptance of a known rendering contract, **not** actual NASA-source content QA, a verified production-stylesheet rendering, installed WordPress/Assembler compatibility, or WCAG certification. Genuine axe-core, NVDA/VoiceOver, real browser zoom, server HTTP navigation, hosted CI, LCP/CLS field measurements and founder release approval are missing. R198 ancestry discrepancy also remains open.

## Explicit isolation and acceptance gate

1. QA must test one and multiple Research Desk shortcodes in **installed staging WordPress** with the current Assembler theme and reusable/dynamic blocks, checking that late `<link>` behavior is allowed by theme/CSP and no CSS/JS duplicates appear.
2. Manually inspect full original six-source R158 template: source IDs/URL custody, image rights/credit, contact with the NASA Apollo 204 Review Board and uncertainties. NASA historical access is **not** an automatic commercial-media license or endorsement.
3. Complete axe-core WCAG 2.2 AA automated baseline, real keyboard/touch and NVDA/VoiceOver, actual zoom and media QA; obtain exact-head hosted CI and independent QA. No merge/release without founder authorization.
4. Do **not** activate both original and candidate plugins. Do not edit homepage PR #49, live WordPress, analytics, paid offers, Grok's publishing queue or TASK-008.

## Conversion-first handoff (Issue #820)

**One visitor action:** verified Grok Apollo documentary (asset ID/landing URL not yet substantiated) → NASA-backed Research Desk → **Read the original Apollo 1 investigation** (free). Prospective Apollo educator evidence dossier is a **business hypothesis**, not an approved sellable SKU or verified checkout; do not insert unrelated affiliates into this historic case. Founder/Claude first validate rights, deliverable, price, fulfillment and true merchant-order reporting. Key KPI is realized net revenue per 1,000 qualified human sessions over 7/30 days, using verified orders net of refunds/fees; no revenue or conversion is attributable to this staging change.

**OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:**
- Educator dossier → paid purchase → no approved SKU/rights/checkout → hold commercial activation → **BLOCKED** → Founder/Claude.
- Grok documentary → source page → no published Apollo asset ID / campaign evidence → TASK-008 reconciliation → **UNVERIFIED** → Grok/Praxxis.
- Source Desk → free original investigation → late shortcode assets and duplicate IDs → R230 alternative shortcode runtime → **PHP/LOCAL FIXTURE PASS; STAGING BLOCKED** → Apollo.
- Verified paid orders → net revenue → no authenticated orders/fees/refunds, no qualified-session denominator → 7/30-day reconciliation → **NOT COMPUTABLE** → Analytics/Commerce.

Source: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/); [NASA advertising restrictions](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/). [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [Business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).

**RELEASE: HARD STAGING HOLD.** No live content, email, affiliate, social, analytics or paid changes.
