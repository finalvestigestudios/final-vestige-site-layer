# Apollo 1 Evidence Atlas R40 — WordPress staging adapter (HOLD)

2026-11-01. **DRAFT. This component is NOT installed, approved, merged, or live.** Branch isolates its changes within `experience2/evidence-atlas/`; base is R39 draft PR #430 at `933474faab95c200691ec846d61c5160116921fd`. Frozen homepage PR #49, homepage lead work, Research Desk PR #158 and existing site settings/content were not modified.

## What R40 closes

R39 emitted a whole `<!doctype html><html><main>...` standalone Atlas preview. Inserting that document into a WordPress shortcode would create nested page/landmark markup and embed inline style/script into the CMS. **R40 compiles a WordPress-safe section fragment**, keeps the existing R39 CSS/JS as external, registered assets, and provides an isolated, read-only `[fv_ex2_evidence_atlas]` PHP shortcode adapter. Its provenance is the original R37 six-record NASA crosswalk with git blob `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea`; the builder refuses mutation. The WordPress adapter pins the compiled HTML fragment by exact SHA-256 `45a552d460cf93a1b10ba5821a662956bee9a77f87c147b22182b805f5d27321`. If the template is missing or altered, it falls back to the original Apollo 1 investigation, without exposing unreviewed data. A second shortcode displays an in-page link rather than duplicate IDs because R39's controller supports one root.

All six NASA source links remain external, and all six photo reuse assessments remain `INDIVIDUAL_REVIEW_REQUIRED`. There are **zero** embedded photographs, geospatial coordinates, speculative pins, or evidence-relationship edges. 1966/1967/2017 source dates describe photographs, not a fire-reconstruction timeline. NASA official policy: https://www.nasa.gov/nasa-brand-center/; this policy does not independently clear individual image rights, publicity or third-party materials.

## Reproduce without WordPress writes

From repo root with R39 ancestry and Python, PHP, Playwright, Chromium available:

```bash
python -m unittest discover -s experience2/evidence-atlas -p test_atlas.py -q
python -m unittest discover -s experience2/evidence-atlas/tests -p test_wordpress_stage.py -q
python experience2/evidence-atlas/build_wordpress_stage.py --output /tmp/fv-apollo-r40-stage
php -l experience2/evidence-atlas/final-vestige-ex2-evidence-atlas.php
python experience2/evidence-atlas/tests/browser_wordpress_stage.py --output /tmp/fv-apollo-r40-browser
# Optional local, preapproved pinned axe.min.js (no download / no paid service):
python experience2/evidence-atlas/tests/browser_wordpress_stage.py --output /tmp/fv-apollo-r40-axe --axe /approved/path/axe.min.js
```

Generated installable *staging candidate files* live at `/tmp/fv-apollo-r40-stage/fv-ex2-evidence-atlas/`; they are deterministic and not automatically deployed. `STAGING-MANIFEST.json` pins each compiled file by SHA-256. Do not activate on production; approved standalone test WordPress instance is required. The adapter deliberately enqueues Atlas assets on every singular page to avoid the nested/dynamic shortcode asset gap seen in R35. This introduces an **untested unnecessary-asset-load cost** on singular pages without the shortcode; gate in actual WordPress staging before approval.

## Executed local QA and exact limits

- Original R39 source-custody suite: **11/11 Python tests PASS**.
- New R40 stage/PHP lifecycle suite: **12/12 PASS**, including exact NASA IDs, unique ID/ARIA targets, no nested main, external CSS/JS, second shortcode protection, missing fragment fallback, mutated-fragment rejection, and deterministic output.
- Real Chromium of **actual compiled PHP shortcode HTML**: **14/14 PASS** at widths 320, 360, 390, 768, 1024, 1440, 1920, each with JS enabled and disabled, plus keyboard drawer, mobile touch filter/reset, year/search counts, reduced-motion emulation, focus, no overflow or unexpected remote requests. Four screenshots matched byte-for-byte across two independent runs. PHP lint passed.
- Chromium `page.goto` on a fully intercepted HTTPS test URL returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` in this environment. QA therefore used `page.set_content` on the exact locally rendered PHP markup and bundled CSS/JS. **It is not a genuine navigated HTTP or real WordPress test; CSP and LCP/CLS/INP are NOT certified.** Attempted PerformanceObserver entries were unavailable; no synthetic numbers are promoted as hosted CWV.
- No preapproved local axe-core bundle, so **axe not executed**, and Safari, NVDA/VoiceOver, real WordPress/Assembler, Jetpack, media CDN, QD independent review, green hosted CI, founder art-direction approval and each NASA media-rights decision are still outstanding.

## Release: HARD HOLD

Review first on an isolated WordPress installation with Assembler theme, nested/reusable blocks, shortcode lifecycle, actual HTTP headers, keyboard and screen readers, 320–1920 widths and 200% zoom; run approved pinned axe-core and Lighthouse/Web Vitals under navigated HTTP, then evaluate the singular-page asset cost. Independent editorial/rights review, QD and successful CI on the exact final commit are prerequisites. **No production merge or WordPress writes authorized.**
