# Apollo R343 — standalone chronology CSS preflight (staging only)

**Source of truth:** [Experience 2.0 #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Stack on R342 [#2384](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2384); do not merge, deploy, alter homepage PR #49, change Research Desk PR #158, or override Grok/Claude roles.

## Reproduced real integration gap

R339 registered the standalone shortcode `[fv_apollo_chronology_r339]` **without its own pre-head stylesheet enqueue**. R340/R341's stylesheet preflight only recognized their gallery/composite shortcodes. A standalone WordPress shortcode could therefore render complete semantic NASA chronology **without the scoped CSS**.

This patch adds a bounded, read-only `fv_apollo_r339_in_content()` and `fv_apollo_r339_enqueue()` to the existing R339 plugin. It detects direct shortcode uses or nested `core/block` reusable references, with a five-level depth limit, 24 unique-reference cap, 500KB content limit, post-type check, cycle protection and missing-reference fallback. Only the **existing** `fv-apollo-r339-chronology` stylesheet handle is enqueued; no JS, tracking, content changes or commerce. The separate R340 composite/gallery CSS routing is unchanged. Standalone HTML remains meaningful without styles/JavaScript.

## Executable QA

Run from repository root with PHP, Python Playwright and Chromium:

```bash
php -l experience2/apollo-r339/chronology-rail.php
php experience2/apollo-r343/qa/standalone_preflight.php
python experience2/apollo-r343/qa/browser_gate.py
FV_R342_OUT=/tmp/apollo-r342-check python experience2/apollo-r342/qa/acceptance.py
```

R343: **16/16** simulated WordPress preflight cases; **11/11** real Chromium cases (320/390/768/1440/1920px, root text 100–400%, no-JS, touch, reduced motion, forced colors, keyboard native disclosures, fragment links, hitboxes, multiple instances); plus missing-style negative control. R342 regression re-executed: 10 Chromium contexts, 8 unsafe mutation rejections. Real local fixture LCP/CLS observations are in QA receipts; not production Core Web Vitals.

**Genuine axe-core:** the test supports `AXE_JS=/path/to/vendor/axe.min.js` but the package was not available in this execution. AXE=**NOT_EXECUTED**, not a simulated or fabricated pass. Independent screen readers, Firefox/WebKit, installed WP/Assembler/CDN, actual HTTP CSP and hosted exact-HEAD CI remain blocked. No WordPress install or production acceptance claimed.

## Evidence custody

Original [NASA Review Board investigation](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html) and [chronology](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/chro.html) establish source boundaries. [Later NASA history](https://www.nasa.gov/history/55-years-ago-the-apollo-1-fire-and-its-aftermath/) is separately classified. The Board did not conclusively identify a single ignition source. Four R340 contextual photo accessions stay link-only; no commercial imagery rights presumed, no synthetic map locations or relationships.

**Release: HARD HOLD** pending installed-WP/browser accessibility acceptance, hosted CI, NASA/editorial rights review, authenticated payable offer and founder approval.
