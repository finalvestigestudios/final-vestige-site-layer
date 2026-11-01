# R35 — Research Desk dynamic-shortcode asset lifecycle fix (DRAFT / HOLD)

Issue #150 · Stacked review on PR #158, **not a modification of PR #158 or homepage PR #49**. No WordPress deployment, theme settings, page edits, merge, or production publishing.

## Defect and exact change

PR #158 only enqueues its stylesheet and footer script when `has_shortcode($post->post_content, 'fv_ex2_research_desk')` detects a literal shortcode in the top-level singular post. A shortcode supplied by a synchronized/reusable block, dynamic block or template part can execute after `wp_head` while being absent from `post_content`; the original adapter then does **not** enqueue its CSS or JS. This is an acknowledged blocker in PR #158's README.

R35 removes the brittle `get_post()`/`has_shortcode()` early-enqueue gate. On all singular views, the plugin now enqueues **the exact same first-party stylesheet and footer JS** at `wp_enqueue_scripts` priority 20, before late block/shortcode rendering. The CSS remains `.fv-ex2-ledger`-scoped; the existing JS is inert when `[data-fvx-ledger]` is not rendered; the source template and the six NASA records are **unchanged**.

**Explicit performance trade-off:** singular views that never render a Research Desk now load these small local assets. This is acceptable only as a staging proof of correctness; production requires bundle-size, page-coverage and CWV measurements before choosing unconditional or more selective early loading. Non-singular archive views remain outside early loading; they fall open to readable static shortcode markup, not a styled/interactive guarantee. No claim of universal asset coverage is made.

## Reproducible tests

```bash
cd experience2/research-desk
python -m unittest discover -s tests -p 'test_r35_wp_lifecycle.py' -v
php -l final-vestige-ex2-research-desk.php
# Optional cross-lane Chromium regression of the separately pinned R34 static artifact:
python tests/browser_r35_existing_chronology_regression.py --html /path/to/apollo-chronology-r34.html --out /tmp/r35-browser
```

The PHP fixture uses mocked WordPress hooks and deliberately calls `wp_enqueue_scripts` **before** rendering an invisible-to-`has_shortcode()` reusable or dynamic block. It is NOT an installed WordPress environment. The baseline PR #158 adapter blob is `d1879a90101b5475990132369178f42743f4b57c` (verified locally by reconstructing original bytes). The original adapter fails the reusable-block early-asset case; the changed adapter passes. The original CSS, JS and six-record source template remain pinned by Git blob SHA tests (when checked out).

The optional Chromium suite tests the **unchanged R34 static source chronology**, not PR #158's actual WordPress/Assembler rendering. It does 320–1920px, JS enabled/disabled, mobile touch, keyboard, reduced motion and screenshot receipts; `page.set_content` bypasses HTTP navigation. Chromium LCP/CLS receipts are synthetic only, not hosted/field Core Web Vitals. Do not present them as WordPress integration testing.

## Release holds and editorial boundaries

- The source-linked, image-reuse-held six-record NASA evidence remains unchanged. `S67-19766` is **not** confirmed by the linked NASA page; do not convert it to an affirmative photo-catalog identity.
- The 1966/1967/2017 date-indexed photography rail is separate from the Apollo 204 incident instrument chronology. No invented coordinates, map pins or relationship edges.
- **BLOCKED:** authentic WordPress/Assembler and reusable/dynamic block integration; proven CSP headers over HTTP navigation; independently obtained and verified axe-core bundle; Safari/VoiceOver/NVDA; production-like CWV; NASA rights and original catalog identity; independent QD; green exact-head CI; founder visual/release approval.
- The tests do not modify WordPress posts/pages/settings or call external services; no licensed imagery is embedded.

**Release decision: HOLD.** Do not merge, install or deploy without the governed evidence gates and approval.
