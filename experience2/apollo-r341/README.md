# Apollo Experience R341 — reusable-block asset preflight (DRAFT / HARD HOLD)

An isolated, stacked change to `../apollo-r340/apollo-accession-gallery.php`. The existing R340 `wp_enqueue_scripts` preflight searched only top-level singular post content. A composite or gallery shortcode inside a **WordPress core/block reusable pattern** could render all source HTML but fail to enqueue its CSS. R341 scans the existing content and bounded referenced `wp_block` content before `wp_head`; it does **not** render a block, write a post, modify the homepage or add analytics. The six-source ChronologyRail and four-link NASA accession gallery are unchanged.

## Exact scope and reproduction

- Direct composite shortcodes enqueue two scoped styles; gallery-only enqueues one; irrelevant posts enqueue zero.
- Recursively inspect `core/block` references, with cycle detection (seen IDs), depth cap 5, reference cap 24, 500KB content guard, and `wp_block` type check. Missing/foreign/cyclic references enqueue nothing unless another valid shortcode is present.
- CSS enqueuing for arbitrary dynamic blocks, template parts and patterns not expressible as `core/block` remains **unverified**; actual installed WP/Assembler and caching acceptance is mandatory.
- `php experience2/apollo-r341/qa/reusable_block_smoke.php` tests twelve isolated WP-function stub scenarios.
- `python experience2/apollo-r341/qa/browser_gate.py` runs real Playwright Chromium on PHP-produced HTML at 320/390/768/1440/1920px, JS/no-JS, keyboard, reduced motion, touch/forced colors; exports JSON and two screenshots. Chromium must be installed and accessible via `CHROMIUM` (defaults to `/usr/bin/chromium`). `FV_R341_OUT` selects output directory.
- Browser fixture LCP and CLS are **local values only**, not production Core Web Vitals. No live HTTP/CSP, axe-core, independent screen readers, Firefox/WebKit, WordPress, paid checkout or Grok campaign certification.

## Editorial and business control

NASA original Apollo 204 Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . Photographic accession pages and media rights remain link-only/contextual; individual reuse rights are **not** granted. There are no geographic pins/edges or additional commerce links.

Controlled path: authenticated Grok Apollo history film (**asset ID not yet established**) → staged sourced chronology/gallery → existing free investigation → only an independently approved rights-cleared payable Apollo educational product (**not yet authenticated**). One existing editorial CTA remains. Conversion is **not proven**. Net revenue/1,000 qualified human sessions cannot be calculated without paid orders, refunds, fees and qualified sessions. No new analytics script or WordPress/public changes.

Owned by Apollo research lane under Issues #150 and #820. Stacked on R340 PR #2371; does not modify frozen homepage PR #49, Research Desk PR #158, Grok TASK-008 or any production site. Do not merge/deploy without independent QA, founder approval and relevant lead reviews.
