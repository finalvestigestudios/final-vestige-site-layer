# Apollo Experience 2.0 — R364 nested-custody asset bridge

**STAGING-ONLY / DRAFT / UNMERGED / NOT LIVE.** Adds a companion, read-only `wp_enqueue_scripts` pre-head resolver for the existing R363 shortcode `[fv_apollo_custody_guard_r363]`, without editing R363, Research Desk PR #158, homepage PR #49, WordPress or Grok's queue.

## Why

R363's original stylesheet enqueue inspects only the singular post's literal content. A custody guard rendered inside a reusable block, same-theme `core/template-part`, explicitly assigned block template or previously captured default template can lose its CSS. R364 recuses into those *verified* sources before the page head, reusing WordPress's existing `fv-apollo-r362-crosswalk` style handle (one enqueue). No script, remote request, content mutation or guessed template hierarchy.

Traversal is bounded to 500,000 cumulative bytes, 128 nodes, 48 references and six levels. Invalid or stale identities, foreign themes, cycles, missing post data and incomplete scans withhold asset authorization. This is an **asset-discovery** fail-closed rule; the underlying R363 historical record remains static-first, text-readable and no-JS.

## Reproduce from repository root

```sh
php -l experience2/apollo-r364/custody-asset-bridge.php
php experience2/apollo-r364/qa/wp_contract.php
python experience2/apollo-r364/qa/browser_gate.py
python experience2/apollo-r364/qa/build_evidence.py
```

The PHP QA uses **WordPress API stubs**, not installed WordPress. Browser QA uses actual Playwright Chromium on real PHP-rendered R363 output and asserts Git blob `600c2eb6a435f818262a26c39dad9142bb48ec94` for R362 CSS. Tests include 320–1920px, touch, keyboard, 400%-root text, reduced motion, forced colors, no-JS, named links, synthetic LCP/CLS and native Chromium print source destinations. Frozen ZIP build is deterministic, but regenerated browser PDF/PNG metadata/timings need not be byte-identical.

## Evidence and rights boundary

The 1967 Board's probable electrical-arc initiation is not a conclusive identification of a particular ignition source: https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html . NASA's February 14, 2018 retrospective documents 102 deliberate CM Boilerplate 1224 ignitions during December 1967–February 1968: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ . The latter are post-fire engineering tests, not 1967 Board observations. NASA links do **not** grant commercial photo, logo, likeness or endorsement rights. No images, geospatial pins, scripts, sale claims or affiliate links are introduced.

## Conversion-first / governance

One candidate path: verified Grok Apollo documentary (asset ID/UTM only when actually published) → free source-backed Atlas/Research Desk → exactly one free Apollo investigation CTA → *future* founder-approved, payable, rights-cleared educator offer. **No payable Apollo SKU or merchant acceptance is verified**, so there is no product CTA or revenue claim. Grok owns production; Praxxis external creator QA; Claude commerce/analytics; founder/QD release approval. Cross-reference [Apollo #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) and [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).

**HARD HOLD:** real installed WordPress/Assembler including default template lifecycle, axe-core/NVDA/VoiceOver, Firefox/WebKit, HTTP-response CSP, hosted exact-HEAD CI, media reuse, authenticated paid product, founder/QD approval. No merge, deployment, WordPress write, tracking, social publication or spending.
