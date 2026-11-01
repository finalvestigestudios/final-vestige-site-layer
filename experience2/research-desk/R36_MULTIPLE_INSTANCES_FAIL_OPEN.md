# Apollo R36: repeated-shortcode identity and late-search failure recovery — STAGING / HOLD

Scope: [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), stacked on R35 draft PR #405, itself stacked on Research Desk draft PR #158. **No change to PR #49 or homepage code, WordPress content/settings, production, or any live plugin.**

## Defects and correction
1. When a reusable/synced block or template part renders `[fv_ex2_research_desk]` multiple times, the immutable bundled `templates/ledger.html` hard-codes repeated `id`, `label for`, `aria-labelledby`, and `aria-controls` values. Before R36 these collide across instances, making label/target resolution ambiguous. The PHP adapter now keeps the first instance identical to the existing template, then namespaces subsequent instances on the server as `fv-ex2-ledger-apollo1-2-...`, `...-3-...`. No client-side scripting or new WordPress hooks are needed.
2. If a record's `data-fvx-search` attribute disappears *after* JS search initializes, the original input handler throws and may leave a subset of evidence hidden. R36 catches filter-time failures, reveals all cards, hides the broken search enhancement, removes that instance's listener, and preserves the other Research Desk instances. No network, storage, HTML injection or hidden photo elements are introduced.

## How to reproduce on a full checkout
Run `python -m unittest discover -s experience2/research-desk/tests -p 'test_r36_shortcode.py' -v`.
Run `python experience2/research-desk/tests/browser_r36.py`; requires PHP, Node, Python Playwright and Chromium at `/usr/bin/chromium` (adjust executable locally if necessary).
The test driver calls the **actual Research Desk shortcode PHP**, reads the **actual unchanged NASA template + CSS + new JS**, emits a three-instance private test HTML, then exercises 7 widths (320/360/390/768/1024/1440/1920) × JS enabled/disabled. It checks all 18 evidence records, all ID/ref relationships, NASA links, isolation of search results between instances, empty-search recovery, keyboard disclosure toggling, touch disclosure, reduced motion, overflow, and fail-open after a late record-index mutation. Real Chromium screenshots are generated at 390px and 1440px with JS on/off.

The browser script first attempts a local `file://` navigation to measure local synthetic LCP/CLS using observers. **If navigation is blocked by the environment, it transparently falls back to `page.set_content()` and records both performance metrics as null.** Do not substitute them for measured hosted CWV.

## Known limitations / release gate
- This is PHP WordPress-function test-double evidence, **not installed WordPress + Assembler**. WP nested/rendered blocks, shortcode on archive views, and enqueue impacts remain to be audited in real staging.
- R35's early singular-view asset loading remains intact, including its per-page performance trade-off; this PR does not optimize it.
- Real LCP/CLS on deployed host, axe-core, Safari/VoiceOver/NVDA, CI at exact head, and independent QD all remain incomplete.
- NASA photo rights are **not cleared**. The six record cards link externally; source records and limitations remain immutable. The `S67-19766` identifier is still under editorial review. A photo-source ID is not automatically proof of historical claim or permission to reuse an image.
- No speculative Atlas geographic pins or relationship edges. No NASA images embedded, no WordPress writes, merges, activation, or deployment.
- WordPress/theme-dependent heading outline for multiple `h1` records merits independent review; ID uniqueness alone is not WCAG conformance.

**Release decision: HOLD** until actual WP staging, source/editorial/rights review, axe-core and manual accessibility, hosted performance, CI, and founder approval.
