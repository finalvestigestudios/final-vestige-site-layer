# Apollo R347 — source custody index / accessible evidence navigation (DRAFT)

**Independent Experience 2.0 lane.** Coordinates with [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and charter #818. Stacked on unmerged R346 [PR #2404](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2404) at `d0f66b45eaad04e801aa8523ba756bf4239ad646`. Do not merge, deploy, edit homepage PR #49, Research Desk PR #158 or any production WordPress content/settings.

## Purpose and implementation

The chronology, original Board EvidencePlates and contextual photo gallery previously required readers to separately open several source drawers. The new **source index** presents **13 referenced evidence entries** from the same already-reviewed PHP arrays (3 original Board findings, 5 original Board chronology markers, 1 later NASA history and 4 contextual photographs). They reference **eight distinct NASA pages**, not 13 independent NASA documents. Boundaries and source classifications remain visible in every entry. No new claim, map pin, media reuse, external script service or commercial CTA is introduced.

Staging shortcodes: `[fv_apollo_source_index_r347]` for the index alone; `[fv_apollo_experience_r347]` for the chronology, three Board plates, four-photo link gallery and index with exactly **one** existing free-investigation continuation. The optional five-button filter is progressively enhanced; without JS all entries remain visible. Screen readers receive native button state and a live result count. All source links remain available in native browser PDF export even if the visitor selected a filter. Unique IDs support multiple instances. A WordPress pre-head resolver schedules all four scoped styles and one optional local script for direct and bounded reusable-block placements. Missing parent components render a free editorial fallback.

**Verified original source:** [1967 NASA Apollo 204 Review Board findings](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html), specifically 1, 2 and 4. Original investigation and chronology: [investigation](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html), [chronology](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/chro.html). Later NASA historical source: [Apollo 1 fire and aftermath](https://www.nasa.gov/history/55-years-ago-the-apollo-1-fire-and-its-aftermath/). Gallery accession IDs S67-15717, S66-58038, S67-21294 and KSC-20170124-PH_KLS01_0090 were checked against NASA accession pages on November 13, 2026; they are source links, **not media rights clearance or ignition evidence**.

## Executed local QA (NOT WordPress staging)

Run with PHP 7.4+, Python, system Chromium, Playwright and PyMuPDF:

```sh
php -l experience2/apollo-r347/source-index.php
php experience2/apollo-r347/qa/preflight.php
python experience2/apollo-r347/qa/acceptance.py
```

Preflight: direct shortcode, index-only styling, composite CSS dependencies, script, recursive reusable-block cycle, missing block, oversized content, exactly one CTA and no commerce/geo/media violations PASS. Chromium: eight contexts across 320, 390, 768, 1440 and 1920px, including 320px/400% root text, JavaScript-disabled, keyboard Enter filter, touch, forced colors and reduced-motion PASS. Two independent copies on one page have unique IDs and isolated filter state. Filtered native PDFs preserve all four categories and NASA links; overflow checks pass. 13 evidence entries and 8 unique NASA URLs verified. Browser screenshots, native PDF, JSON receipt and a SHA-256 archive are packaged outside GitHub. A 320px/400% text overflow was **found and fixed in the new index headings/filter buttons**, then rerun PASS.

A separately executable `qa/performance.py` uses genuine Chromium `PerformanceObserver` for LCP and layout shifts over five local viewports (320/390/768/1440/1920px) with a 700ms observation window. In the executed local pass LCP ranged **76–220ms**, with **zero observed CLS**. These are **synthetic local fixture observations**, not field data or installed-WordPress/production Core Web Vitals.

This is a PHP-rendered `page.set_content` browser fixture, not actual installed WordPress, HTTP/CSP, CDN, authenticated browser session, WCAG certification or production performance. Genuine axe-core, screen readers, Firefox/WebKit, production LCP/CLS, exact-HEAD CI and installer acceptance are NOT VERIFIED. Never call local fixture timing production Core Web Vitals.

## Conversion-first decision

**Audience:** Grok's Apollo long-form viewers who are history teachers, evidence-curious readers, or students investigating the design/safety lesson. **Trust bridge:** Grok Apollo long-form → source index/Atlas → existing free Apollo 1 investigation → **only after independently verified rights-clearance and payable checkout** an Apollo educator dossier offer. A free investigation is not a paid sale.

**Hypothesis:** better immediately inspectable provenance reduces qualified-reader trust friction and improves progression to relevant educational material; requires genuine qualified-human attribution and paid-order reconciliation to validate. No published Grok asset_id, payable Apollo SKU, confirmed orders, fees, refunds or campaign attribution were authenticated. One existing editorial CTA only. Privacy-respecting attribution belongs to Claude's #820 lane, without duplicate scripts. Grok owns content/production and Praxxis owns independent creator review; do not modify TASK-008.

**HARD HOLD:** QD, founder, rights/editorial approval, installed WordPress/Assembler, non-Chromium browsers, real axe-core/screen readers, native HTTP/CSP, hosted CI, validated checkout, Grok post/destination and paid measurement remain outstanding. This isolated PR is research/staging code only, not permission to release.
