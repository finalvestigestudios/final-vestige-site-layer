# Apollo R41 — Evidence Atlas failure recovery and print source custody

**2026-11-01 — STAGING HARD HOLD.** Draft work under Issue #150, stacked only on R40 PR #442 (exact base `8fb0779cf8309e810eb569b57c56279ad08b4d02`). This branch does **not** edit homepage PR #49, homepage development branches, Research Desk PR #158, WordPress content/settings, or production. No merge, plugin install, or paid service.

## Two demonstrated defects fixed

1. **Enhancement rollback:** R40 `apply()` can detect changed source metadata and call `restore()` *after* listeners were bound. The initializer then unconditionally made the controls visible, despite the handlers having been removed. R41 returns a success/failure boolean from `apply()` and reveals controls only when initialization remains active. In Chromium, deliberately mutate the first record's `dataset.fvaYear` between initial `valid()` and first `apply()`: R40 has dead controls visible; R41 hides them, keeps all six records visible and six NASA links intact. No JavaScript/no successful initialization is ever required for reading.
2. **Print fidelity:** R40 printed only records remaining after a visitor's interactive year filter, and hid closed source-custody drawers. R41 print CSS restores all six records, shows each source's custody metadata, displays its original NASA URL as text, suppresses interactive controls and decorative plates, and reduces excess print whitespace. Actual Chromium regression: filtered to 1967 (three visible), print mode now exposes six (previously three); closed `<details>` metadata is readable (previously not). A rendered four-page Letter paper proof was inspected. The generated PDF is QA evidence, not a reviewed publication asset.

## Source integrity

Only the following paths are changed/added, all under `experience2/evidence-atlas/`:

- `atlas.js` — Git blob `287d3db8cd5b1306a3ea5062ee0e3f8a5e085ea0`
- `atlas.css` — Git blob `fb393fccf1d13a5ac4c50c8a41cfa0ee3ee18cf5`
- `final-vestige-ex2-evidence-atlas.php` — Git blob `ceed1809c6eccfbc2d67d10824983631ba8ec2d8`, version to 0.0.41-staging; unchanged pinned source-fragment SHA-256
- `build_wordpress_stage.py` — Git blob `0d02b64db72b64154010480c592b7c9b2d7affd6`, stage manifest schema to r41
- `tests/browser_regression_r41.py` — Git blob `3a4ac889ccd1085598e79ec797757b5ddeb0c9ff`; optionally generates four Chromium screenshots and JSON receipt.
- `tests/build_r41_review.py` — Git blob `dc06d3457df7e317cc5da0501acec5fce3499c0c`; deterministic offline QA ZIP builder.
- `R41_FAILURE_RECOVERY_PRINT_CUSTODY_HOLD.md` — this source-controlled report.

The original R37 source-custody crosswalk blob `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea` and six external NASA catalog links remain unchanged. Six image-rights decisions remain `INDIVIDUAL_REVIEW_REQUIRED`. No image binaries, speculative coordinates, map pins, map edges or claims about a reconstructed fire timeline are introduced.

## Reproduce source and browser tests

From a checkout with R40 ancestry, Python, PHP, Node, Playwright Python and Chromium installed:

```sh
python -m unittest discover -s experience2/evidence-atlas -p test_atlas.py -q
python -m unittest discover -s experience2/evidence-atlas/tests -p test_wordpress_stage.py -q
php -l experience2/evidence-atlas/final-vestige-ex2-evidence-atlas.php
node --check experience2/evidence-atlas/atlas.js
python experience2/evidence-atlas/tests/browser_regression_r41.py --output /tmp/fv-apollo-r41-qa
python experience2/evidence-atlas/tests/build_r41_review.py --qa /tmp/fv-apollo-r41-qa --out /tmp/fv-apollo-r41-review.zip
python experience2/evidence-atlas/build_wordpress_stage.py --output /tmp/fv-apollo-r41-stage
```

**Executed locally:** R39 source-custody Python 11/11 PASS; R40 WordPress adapter tests 12/12 PASS; PHP lint PASS; Node syntax PASS; **14/14** actual compiled R37/R39 custody / PHP-shortcode Chromium configurations PASS at widths 320, 360, 390, 768, 1024, 1440, 1920 with JavaScript on/off, keyboard disclosure, touch targets, filter and no-JS. Additional adversarial failure-in-initialization and print-custody tests PASS. All four screenshots at 390/1440 JS/no-JS reproduced byte-identically in two independent runs; the staging manifest reproduced byte-identically. The 19-file ZIP built twice byte-identically: SHA-256 `dcd8f156dd0f2491bec832b3d7bd6b39b5e2588edbdc94ece81730b1489c7438`. A four-page PDF print proof was visually inspected but excluded from the deterministic ZIP because Chromium PDF metadata is timestamped.

**Explicit testing boundary:** Chromium `page.goto` is blocked by administrator even for loopback HTTP, so browser tests use `set_content` on the *actual locally compiled PHP-rendered Atlas*, with inlined **test-only** CSS/JS. This is not navigated HTTP, authentic WordPress/Assembler, hosted CSP enforcement, or a production LCP/CLS/INP measurement. Pinned/approved axe-core bundle is absent; do not assert an axe pass or WCAG certification. No Safari/VoiceOver/NVDA tests or independent QD review have been performed.

## Release decision: HOLD

Need isolated WordPress/Assembler staging (including dynamic/reusable shortcode and Jetpack behavior), real HTTP navigation and browser security headers, a reviewed pinned axe-core bundle, manual assistive-technology coverage, Safari, hosted Core Web Vitals, individual NASA photo-rights clearance, independent editorial and engineering review, founder approval, and successful CI **on exact head**. The R40 issue of unnecessary asset loads on unrelated singular WordPress pages remains **unresolved**. This R41 patch does not claim to fix it. Do not install or merge while any gate is outstanding.
