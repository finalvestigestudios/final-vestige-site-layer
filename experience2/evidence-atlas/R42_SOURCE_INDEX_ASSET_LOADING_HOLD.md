# Apollo Evidence Atlas R42 — source index and demand-loaded assets

**Status: DRAFT / STAGING_HOLD.** This change is stacked only on R41 PR #447 for Issue #150. It does not modify or approve homepage PR #49, lead homepage branches, Research Desk PR #158, production WordPress, publishing, settings, or paid services.

## Implemented

- Six source-custody-backed index anchors link to the actual Atlas evidence records. They use R37 catalog labels and photography dates rather than invented pins, location claims, or causal connections. The links work without JavaScript.
- JavaScript-enhanced source jumps reset any incompatible active filter, restore the full evidence set, preserve the URL hash, and focus the requested article for keyboard users. If an index target or record ID is altered, the enhancement does not expose unusable controls; all six original records remain readable.
- The WordPress adapter now registers its CSS/JS on the early enqueue hook, enqueues early for a direct top-level shortcode, and enqueues inside a successfully rendered shortcode for dynamic/reusable/template-part content. Pages without a rendered shortcode no longer incur Atlas assets in the PHP lifecycle stub. Late CSS delivery and possible flash of unstyled content must be measured on genuine WordPress/Assembler staging.
- The original six NASA links and photo-custody records are preserved. Six image-reuse assessments remain individual-review-required. Zero image binaries, speculative geographic pins, map edges, or reconstructed fire sequence claims were introduced. Printed output still restores all six original source records and custody details.

## Reproduction

From a full checkout with Python Playwright and local Chromium:
1. Run Python unittest discovery for test_atlas.py and tests/test_wordpress_stage.py.
2. Run PHP syntax checks on the plugin and tests/wordpress_shortcode_probe.php, and Node syntax check on atlas.js.
3. Run build_wordpress_stage.py with --output pointing to an empty directory.
4. Run tests/browser_regression_r42.py --output pointing to an empty QA directory.
5. Run tests/build_r42_review.py with --qa and --out; repeat the archive build to compare SHA-256.

**Observed locally:** 26/26 Python unit tests; PHP and Node syntax checks pass; inherited R41 Chromium regression 14/14; R42 real Chromium component tests 14/14 across 320, 360, 390, 768, 1024, 1440, and 1920 CSS pixels with JavaScript enabled and disabled. Keyboard and touch controls, source-jump focus and hash restoration, malformed-index fail-open behavior, print preservation, and no horizontal overflow passed. Four repeatable screenshots were captured at 390 and 1440px, with JS enabled/disabled.

**Source custody lock:** unchanged R37 crosswalk Git blob ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea. Compiled WordPress fragment SHA-256 1825ac0de797f6804c3d2eadfb52f0034d4c4c84e88d0c7bd4a32032df891894 is enforced by the adapter.

## Release blockers / measurement limits

- Chromium navigation to even localhost is blocked by ERR_BLOCKED_BY_ADMINISTRATOR. Browser tests run real Chromium on actual compiled PHP-rendered Atlas markup using Playwright set_content, not HTTP navigation, installed WordPress, or HTTP CSP.
- Synthetic Playwright LCP/CLS observations are marked as such in the QA receipt. They are **not** hosted Core Web Vitals or field-performance certification. Hosted LCP/INP/CLS and site-specific asset-load comparisons are still required.
- No approved local axe-core bundle was available; axe certification, VoiceOver/NVDA, Safari, independent accessibility and editorial QA, and exact-head green CI remain outstanding.
- No real isolated WordPress/Assembler lifecycle test exists yet; validate reusable and dynamic shortcode placement, late CSS, footer scripts, caching and Jetpack. Individual NASA photo licensing/personality-rights review and founder art-direction/release approval remain outstanding.

**Decision: HOLD.** Nothing merged, activated, installed, or deployed.
