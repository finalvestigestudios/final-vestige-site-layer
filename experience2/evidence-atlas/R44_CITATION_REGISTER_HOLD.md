# Apollo 1 Evidence Atlas — R44 Citation Register — STAGING / HOLD

Parent: draft PR #461, exact commit `d6641759bde2fbf5b069844cf000cb00c0c2929f`. This candidate changes only `experience2/evidence-atlas/`; do not merge to production or touch homepage PR #49, homepage lead branches, or Research Desk PR #158.

## New implementation

- `build_atlas.py` generates a **six-entry, text-only NASA citation register** directly from the immutable R37 photo-custody ledger, preserving catalog IDs, photograph date precision, original NASA URLs and individual image-rights warnings. It never embeds photos or declares reuse rights cleared. `S67-19766` remains January 1967, **day unasserted**. Citation register remains readable without JavaScript and remains intact when the six cards are filtered.
- `atlas.js` exposes six copy controls **only if Clipboard API exists**; keyboard Enter/touch activates the same behavior. Permission denial announces a text-selection fallback through a live status and keeps all citations readable. Altered custody IDs disable optional controls and filters without hiding source records or citations. No tracking, storage, remote API, media loading, coordinates or speculative relationships.
- `atlas.css` supports the citation register across 320–1920px, visible keyboard outlines, 44px copy targets, reduced motion inherited, and print styles preserving all six citations and source records after filters.
- Updated WordPress fragment SHA-256 pinned in PHP: `169ffdbed3dd8f625a1b133deb8725f891d120e7320d8c4589398c8bbb511db6`; plugin `0.0.44-staging`. Both standalone and WordPress manifest schemas now R44.

## Reproduce (complete checkout, offline)

```bash
cd experience2/evidence-atlas
python -m unittest test_atlas.py tests/test_wordpress_stage.py tests/test_chronology_r43.py tests/test_citations_r44.py -q
php -l final-vestige-ex2-evidence-atlas.php
node --check atlas.js
python tests/browser_regression_r43.py --output /tmp/fva-r43-baseline
python tests/browser_r44_review.py --output /tmp/fva-r44-browser
python build_wordpress_stage.py --output /tmp/fva-r44-wp
python build_atlas.py --output /tmp/fva-r44-preview
```

## Verification scope and exact limits

- Local R44 source/adapter: **39/39 Python tests** pass. PHP lint and Node syntax pass. Inherited R43 and R44 Chromium runs each **14/14 responsive configurations** at 320, 360, 390, 768, 1024, 1440, 1920 with JS on/off; R44 adds clipboard permission-denied/unsupported, keyboard, touch, corrupt-ID fail-open, print and no-network checks. Four reproducible R44 screenshots retained in the QA package.
- Browser content comes from **actual PHP-rendered, pinned six-record template**, but uses `page.set_content`: all Chromium navigations to localhost, file and data URLs fail `ERR_BLOCKED_BY_ADMINISTRATOR` in this environment. LCP/CLS observers (where present) report **synthetic fixture values, not field Core Web Vitals**; INP cannot be certified. Axe-core is not installed or included and **was not executed**. These results are not authentic WordPress/Assembler, CSP, screen-reader or hosted performance certification.
- Six individual NASA photo-rights reviews remain unresolved. General NASA media guidance: https://www.nasa.gov/nasa-brand-center/ . No rights assertion based on that generic guidance; zero NASA image binaries distributed.
- Release remains **HOLD** until real WordPress staging/Assembler, approved pinned axe-core run, Safari/NVDA/VoiceOver, hosted LCP/CLS/INP, CI on exact commit, independent editorial/rights QA and founder approval. Never install, activate, merge, publish or write production WordPress from this PR.
