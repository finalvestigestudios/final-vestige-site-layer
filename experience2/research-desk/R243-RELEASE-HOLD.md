# Apollo Experience 2.0 / Research Desk R243 — nested-shortcode fail-open

**STAGING-ONLY DRAFT. NOT LIVE.** This patch is stacked on the unmerged Research Desk PR #158 (base commit `250d7f05a4de037e73826dcf0cfaef0ec4c29383`), not on frozen homepage PR #49. It modifies only the isolated Research Desk PHP adapter and adds `qa/r243_core.py`; the six NASA evidence records, CSS, search JS and URLs are unchanged.

## Actual failure addressed

The v0.0.3 adapter enqueued CSS and optional JS only when `has_shortcode()` detected a literal shortcode in the top-level singular post. Reusable blocks, dynamic shortcodes and theme template parts can render `[fv_ex2_research_desk]` without that literal in `post_content`, so the Research Desk could appear without its stylesheet. Rendering the same template twice also duplicated fixed `id`, `for`, `aria-controls` and `aria-labelledby` references.

The v0.0.4 staging adapter still opportunistically pre-enqueues assets for ordinary posts, but **also enqueues at shortcode render**. When the theme has not printed its style handle, it embeds locally bundled CSS once as a late fallback. It rejects CSS containing `</style`, `<script`, `@import` or `url(...)` before emitting inline content. If CSS is missing, static evidence stays readable. If the template is missing, the free original-investigation link remains the fallback. Each subsequent shortcode instance receives a deterministic identifier suffix, keeping all bundled label and ARIA references unique. Search remains optional and scoped to each root; no remote JS, images, analytics, commerce, geo or shortcode attributes are injected.

**CSP caveat:** an inline `<style>` can be prohibited by a stringent site Content Security Policy; in that case the records still render as HTML. Actual installed WordPress must verify WP output sanitization, caching, CSP and its style-print lifecycle. This is NOT verification of WordPress or Assembler compatibility.

## Reproduce source-controlled tests

```bash
php -l experience2/research-desk/final-vestige-ex2-research-desk.php
python3 experience2/research-desk/qa/r243_core.py --source experience2/research-desk
python3 experience2/research-desk/qa/r243_core.py --source experience2/research-desk --fixture
```

The first run uses the **real six-record source-controlled template** from PR #158 when that branch is checked out; the second uses an explicitly synthetic six-card sample. Tested locally 2026-11-09: PHP lint PASS and synthetic fixture tests PASS for early/late enqueue, multiple-instance ID reference integrity, CSS-guard rejection and missing-template fallback. Extended synthetic PHP → Chromium 144 Playwright acceptance separately covered 320/390/768/1440/1920px, JS/no-JS, keyboard/touch interactions, independent search-state isolation, unexpected network requests, overflow and screenshot reproducibility (10/10 identical across two runs). **Do not mislabel synthetic-fixture QA as original NASA content QA or installed WordPress QA.** Exact code Git blob parity checked for both changed PHP and source-controlled QA test.

## Evidence and conversions

The current Apollo funnel remains: unverified published Grok documentary ID → free source-backed Atlas/Research Desk → free original Apollo investigation. The proposed educator dossier is not an approved purchasable SKU, so a paid CTA is held. A separately rights-cleared product or affiliate offer must be reviewed independently with valid merchant acceptance and disclosure before any experiment. No invented traffic, lead, checkout, affiliate sale or net revenue. Cohort revenue per 1,000 qualified human sessions cannot be calculated without confirmed transactions and qualifying session attribution. Grok owns publishing; Praxxis handles external creator QA; Claude owns core production/analytics; founder approves spending and live changes. #820 / #818.

## Mandatory gates

- Real WordPress/Assembler, nested reusable-block/theme template, repeated shortcode and CSS/JS registration smoke.
- Genuine axe-core, NVDA/VoiceOver, manual zoom 200%, CSP/no-JS, mobile touch and hosted CI with independent QA.
- Verify NASA media rights and historical source ancestry; existing R198 discrepancy unresolved.
- No merge, production WP writes, affiliate activation, email, social posting or paid services without authorization.
