# R338 — Research Desk isolated multiple-shortcode correctness

This branch is stacked ONLY on R337 PR #2358 (itself based on Research Desk owner PR #158), NOT homepage PR #49. The substantive adapter patch namespaces the immutable template ID prefix independently on every shortcode render. This fixes cross-instance duplicate heading/search/grid/record IDs and labels/ARIA pointing at the wrong instance. User shortcode arguments and query params never form identifiers.

## Executable acceptance

- `php -l experience2/research-desk/final-vestige-ex2-research-desk.php`
- `php experience2/apollo-r338/qa/research_desk_instances.php`: actual six-record bundled template, 2 shortcode renders, 12 distinct source/rights pairs, valid label/ARIA references, one existing free investigation CTA per render, no invented geo or merchant destination.
- `php experience2/apollo-r338/qa/research_desk_instances.php --emit-fixture > /tmp/r338.html`: browser fixture uses real updated PHP, actual R337 template and bundled CSS/JS without WP installation, external network or fabricated NASA image bytes.
- Run Playwright browser acceptance against /tmp/r338.html at 320–1920, JS on/off, 400% zoom, forced colors, reduced motion and keyboard search/disclosures. Produce real screenshots/receipts, never present offline fixture CWV as production metrics.

## Remaining release hold

Browser acceptance of modified Research Desk, native WordPress/Assembler/CDN and nested shortcode asset enqueue, genuine axe-core, Firefox/WebKit, independent screen readers, HTTP CSP, media reuse rights/editorial review, hosted exact-head CI, verified Grok asset, payable/rights-cleared commercial SKU and founder/QD release approval. No WordPress writes, external images, paid services, affiliate tracking, deployment or changes to Grok's TASK-008 queue. Source-custody primary/photographic distinction from R337 is preserved.

**Conversion hypothesis:** credible NASA provenance plus accessible navigation helps qualified Grok long-form visitors progress to the one existing free investigation and, only after a real SKU/checkout is approved, a relevant educator evidence kit. The commercial KPI is settled net revenue per 1,000 qualified-human sessions; without merchant reports and qualified-session attribution this remains NOT COMPUTABLE. Cross-reference #150, #820, #818.


## R338 executed acceptance (2026-11-13, independent local receipt)
- Real PHP CLI renders the exact committed six-record R337 template TWICE: **PASS**; 12 historical cards, 12 documentary-first source links, 12 contextual-photo-only links with reuse-review required; 18 unique DOM IDs and working for/aria-controls/aria-labelledby references across instances.
- Changed adapter Git blob `fa7e8b0d9535bd2e87d46d484d9ff481b2e1e148`; scoped source-ledger CSS Git blob `0ae12d1bb9e0e10cb8ce6286e205b500f7b8f304`; original template R337 blob `d773d0de24d9eb0eaf073e007b135034c214fb51`.
- New actual-browser failure reproduced on original CSS: NASA link hitboxes approximately **20.8px tall** at 390px / 1440px. CSS now provides **at least 44px height** on primary NASA record links AND the single existing editorial continuation link. **PASS** all 15 extended Chromium offline PHP-rendered contexts (320/360/390/768/1024/1440/1920; JS on/off; 320 root font 32/64px; forced colors; reduced motion; touch emulation); every tested outbound target at least 44px tall and wholly within viewport. Search filters only its own shortcode, clear restores six results, keyboard Enter expands native details, and no-JS preserves full evidence.
- Expanded actual-browser guard rejected **6/6** intentionally bad DOM mutations (duplicate ID, merchant masquerading as source, media-rights laundering, fake geo edge, missing evidence, duplicate editorial CTA).
- Separately, **12/12 contexts PASS** on exact GitHub-committed Playwright script `experience2/apollo-r338/qa/research_desk_browser.py` after fresh Git blob readback. The longer 15-case local script + JSON receipt + screenshots are archived separately.
- Offline Chromium `PerformanceObserver` LCP observations at widths 320, 390, 768, 1440, 1920: **180, 100, 124, 84, 92 ms**, with initial observed CLS 0 in these five offline instances. These are not installed WordPress or field Core Web Vitals; no INP claim.
- Native Playwright Firefox and WebKit could not launch because their browser binaries are absent; **0 non-Chromium acceptance cases**, not failures of the rendered experience. Genuine axe-core and manual screen-reader verification were not executed.

These improvements do **not** fix nested/reusable-block shortcode asset enqueue on installed WP. That remains a separate integration blocker. No automated order, affiliate, newsletter, live campaign or merchant claims. All source and conversion work is staged-only and subject to founder/QD release hold.
