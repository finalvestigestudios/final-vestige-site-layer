# Apollo R65 — complete NASA source-link hit-target audit (STAGING HOLD)

Original requirements: Issue #150, R38 Research Desk, PR #158, separate R64 draft (#610). All changes live in `experience2/evidence-atlas/`; frozen homepage PR #49 and lead branches remain untouched.

## Independently reproduced defect

At a 1440px viewport, **all six actual NASA photographic-archive links** (`.fva-card__external`) had just **39.1px** hitbox height. Previous testing checked the context/footer NASA links, but not these six main EvidencePlate archive links. This is below Final Vestige's 44px activation-area standard, even though the 24px WCAG 2.2 AA minimum could be met. We corrected the six original link areas with one cohost-scoped CSS rule; original URLs, historical dates, source metadata, license assertions, PR #158 files and Atlas runtime stay identical. Updated stylesheet asset version: `0.0.65-staging`.

## Reproducible acceptance

`python tests/browser_r65_all_targets.py --output <qa-dir>` runs **32 Chromium configurations**: eight widths 320–1920px, JS on/off and regular/forced colors. It computes actual bounding boxes for **every visible link, input, button and native summary** within the suite. Any interactive target below 44px high or 24px wide fails the run. It also tests original NASA HTTPS targets, new-tab `noopener`, keyboard focus visuals, 200% text reflow, six-record print restoration after filtering, all 30 Desk and 54 Atlas custody fields, no-JS, no unexpected requests, screenshot equality, and local fragment LCP/CLS observations. The runner invokes the **original R38 shortcode and source-built Atlas** through a PHP WordPress API simulator; it is **not** installed WordPress or an accessibility certification.

`python -m unittest discover -s tests -p 'test_*.py'`, `python -m unittest test_atlas.py`, PHP lint and Node syntax checks are separate gates. `python tests/build_r65_bundle.py --output <zip> --qa <qa-dir>` deterministically creates an 11-file private WordPress staging triplet plus exact source, test runner, QA receipt and captures; generate twice and compare SHA-256. Nothing is installed, activated, or written to WordPress.

## Release blockers

Private actual WordPress/Assembler install, verified axe-core and screen-reader testing, hosted CWV and independent QD, CI on exact PR SHA, six individual NASA image-rights assessments (0/6), and provisional record-01 catalog association. No photos are embedded, no speculative locations appear, and release remains HOLD.
