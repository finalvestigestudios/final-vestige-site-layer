# Apollo R46 — Source Pair Inspector / STAGING HOLD

Research Desk / Evidence Atlas component sprint for Experience 2.0 Issue #150. Child of Apollo R45 (PR #472), not homepage PR #49 or Research Desk PR #158. Independent review required; do not install, activate, merge or publish.

## Function

A progressive-enhancement-only, text-only pair inspector. Six source cards each receive a hidden-by-default, 44px-minimum selection button. With validated JavaScript, a reader can select up to two NASA records and view their *already displayed* catalog labels, photographic dates, documented role and image-rights status side by side. Selecting a third source rotates the oldest selection; deselect and Clear are supported. Native deep links back to complete source custody reveal a record if a user previously filtered it out. There is no inference of geographic proximity, chronology of the fire, linkage, causality, or media permission.

The inspector remains hidden without JavaScript; six source cards, six SourceDrawers, ChronologyRail, the Citation Register and native NASA links remain available. Pair metadata is assigned through `textContent` and element creation, never HTML insertion. When a required element or record is tampered with, enhancement is suppressed/restored fail-open. Printing excludes the derived pair UI and includes all six original records and citations.

## Evidence and reproducibility

Run from `experience2/evidence-atlas/`:

```
python -m unittest -q test_atlas.py
python -m unittest discover -s tests -p 'test_*.py' -q
php -l final-vestige-ex2-evidence-atlas.php
node --check atlas.js
python tests/browser_r46_pair_smoke.py
python tests/browser_r46_compare.py --output /tmp/fv-apollo-r46-qa
python build_atlas.py --output /tmp/fv-apollo-r46-preview
python build_wordpress_stage.py --output /tmp/fv-apollo-r46-wp-stage
```

The extended browser runner `browser_r46_compare.py` is supplied in the QA package pending source-controlled promotion; the shorter 14-configuration Playwright smoke test is source-controlled. Browser tests used **actual PHP-rendered shortcode markup via `set_content`** with Chromium (320/360/390/768/1024/1440/1920; both JS-on and no-JS); they are not navigated WordPress. The captured LCP/CLS observers are *synthetic fixture observations*, not hosted Core Web Vitals evidence. Host blocks even loopback HTTP navigation with `ERR_BLOCKED_BY_ADMINISTRATOR`; no `axe-core` binary can currently be fetched/loaded, so do not claim an axe audit.

Pinned R37 custody Git blob: `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea`. Compiled shortcode fragment SHA-256: `4ee830625151587b0d446ee27602618125c2198118d3f11f8b2d95938830f890`. Adapter version: `0.0.46-staging`. Six photographs remain external NASA links, with all six individual media-rights reviews open. All six official NASA reference pages and NASA's media-usage restrictions were re-opened on 2026-11-01; link presence is verified, not a rights clearance.

## Release blockers

Authentic isolated WordPress/Assembler staging, HTTP/CSP and true hosted LCP/CLS/INP, verified axe-core, Safari/NVDA/VoiceOver/manual accessibility, individual media-rights review, editorial and independent QD, founder direction, and exact-commit CI remain outstanding. Do not change homepage PR #49, homepage lead branches or production WordPress. No geographic pins/edges, imagery, paid services, deployment or site settings/content writes were made.
