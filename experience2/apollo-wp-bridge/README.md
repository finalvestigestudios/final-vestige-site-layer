# Final Vestige Experience 2.0 — Apollo WordPress bridge (DRAFT, staging only)

This directory contains a **real, source-controlled WordPress shortcode adapter** for the existing Apollo 1 casefile, along with a deterministic build system, explicit source lineage guard, PHP-integrity fallback and a CLI WordPress mock + real Chromium component QA harness.

## What a staging installation would render

Shortcode **`[fv_ex2_apollo_casefile]`** renders the Apollo chronology, Research Desk, six-card claim custody ledger, side-by-side evidence comparison, six-part Board/response audit, six documentary source trails, source gallery and geolocation-free Evidence Atlas. It preserves the existing live post rather than overwriting it.

The generated WordPress fragment removes the nested `<main>` and changes the internal headline to an `<h2>`, avoiding extra main landmarks and a competing page H1. The builder prefixes all generated CSS selectors under `.fv-ex2-apollo`, preserving the enclosing WordPress theme's header/footer and base styles. All four CSV/JSON source exports use a real plugin asset-base substitution instead of relative links that would fail on nested WordPress page URLs. Script behavior remains optional; complete historical records and native disclosures survive without JS.

The shortcode serves a single instance per page, validates seven deterministic output file SHA-256 values, and falls back to the published original Apollo investigation if files are missing, corrupted or built from an unreviewed source version. The CLI mock can explicitly override a mismatched fixture for isolated research; **HTTP requests cannot**.

## Exact upstream contract

Base: [Apollo Documentary Trails PR #215](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/215) at commit `74375657f2cdaac0710f94c6de6c24534ee06858`. `upstream-pr215-blobs.json` pins all **12** read inputs to exact Git blob IDs from that commit.

**On the actual GitHub PR #215 source head**, `python experience2/apollo-wp-bridge/build.py` should regenerate the fragment, locally scoped CSS, JS, four exports and cryptographic output manifest without a fixture override. Installation and publishing are **not** part of this PR.

**In this run's local historical ZIP fixture**, four pre-existing response files differ from the streamlined code already on PR #215: `response_lab.py`, `response-crosswalk.json`, `assets/response.css`, `assets/response.js`. The builder correctly **rejects these by default**. For browser *component research only*, `FV_EX2_ALLOW_UNPINNED_FIXTURE=1` builds a manifest that explicitly records `source_matches_pr215=false`. A production HTTP shortcode refuses that manifest. No locally assembled fixture is described as an exact PR #215 integration test.

## Reproduce checks (no WordPress server required)

From a branch containing the full sibling `experience2/apollo-casefile`:
```bash
python -m pip install "tinycss2==1.5.1" "playwright"
python experience2/apollo-wp-bridge/build.py
php -l experience2/apollo-wp-bridge/fv-ex2-apollo-casefile.php
python experience2/apollo-wp-bridge/qa/verify_bridge.py
python experience2/apollo-wp-bridge/qa/browser_bridge.py
```

The package intentionally **does not commit generated assets from the earlier divergent local fixture**. Generate them from the pinned source before copying this plugin to a **separate WordPress staging system**. Install/activate there only after separate founder approval; no production CMS or WordPress settings writes have occurred.

## Local QA actually performed, 2026-10-30

- Real PHP CLI lint on adapter and shortcode stub; single-instance rendering, accurate export URL rewriting and intended fallback.
- Two deterministic local fixture builds; SHA-256 values identical.
- Deliberate source-pin rejection of the four divergent fixture inputs; deliberate tampering with one generated JS file causes PHP to output the fallback **even after** the test harness marks its temporary copied fixture lineage as reviewed.
- Actual Chromium/Playwright running the **PHP-generated HTML plus the exact locally generated CSS and JS** via `set_content`, at **320, 360, 390, 768, 1024, 1440 and 1920 px**. Verified visible chapter counts, six trails, source drawers, filtering, hash/focus behavior, no JS, reduced-motion configuration, 200%-equivalent zoom, zero horizontal overflow in tested states, no page errors, and unaffected mock WordPress header.
- Chrome CDP accessibility-tree smoke identified no unnamed button/combobox among those tested. This does NOT substitute for axe or screen-reader QA. Screenshots of the resulting 390px/1440px hero and documentary trails are available in the local staging evidence ZIP; no raster assets or NASA photograph bytes are committed.
- Local in-memory browser reported **no LCP events**; report fields are `null` rather than falsely describing LCP as 0. Observed CLS=0 in that fixture, not production field performance.
- **Actual HTTP navigation, CSP enforcement, WordPress Assembler integration, MIME/download routes, axe-core, Safari, NVDA/VoiceOver, live CWV LCP/CLS/INP, image license review, hosted CI and independent QD are STILL OPEN.** This sandbox's Chromium is administratively blocked from navigating even to localhost/file:// and the verified axe-core bundle was unavailable; do not interpret the absence of browser errors as a passing real WordPress integration.

## NASA source and editorial limits

Historical source URLs were checked on October 30, 2026: [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/), [NASA's response](https://www.nasa.gov/missions/apollo/apollo-1/nasa-response-to-findings/) and [NASA media-use policy](https://www.nasa.gov/nasa-brand-center/). The casefile renders source citations and clearly bounded documentary claims, not NASA photographs. Independent image credit/publicity/license evaluation remains a release gate. **No endorsement, NASA seals, paid service, user tracking, invented geospatial coordinates or speculative historical edges.**

## Release gate

This is an **isolated draft PR** stacked only on the Apollo PR #215 branch. It does **not** touch the frozen homepage PR #49, Research Desk PR #158, homepage lead lane or live WordPress. The shortcode must not be activated on the public site without a real staging integration review, exact-head CI/QA, manual assistive-technology testing, source rights sign-off and explicit founder approval.

Tracking: [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150).
