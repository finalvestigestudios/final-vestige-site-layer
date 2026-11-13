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
