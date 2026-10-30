# Research Sources category-count QA (offline only)

This folder provides a **read-only** guard for the saved WordPress/Gutenberg HTML of the published **Research Sources** page (WordPress page **1338**, `/research-sources/`). It makes **no HTTP requests** and does not update WordPress. The input is an explicitly exported `content.raw` snapshot kept outside the repository.

```sh
node --test qa/catalog/research_sources_count_guard.test.cjs
node qa/catalog/research_sources_count_guard.cjs /path/to/research-sources-content-raw.txt
```

The guard counts `<article class="fv-rs-card" data-cat="...">` entries and compares those counts against the category totals in the saved page's last `const totals={...}` script. Exit codes: 0 = counts match, 1 = source mismatch, 2 = insufficient data or invalid input. **This is a CMS-source audit, not a rendered-browser test.** Never store private credentials, subscriber data, or full page exports in this repository.

## WordPress read-only observation — October 30, 2026

* 90 source cards exist; counts by `data-cat`: declassified **12**, accountability **24**, engineering **21**, archives **25**, navigation **8**.
* The later inline count script declares: all **90**, declassified **12**, accountability **23**, engineering **21**, archives **26**, navigation **8**.
* The saved static lead/search/filter labels still refer to **60** sources and are changed to 90 by client-side JavaScript. The script also relocates cards from a batch container. Do not infer actual rendered desktop/mobile behavior without browser testing.
* Category labels are therefore source-inconsistent even though overall total 90 is correct. Do **not** automatically reclassify a card; ask the editor to verify intended taxonomy and then align the category counters and static fallback labels through the normal approval workflow.

This check deliberately does not edit the WordPress page, site navigation, newsletter, plugin settings, PDFs, or any public content. No CI, live accessibility certification, browser verification, or deployment is claimed. Claude's active editorial design lane remains the owner of any CMS changes.
