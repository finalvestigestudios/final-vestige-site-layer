# Apollo R47 — downloadable NASA reference register / staging HOLD

Part of Experience 2.0 Issue #150. Branch must descend directly from R46 PR #479, commit `1f1b63adb3cb59d82df41498c3a660920ed3aa33`. No homepage, Research Desk, WordPress, or production changes are authorized.

## Delivered

- Optional **Save all six source citations (.txt)** enhancement, derived entirely from the six existing visible NASA citations, with no network, analytics, image binary, license inference, geospatial pin, or relationship edge. A temporary year/search filter never alters the export. The output discloses the month-only uncertainty of S67-19766, historical-vs-photograph chronology, six unreviewed image-rights checks, NASA non-endorsement, and links to the Apollo 204 Review Board and NASA usage guidance.
- Native source index, all six source drawers, chronological links, citations, keyboard/touch interactions, and print remain available without JavaScript. Export is hidden by default and gracefully declines on altered provenance or unavailable browser Blob support.
- Fail-closed, read-only Research Desk ↔ Atlas catalog/photo-link parity validator (`tests/check_research_desk_parity_r47.py`), plus malformed-link/custody negative tests. This validates record identity, not historical claims or WordPress co-installation.

## Reproduce

From `experience2/evidence-atlas/`:

```bash
python -m unittest -q test_atlas.py
python -m unittest discover -s tests -p 'test_*.py' -q
php -l final-vestige-ex2-evidence-atlas.php
node --check atlas.js
python tests/browser_r46_pair_smoke.py
python tests/browser_r47_smoke.py
python tests/browser_r47_export.py --output /tmp/fv-apollo-r47-browser
python build_atlas.py --output /tmp/fv-apollo-r47-preview
python build_wordpress_stage.py --output /tmp/fv-apollo-r47-stage
python tests/check_research_desk_parity_r47.py --ledger /path/to/research-desk/templates/ledger.html
```

The more extensive browser export/capture runner is provided in the deterministic review archive. The actual source-controlled smoke runner covers Chromium widths 320, 360, 390, 768, 1024, 1440, 1920 in JS/no-JS and confirms byte-identical six-source downloads, filter isolation, citation visibility and tamper rejection. Browser testing executes real PHP shortcode markup via Playwright `set_content`, NOT an HTTP WordPress navigation.

The R38 Research Desk ledger Git blob `4842afb84b4c993cfc4861ce7f5a7a4d7b451871` and R37 photo crosswalk Git blob `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea` were independently read through the connected GitHub API on November 1, 2026; all six record IDs, catalog names, custody ids and NASA photo URLs match. This check did not establish parity of interpreted claims or photo rights.

## Not executed / release gates

Chromium HTTP navigation to a local server returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Actual WordPress/Assembler rendering, CSP, pinned axe-core, Safari, NVDA/VoiceOver, independent editorial QA, hosted Core Web Vitals (LCP/CLS/INP), six individualized image-rights reviews, hosted CI, and founder approval are **NOT PASSED**. No installer, deploy, merge, protected branch change, WordPress content/settings write, or paid service. All six original NASA image URLs were checked on November 1, 2026 and still resolve to NASA source pages, which does not grant photo-use rights.

**Release decision: HOLD.**
