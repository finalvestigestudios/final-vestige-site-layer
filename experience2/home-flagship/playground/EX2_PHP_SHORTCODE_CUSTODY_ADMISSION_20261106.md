# Experience 2.0 — PHP shortcode custody admission (2026-11-06)

**Status: SOURCE-EXACT PHP EXECUTION + LOCAL CHROMIUM PASS; WORDPRESS/ASSEMBLER RELEASE HOLD.** This review-only follow-up is stacked on draft PR #1294, head 88e6a382e717e7a9703df61a8c21060af19d9fd6. Frozen PR #49 (10495883299d53596992c26a8987f629b2904670) is untouched. Issue #150 is the creative charter; #818/#820 govern conversion and attribution. Apollo R&D is separately owned by #158.

## What this closes

Earlier Chromium reports used PHP-extracted static HTML/CSS/JS. This new executable gate loads the **entire exact pinned Playground Blueprint MU-plugin source into real PHP CLI**, using deliberately minimal WordPress API stubs. It invokes the registered wp_enqueue_scripts callback and actual [fv_ex2_playground] shortcode callback rather than only parsing heredocs. It compares PHP-emitted HTML, CSS and JavaScript byte-for-byte to the source heredocs. Then it loads the PHP-emitted output into Chromium, with no external network requests permitted.

This **does not** replace WordPress: the stub has no WordPress core, Assembler styles, REST routing, Gutenberg shortcode/block rendering, Jetpack forms, server caches or database. It is a PHP/runtime custody gate, not a genuine Playground or hosted-WordPress staging gate.

## Exact evidence / commands

- Source: experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json; Git blob **455c6cccbf8a00e6ecc4c2524775010d7ee1762c** on parent head, SHA-256 (full file) **89a78c35471360880c6e0053ad2f8618b35fcc0c1a5b3a5efa87989482c8a2e8**.
- New test command: python3 experience2/home-flagship/playground/verify_php_shortcode_execution.py (requires PHP CLI, Python Playwright and Chromium at /usr/bin/chromium; no site secrets).
- Local test record: **19/19 PASS**, consisting of 3 PHP-emitted segment-exactness tests, 1 preservation/nonlive-label test, 3 independent fail-closed isolation negatives, and **12 PHP-emitted Chromium layouts** (320×568, 360×640, 390×667, 768×900, 1440×900, 1920×900, each JS on/off). No document overflow, broken internal fragment targets, JS page errors or sub-44px contextual actions detected in those scenarios. The 390×667 Focus action ended at **658.97px** inside the 667px screen.
- PHP 8.4 syntax PASS. Supplementary screenshots were captured at 390×667 JS on/off and 1440×900; a CSS zoom study was also captured. Screenshot transfer, image source network, axe/WCAG, real Lighthouse and CWV **are not certified** by these tests.
- All 72 public Margins records, 7 chapter anchors and 5 Focus destinations were retained. Existing 52-page Fieldbook and live Jetpack configuration were not edited. No new media, merchant claims, analytics instrumentation or paid tooling.
- WordPress read-only site inventory on 2026-11-06 found only production ID 256784396. Current active theme is **Assembler**. WordPress Page **6** is published and reported modified 2026-11-05T12:07:24. The WordPress.com Personal plan lacks a native staging clone, and the listed wpcomstaging address is not a clone.

## Security/release isolation negatives

1. The wrong review-secret option causes the PHP plugin to register neither emitted assets nor content.
2. The wrong page slug causes the enqueues and shortcode content to be empty.
3. Both wrong state inputs likewise produce nothing.

The static browser aborts external requests, so a pass does **not** mean Apollo/Franklin images loaded. CSS zoom is not equivalent to full manual browser zoom or screen-reader testing.

## Conversion-first decision

**OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:** Free 52-page Focus Fieldbook → above-fold historical trust / contextual action → earlier tests did not verify PHP shortcode activation and asset guarding → native PHP callback execution + browser evidence → 19 cases pass, but **zero confirmed leads, orders, affiliate sales or net revenue** established → interim homepage engineering and independent Site QA. Claude owns attribution and merchant/checkout integration; Grok and Praxxis own social acquisition.

## Outstanding release gates — HOLD

The **next highest priority** is the actual unmodified source candidate in **isolated WordPress Playground with Assembler and public content only**, not more conceptual chapters. Run exact-source WordPress-native screenshots at 320/360/390/768/1440/1920 and 200% zoom, WordPress routing/shortcode tests, axe with real library (fail closed), keyboard/touch/reduced-motion/no-JS, and genuine archival image requests with status/bytes/dimensions/provenance. Run real Lighthouse and inspect source rights. Jetpack's actual subscribed lead confirmation is a distinct gated test, never inferred from URL parameters. Playground is not WordPress.com production hosting and cannot certify WordPress.com cookies/redirects/Jetpack or field CWV. CI and independent exact-head QD remain separate blockers. Founder release authorization remains mandatory.

**No production WordPress, plugin, theme, page, navigation, analytics, newsletter, affiliate, subscriber, spending or merge actions.**
