# Apollo R185 — early WordPress stylesheet lifecycle (draft / production hold)

**Ownership and scope:** isolated Apollo Experience 2.0 evidence lane, Issues #150 / #820 / #818. Stacked on R184 PR #1369 at `eac7b2bff411066f0d115c5ee8eac9d671cc40d0`. Neither homepage frozen PR #49, homepage lead branch nor original Research Desk PR #158 is modified. Grok owns video/social; Praxxis owns external creator review; Claude owns core WP production and analytics; founder approves release/spending/posting.

## Defect and change

R184 registers/enqueues CSS **inside the shortcode render callback**. On normal `the_content` rendering, WordPress has already printed `wp_head`. A style enqueued at that point cannot be guaranteed present in the document head; footer placement or missing/late styling is dependent on theme/runtime. The R184 static and fixture checks did **not** simulate that event ordering. WordPress documentation: https://developer.wordpress.org/reference/functions/wp_enqueue_style/ .

R185 builds from R184's SHA-verified, source-controlled asset generator and changes only the PHP delivery mechanism:
- On `wp_enqueue_scripts` preflight, for a singular queried `WP_Post` whose content contains `[fv_ex2_apollo_atlas]`, SHA-check the immutable fragment/CSS, then enqueue the stylesheet **before** normal head printing.
- Keep the rendered content source-identical: four dated chronology events, four EvidencePlates, four NASA gallery/source entries, eight HTML `details` SourceDrawers and exactly one relevant **free original investigation** link.
- No global stylesheet loading on unrelated posts. No new external JS/fonts/images, analytics tags, paid affiliate, forms, or commerce promises. CSS remains locally generated and scoped.
- Invalid/missing asset, shortcode unexpectedly rendered only after `wp_head` (such as widget/programmatic late injection), or second shortcode instance → visible accessible text fallback to the original investigation; fail open to **historical reading**, fail closed to displaying broken Atlas styling/duplicate IDs.
- Uses CSS file content hash prefix for deterministic cache version. This is a staging candidate, **not** approved for real WP activation. R184 and R185 implement the same shortcode and MUST NOT be active simultaneously.

## Build and isolated verification

From repository root:

```bash
python experience2/apollo-r185/build_r185.py
php -l experience2/apollo-r185/dist/fv-ex2-apollo-r185.php
python -m unittest discover -s experience2/apollo-r185/qa -p 'test_*.py' -v
python experience2/apollo-r185/qa/browser_acceptance.py --out /tmp/apollo-r185-runA
python experience2/apollo-r185/qa/browser_acceptance.py --out /tmp/apollo-r185-runB
```

Build requires R183 + R184 checked out and Python `beautifulsoup4` / `tinycss2` installed; tests also need PHP CLI and Playwright + system Chromium. `dist/` is generated, contains an unpublished plugin assembly, and must not be installed as part of this PR.

**Local source-equivalent proof, 2026-11-07:** using earlier archived R184 asset bundle, PHP lint PASS, Python mock lifecycle **10/10 PASS**, real Playwright Chromium mock-shell **160/160 assertions per pass**, two runs, 12 browser contexts spanning 320–1920px, no-JS and no-CSS, keyboard/mouse/touch, reduced-motion, forced-colors, 200% zoom; screenshots **12/12 identical hashes**. Mock lab LCP 72–192ms, CLS 0. This was not an installed WordPress execution, exact-head CI, genuine axe-core, AT audit, actual CDN/CSP, or production CWV.

## Release criteria / known limitation

The shortcode must be present in the queried post content at `wp_enqueue_scripts` time; blocks/widgets with dynamically injected shortcode after this hook use the free fallback rather than risk a broken component. Verify actual staging theme/shortcode rendering order, CSS head delivery, CSP, cache/minification, WordPress PHP version, accessibility via genuine axe-core and screen readers, 320–1920px first paint, LCP/CLS under realistic network/CPU, no-JS/no-CSS and strict rights/source review. Fail the release if any gate is missing. A WordPress installed staging URL and exact-head CI are **not** established.

## Commercial/creator contract

Flagship: Apollo 1. Grok YouTube long-form/Shorts → source-grounded Atlas → **Read original investigation** (only enabled CTA). Educators are a plausible high-intent segment for an original rights-cleared classroom dossier, but **no existing verified purchasable Apollo SKU**, approved checkout, affiliate commission, attributed Grok Apollo asset ID or paid order has been established. Do not substitute an unrelated affiliate or claim views/clicks are sales. Commerce decision comes after product inventory/rights/checkout verification; use #820's qualified-human sessions → CTA → verified leads → paid orders → fees/refunds → realized net revenue, 7/30-day cohorts, and tiny-sample confidence flags. No production, content, social or merchant writes are authorized by this PR.
