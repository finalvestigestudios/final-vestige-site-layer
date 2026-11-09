# EX2 private-preview admission: activation path + authenticated full-page review

**2026-11-09 · DRAFT / RELEASE HOLD.** Stacked on PR #1750 (parent `3afd95d4fae3d9cd66fb926c5cd4613f6a98dfe5`), which itself is stacked on sealed PR #224. **No WordPress writes, plugin activation, production changes, merge, paid service, or new editorial chapter.** Frozen PR #49 remains unchanged.

## Two concrete blockers corrected

**1. WordPress Playground activation path.** The former Blueprint passed an *absolute PHP-file path* to `activatePlugin`: `/wordpress/wp-content/plugins/fv-ex2-sealed-staging-preview/fv-ex2-sealed-preview.php`. The official Playground step API supports an **absolute plugin directory** or a **plugin entry file relative to the plugins directory**; an absolute entry-file path is not a documented form. The new path is `fv-ex2-sealed-staging-preview/fv-ex2-sealed-preview.php`, consistent with the mounted plugin location. The Blueprint still creates only a **private** page in `WP_ENVIRONMENT_TYPE=local`.

**2. Authenticated reviewer route.** Sealed PR #224 embeds an authenticated `admin-ajax.php` response in an iframe sandboxed without `allow-same-origin`. Sandbox opaque origins may affect first-party cookie access; the iframe also limits accurate full-page viewport testing. Do **not** add `allow-same-origin` to `allow-scripts` merely to work around this, because that weakens the sandbox boundary. The editor-only shortcode now includes a normal top-level **“Open the private full-page preview in a new tab”** link to the **same existing nonce-protected AJAX action**. The iframe remains available unchanged, and the link offers a safer, non-JS browser-review route when iframe authentication fails. It does **not** make the content public or bypass WordPress user/capability checks.

## Actually tested

- Python `unittest`: **16/16 PASS** (9 generator checks, 7 PHP-template checks).
- PHP CLI: plugin template parses; authorized local editor gets one top-level link and the existing sealed iframe; production environment, absent feature flag, absent login or absent editor capability produce **no shortcode output**.
- Shortcode browser fixture: actual PHP output composed with a visibly labeled representative wrapper in Chromium JS-disabled via `page.set_content`, before and after at 390px and after at 320px and 1440px. Before: **0 links**; after: **1 keyboard-focusable link**, no root overflow in these fixture layouts. **Not** a WordPress screenshot, real cookie test, actual staging test, WCAG certification, or field performance measurement.
- All four modified/new source files must have exact Git blob SHA checks when running the complete checkout.
- Source rights: **no new visual assets, fonts, historical claims or affiliate claims**. Existing Apollo/Franklin/NYPL rights and delivery gates remain governed by PRs #1730 and #1737.
- Security: the shortcode still fails closed in production, lacks a public `wp_ajax_nopriv_` renderer and keeps nonce, `edit_pages`, noindex and CSP checks. The new link is only rendered for authorized editors.

Reproduce with PHP available:

```bash
python -m unittest discover -s experience2/home-flagship/qa/integration/playground -p 'test_*.py' -v
php -l experience2/home-flagship/qa/integration/sealed/fv-ex2-sealed-preview.php
```

## Still required (hard release gate)

An authorized **local Playground** installation with mounted sealed plugin and actual WordPress PHP runtime, followed by independent private-page and top-level-AJAX request/cookie/nonce test; Chromium/axe at 320/390/768/1440/1920 + 200% browser zoom, keyboard/touch/no-JS/reduced motion, full seven-chapter visual review; real media transfer/image rights, Lighthouse lab performance. The public WordPress.com Personal plan has no native staging clone; Playground ≠ WordPress.com Atomic, Jetpack, hosted cookies/redirects or field CWV. Actual Jetpack subscriber confirmation and the Focus false-success P0 (#1681), independent CI/QD and founder release approval remain unresolved. Do not install or deploy this plugin to production.

**Conversion contract:** The offer remains the existing 52-page Seven Day Focus Fieldbook. This engineering step prevents local staging review problems; it does not establish a lead, affiliate sale, paid order, or net revenue. Grok/Praxxis own distribution and asset IDs under Issue #820; Claude owns deployed attribution.
