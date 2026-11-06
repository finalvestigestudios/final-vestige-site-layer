# Apollo R158 — deterministic WordPress shortcode staging package (not deployed)

**Status: BUILT / PHP CLI + Chromium-tested / STAGING HOLD.** Scope: Issue #150, conversion #820 / charter #818. Isolated from homepage PR #49 and original Research Desk PR #158. This is a proposal and reproducible build, **not a WP staging installation**.

## Why this exists

The original PR #158 shortcode adapter enqueues CSS/JS only if a top-level singular post contains the literal shortcode during wp_enqueue_scripts. Nested blocks, reusable patterns and shortcodes produced by template parts may not enqueue assets. R158 tests a self-contained staging-only delivery: the shortcode reads byte-verified bundled HTML/CSS/JS and emits both assets at render time. Rendering after the document head is tested. Source/asset mismatch fails closed to a safe investigation link. Repeated shortcode instances avoid duplicate IDs, scripts, and handlers by emitting a return-to-desk link.

**Integration caveat:** Inline style/script output inside block content needs an actual WordPress/Assembler/CSP and caching review. No site has been changed. If the staging environment enforces restrictive CSP or sanitizes shortcode return content, this candidate must be redesigned, not force-deployed. This approach is only a preview candidate.

## Exact source custody

Build reads and checks SHA-256 of R157 HTML; R154 JS; PR #158 base CSS; R156 provenance CSS; R154 compatible CSS; and R157 chronology CSS. Any mismatch stops building; generated PHP checks three artifact hashes at runtime and falls back to the original investigation when assets are missing or modified. No external runtime requests, no analytics, no marketing scripts, no unreviewed paid offer.

## Deterministic build

From the repo root:

    python experience2/apollo-r158/build_staging_package.py --repo . --out /tmp/apollo-r158-build-1
    python experience2/apollo-r158/build_staging_package.py --repo . --out /tmp/apollo-r158-build-2
    sha256sum /tmp/apollo-r158-build-*/fv-apollo-r158-wordpress-staging.zip

For this run the two ZIP files were bit-identical, SHA-256 8d7cef94b83917fa6b8eb555e1b2a077cafd324e1d7372a5ac5d4433a753c0c2, 11,769 bytes. Zip timestamps are normalized; entries sorted; manifest includes every source and bundled SHA-256.

## PHP render + Chromium (emulated WordPress API)

    python experience2/apollo-r158/test_php_shortcodes_browser.py --package /tmp/apollo-r158-build-1/fv-apollo-r158-wordpress-staging.zip --out /tmp/apollo-r158-browser-1

Requires PHP CLI, Python Playwright and locally installed Chromium. The harness invokes **actual PHP plugin code with emulated WordPress hooks**, then renders its returned complete HTML through Chromium with Playwright. Local browser network loopback is blocked in this testing runtime; no actual WordPress was installed or served, and there is no claim of WordPress integration acceptance. It covers 320, 360, 390, 768, 1440, 1920; JS/no-JS; data custody, provenance source drawer, keyboard, touch-eligible width, reduced motion, scrolling, search, external fragment recovery, duplicate shortcode, source tampering and fallback. Screenshots and test receipts are reproducible. Local PerformanceObserver LCP/CLS are **not** real-page field Core Web Vitals. axe-core was unavailable and is **not claimed to have run**.

Two independent executions yielded **110/110 passing assertions** and identical six screenshot hashes. Any change to sources or tester requires rerun.

## Conversion / next action

Historical teacher audience → Grok-sourced Apollo history video (publication unverified) → source-grounded Research Desk → **Read original investigation** (one relevant next action). A paid educator dossier remains *unverified as an existing SKU*. Commercial CTA stays blocked pending verified merchant product/rights/checkout and founder approval. No attributed visitors, sales, customers, refunds or realized net revenue established by this sprint. Keep unique Grok asset IDs/UTMs separate from platform views; apply #820 7/30-day event and paid-order reconciliation.

## Mandatory release gates

Actual staging WordPress with Assembler theme and reusable blocks; media and image rights review (not cleared for commercial packaging); CSP and content filter review; complete axe-core (zero violations and incomplete); screen reader, zoom, real devices, keyboard/touch, real page LCP/CLS/INP; independent QD; hosted CI exact-head; founder release approval. **No production deployment, no affiliate/email/social action, and no spending.**
