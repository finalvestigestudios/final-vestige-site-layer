# Companion admission: complete seven-chapter WordPress page with local archival media

**DRAFT · RELEASE HOLD.** This is an *additional, stricter end-to-end renderer test*, **not** a replacement for the existing private authenticated staging lane described in `qa/playground/README.md`, or PR #224's sealed preview. Never install on finalvestige.com. Source baseline PR #382, `599fe8defd00ac24420f6f752cbc93f0ebc2466f`.

## Why a companion exists

The existing staging lane uses an authenticated PHP private preview iframe and needs a locally obtained/pinned Assembler ZIP. This companion tests a different integration question: **Can the full WordPress post-content template display the seven-chapter fragment without extra global masthead/footer or duplicate main/headings, while loading the three archival originals as truly first-party files?** It must run within an isolated developer WordPress Playground instance only.

## Inputs and safe commands

From this complete, exact Git checkout:

```sh
node --test experience2/home-flagship/qa/playground/test_playground_blueprint.cjs
node experience2/home-flagship/qa/playground/make_playground_blueprint.cjs --output /private/fv-ex2-playground.json
```

The new generator delegates to existing `qa/release-candidate/build_release_review.cjs`, which checks the canonical HTML Git blob `70ebe0d8e122048343c99a3c6adc6f7ac498ed7f` and ten exact asset Git blobs. It produces a **self-contained, approximately 120-KB Blueprint** containing the true HTML fragment, six stylesheets, four scripts, and a PHP-only review adapter. No GitHub/raw assets are requested after Blueprint generation.

Load the resulting JSON into a **fresh free WordPress Playground** session or local Playground CLI. It fetches the official Assembler ZIP from WordPress.com's `public-api.wordpress.com/rest/v1/themes/download/assembler.zip` endpoint and only three *public* original images. It refuses to render unless the WordPress environment is `local`, the plugin's explicit local-review constant is true, the current hostname does not contain `finalvestige.com`, all 11 source SHA-256s match, and the 3 images match verified production media sizes/dimensions. A local WordPress page is created with `[fv_ex2_stage_home]` inside a native shortcode block. All three image `src` URLs are rewritten to local Playground plugin media; remote `srcset` is removed. The actual Assembler theme supplies site-level navigation and page wrapper.

**No subscribers, secrets, user records, private WXR, production theme customizations, Jetpack setup, data sync, new offer, or production site writes.**

Public-source expected images from read-only authenticated WP media:
- ID 473 Apollo WebP: 78,346 B / 1041×810.
- ID 474 Franklin JPEG: 466,043 B / 960×1526.
- ID 1258 NYPL original JPEG: 5,553,669 B / 5667×3831.

These are metadata witnesses only until WordPress actually fetches and browser measures the bytes. Editorial reproduction rights are a **separate unresolved release gate**.

Once an isolated developer site genuinely runs, use a locally verified axe-core distributable and execute:

```sh
python experience2/home-flagship/qa/playground/verify_playground_browser.py \
 --url '<isolated Playground/localhost URL>' --axe-js /private/axe.min.js \
 --output-dir /private/fv-playground-evidence
```

It fail-closes on production URLs, missing axe, absent runtime, unexpected theme landmarks, missing 7 chapters or 3 original cases, errors at 320/360/390/768/1024/1440/1920, keyboard/lens/observer/chooser failures, no-JS loss, 200% zoom overflow, image HTTP byte/dimension mismatch, and WCAG axe violations or incomplete results. It captures screenshots and JSON **only when executed**. Actual independent keyboard/assistive-tech review, Lighthouse, rights, hosted CSP/cookies, QD+CI and founder release approval remain necessary.

## Executed local evidence

A **19-step**, self-contained Blueprint was generated from the preceding exact source review ZIP (all **11/11 SHA-256 file checks passed**). The JSON parsed correctly; PHP 8.4 CLI lint passed. Three CLI tests of local vs production environment and explicit authorization returned expected *fail-closed* outcomes; missing image originals also failed closed. This is only **offline source/gate QA**, not a WordPress runtime. The new six committed Node tests **have not been run against a complete exact Git checkout** in this environment. Local Chromium navigation and official theme-ZIP retrieval are blocked, so no Assembler rendered screenshots, axe passes, Lighthouse, media HTTP transfers or CI/QD are claimed.

The existing parallel private preview lane and its exact-head harness remain the primary hosted stage reference. This companion must not substitute for it silently. No production modifications, merges or deployments occurred. Preserve published 72 Margins records, Jetpack and Focus; keep frozen PR #49 unchanged.

**RELEASE: HOLD.**
