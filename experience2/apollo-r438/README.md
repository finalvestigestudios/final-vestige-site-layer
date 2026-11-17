# Apollo R438 — Provenance Atlas (source-controlled staging candidate only)

This isolated source-link-only mini Atlas attaches to the exact R437 rendered Research Desk chain without modifying homepage PR #49, Research Desk PR #158, WordPress production, analytics, creator pipeline, merchants or releases. **Staging only; disabled unless explicit `FV_R438_ENABLED=true` and integer `FV_R438_STAGING_PAGE_ID` match a singular page in `wp_get_environment_type()==='staging'`.** Shortcode `[fv_apollo_source_atlas_r438]` is a candidate, not installed or deployed. Source routes remain free.

## Value

Five NASA-linked source records each have (a) documentary type and date class; (b) what the record supports; (c) what it cannot establish; (d) independent media/commercial-rights status; and (e) original NASA URL. Primary Board report, prefire training photo, postfire damage photo, 2017 retrospective exhibit and 2018 flammability account are not interchangeable. **No geolocation coordinates, link graphs, NASA media files or insignia**. Optional *side-by-side evidentiary limits* uses progressive enhancement; all original sources, limits and rights stay readable without JS, on print and at 320–1920px. Comparison buttons never make a new assertion of causation. One original investigation CTA from the verified parent is retained, no paid offer, form, cookies, tracking or duplicate scripts.

## Source and release integrity

Catalog is static SHA-256 pinned JSON with a restricted NASA URL whitelist, five exact records and no coordinate fields. Local CSS/JS also SHA-256 pinned, and the full R437 PHP + CSS + JS by Git blob before enqueue or rendering. Parent code recursively verifies prior R436→R429 chain. Altered or symlinked files fail open to one original free Apollo article. WordPress adapter queues assets only on explicitly enabled, exact staging page. No assumptions of NASA endorsement, commercial-photo rights or identifiable-person releases. Source links are not asset licenses. The source catalogue must undergo independent human evidence/rights review before any paid deliverable or public deployment.

## Reproduce executed QA (in the same `experience2/` checkout as R429–R437 pinned ancestors)

```sh
php -l experience2/apollo-r438/staging-source-atlas.php
python3 experience2/apollo-r438/qa/test_contract.py
python3 experience2/apollo-r438/qa/browser_qa.py
python3 experience2/apollo-r438/qa/staging_acceptance.py  # HOLD exit 2 unless approved HTTPS, SHA-reviewed authentic axe
python3 experience2/apollo-r438/qa/package_evidence.py
```

Browser execution is actual Chromium with PHP-generated HTML via `set_content`, **NOT navigated WordPress staging**; browser navigation is explicitly blocked in the current environment even for localhost, so any LCP/CLS, WCAG 2.2 AA and field p75 claims remain **UNVERIFIED**. On approved staging, the separate gate requires real navigation, genuine SHA-reviewed axe-core, 7 widths, lab LCP ≤2500ms and CLS ≤0.1; independent QD, screen reader, real user CWV and founder approval are still mandatory. The ZIP packager excludes itself, preserves file-content digests and uses deterministic metadata.

NASA Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; NASA gallery: https://www.nasa.gov/gallery/apollo-1/ ; NASA tribute: https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/ ; flammability: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ ; rights https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ .
