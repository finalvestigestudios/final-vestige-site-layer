# Apollo R174 — Research Desk dynamic-shortcode asset lifecycle (STAGING HOLD)

**Source of truth:** [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [original Research Desk PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158), [conversion coordination #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Independent from frozen homepage PR #49, Claude's engineering, creator TASK-008 and merchant systems.

## Defect and trade-off

Original PR #158 checks `is_singular()`, the top-level `get_post()->post_content`, and `has_shortcode()` at `wp_enqueue_scripts` (WordPress head phase). A Research Desk shortcode supplied by a reusable Gutenberg block, a template part, a dynamic block, widget or archive may render later with **no CSS or JS**. A render-time enqueue is too late to guarantee stylesheet output in the document head.

**Candidate fix:** enqueue the existing, scoped Research Desk CSS and JS at `wp_enqueue_scripts` on all front-end requests *while this standalone staging plugin is active*. This is intentionally an availability-over-byte-count trade-off. Existing CSS is scoped under `.fv-ex2-ledger`; JS returns immediately if there is no `[data-fvx-ledger]` root. No tracking, cookies, remote scripts, forms or new links. WordPress deduplicates the two stable handles. Do not use this candidate until actual page/asset network sizes, caching, compatibility and mobile CWV are measured. A future approved production solution can use a validated preload manifest instead of sitewide delivery.

## Source custody

The overlay PHP was derived mechanically from the **exact original** `experience2/research-desk/final-vestige-ex2-research-desk.php` on PR #158. Baseline Git blob: `d1879a90101b5475990132369178f42743f4b57c`. **Only** `fv_ex2_rd_assets()` was replaced. The original shortcode HTML, `add_shortcode` registration, template fallback, investigation URL and all other source remain byte-identical. R174 candidate Git blob: `0509c3706dfb26295c681d5569c8750b05b7b8db`. This file is an **overlay**; before staging, place it at the plugin root alongside PR #158's existing `assets/source-ledger.css`, `assets/source-ledger.js`, `templates/ledger.html` (not included or modified in this PR). Do not install the overlay directory by itself.

## Reproducible checks

```bash
php -l experience2/apollo-r174/staging-overlay/final-vestige-ex2-research-desk.php
php experience2/apollo-r174/tests/asset_lifecycle_mock.php
```

Independent local Python source-pinning: 4/4 unit tests PASS; altered baseline/CTA rejected. Independent real PHP CLI: five context cases PASS, link fallback PASS, `php -l` PASS. Real Chromium (R173 representative six-record fixture **only**): 12 contexts, 138 assertions, six widths 320–1920, JS/no-JS, keyboard details, touch emulation, reduced motion, source labels and unchanged original-investigation CTA; fixture LCP 64–116 ms, CLS 0. These **do not** establish actual installed WordPress functionality or CWV. The QA archive includes receipts and screenshots. Genuine axe-core was unavailable and was **NOT EXECUTED**.

## Required next release gate

1. Stage original PR #158 plugin assets and R173 source-role overlay with this isolated replacement, with independent release approval. Do not merge in place or alter WP settings/content.
2. Test top-level, reusable, nested, template-part, widget, archive and empty routes in **installed** WordPress; confirm CSS/JS response statuses and cache handling, genuine axe-core and manual AT, screen readers and performance.
3. Review real-world sitewide load cost and reduce scope only with equivalent proven dynamic-content coverage; apply source custody/security gate and QA signoff.
4. Confirm Apollo-specific approved SKU/rights, checkout, merchant-paid orders and consent-based attribution before activating a commercial link. Until then the sole contextual CTA is **Read original investigation**.

**No production write; no historical photo re-use or new pins; no changes to #49, #158, live WordPress, Grok or Praxxis.**
