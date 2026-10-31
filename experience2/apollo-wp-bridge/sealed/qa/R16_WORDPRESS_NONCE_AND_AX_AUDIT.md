# Apollo Experience 2.0 — R16 WordPress nonce parity and Chromium accessibility tree

**2026-10-31 PT · DRAFT / HOLD · Issue #150 · Stacked on R15 PR #276 at `e4f67809b02bf22d0f01ffe8e894b76ff61c0c7e`.**

## Confirmed compatibility defect

The prior staging adapter used `check_ajax_referer('fv_ex2_apollo_sealed')` with WordPress's **default `stop=true`**. On an invalid token real WordPress outputs `-1` and stops, contradicting the existing local shim's claim that unauthenticated/invalid requests produce an **empty HTTP 403**. The existing shims accepted only a single argument, so they hid the discrepancy. Official WordPress API: https://developer.wordpress.org/reference/functions/check_ajax_referer/ (reviewed October 31, 2026).

The adapter now explicitly validates the `_wpnonce` input as a nonempty, bounded string; checks editor permission and staging opt-in separately; invokes `check_ajax_referer('fv_ex2_apollo_sealed', '_wpnonce', false)`; accepts **only integer 1 or 2** as a valid WordPress nonce; and itself returns an **empty, uncached 403** on failure. A fabricated `_ajax_nonce` can neither shadow nor rescue the explicitly required `_wpnonce` parameter. There is no public AJAX route and no added frontend JS or new third-party dependency.

Both test-only PHP WordPress shims now model WP's default `-1` failure response if `$stop=true`; the local HTTP shim supplies a synthetic valid 12–24h nonce result (`2`) and `no-store` response headers. Existing test expectation for the old mock exit code was repaired to require empty 403. **This is compatibility testing via synthetic shims, not an installed WordPress certification.**

## Actual tests and results

- **78/78** Python/PHP test cases passed locally (68 existing R15 cases plus 10 new adversarial HTTP nonce-contract cases). Valid current and older nonces, unauthorized editors, missing/blank/oversized/array tokens, competing `_ajax_nonce`, and no-body/no-cache denial are exercised over a **real PHP localhost HTTP server**.
- **7/7** real Chromium Playwright widths (320, 360, 390, 768, 1024, 1440, 1920 px) passed, including existing source-year lens, keyboard native radios, touch, CSS-only no-JS, reduced motion, anchor recovery, responsive layouts and source-limitation disclosures.
- **7/7** real Chromium CDP accessibility-tree checks passed on the pinned PHP-rendered content. **174 named actionable AX elements at each tested width** in baseline, with rechecks after 1966 filtering, reset and disclosure opening; no unnamed interactive AX nodes in inspected states. Six source-year cards, all link anchors and unique element IDs were checked; hidden-source links are removed from the accessibility tree when filtered. Two additional AX screenshots at 390/1440 px generated with SHA receipts.
- 14 existing responsive screenshots + 2 AX-state screenshots; no observed synthetic CLS across seven widths. Local synthetic LCP was **156–452 ms** where observable; 1440 px did **not** produce usable LCP. These are **not** hosted or field CWV values.
- SHA-256 deterministic private staging plugin ZIP built twice byte-for-byte identical: `3a3dd0b067b50d5d3090e1efb1cf4dc481f2ce2ac383e94d89895421e7e46923`. Embedded PHP SHA-256: `1db6caaaeb50921a28b31ed14ededb0c76fe070da2dc086aae1475dc9246b54d`.
- **Strict `--require-axe` intentionally fails closed**, with `RELEASE HOLD` because no externally verified axe-core bundle + SHA pin was available. CDP AX checks are NOT a substitute for axe-core or manual accessibility certification.

## Historical/editorial custody

No edits to the original 12 pinned Apollo source files at `74375657f2cdaac0710f94c6de6c24534ee06858`, their six NASA catalog records, claim/source pairings, source chronology, image gallery, curated non-geolocated Atlas, limitations or rights flags. No NASA media embedded or newly licensed; all photographs remain **external NASA links**. NASA guideline: https://www.nasa.gov/nasa-brand-center/images-and-media/. No speculative geographic pins, edges or implied NASA endorsement.

## Reproduce locally

From `experience2/apollo-wp-bridge/sealed/`, with PHP CLI, Python Playwright and Chromium:

```sh
php -l fv-ex2-apollo-sealed-template.php
php -l qa/http_wp_router.php
php -l qa/mock_wordpress.php
python -m unittest discover -s qa -p 'test_*.py' -q
python qa/browser_exact.py
python qa/ax_tree_r16.py
python qa/browser_exact.py --require-axe  # expected RELEASE HOLD until independently verified axe bundle is supplied
python build_sealed.py --out R16-private-review.zip
```

## Non-waivable release gates

Actual isolated WordPress Playground/staging with correct current Assembler theme/Jetpack, WordPress core auth/session/nonces, browser-enforced HTTP CSP/cookies/iframe-download behavior, verified axe-core, Safari/VoiceOver/NVDA, real-device/hosted LCP/INP/CLS, media item rights review if any image would be copied, independent QD, exact GitHub-head CI, founder visual approval. Loopback navigation with Chromium in this environment returns `net::ERR_BLOCKED_BY_ADMINISTRATOR`; the PHP HTTP tests therefore **do not** establish browser-enforced HTTP behavior. Retain **HOLD**. No WordPress writes, merges, production deploys, paid services, frozen homepage PR #49 or Research Desk PR #158 edits.
