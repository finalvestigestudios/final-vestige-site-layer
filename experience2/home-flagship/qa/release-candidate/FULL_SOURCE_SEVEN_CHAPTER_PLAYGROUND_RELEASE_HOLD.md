# EX2: real source-controlled seven-chapter Gutenberg Save — RELEASE HOLD

Date: 2026-11-03. This DRAFT is stacked on PR #808 exact head 7f4a10ccf8c1849f03dd6aed9b88dabb42a69be1. Frozen PR #49 and live page 6 MUST NOT be touched.

## What this changes

PR #808 proved Gutenberg could save a tiny synthetic 8,408-byte Gutenberg candidate byte-for-byte. That did NOT include the actual complete interactive flagship source.

This PR generates an offline test candidate using the real experience2/home-flagship/index.html, its SIX real CSS files and FOUR real JavaScript files from this exact checkout. It preserves all seven chapter-navigation targets, the Franklin archival folio, the reviewed original-NYPL-catalog fallback, and the complete evidence-first source-controlled markup and behavior. Its manifest holds exact SHA-256 fingerprints of all eleven source files. No real page-6 source is stored in GitHub.

The existing isolated WordPress Playground editor runner is reused without modification: ephemeral local WP core, real Chromium/Gutenberg editor Save, byte-exact SHA-256 database readback, and mandatory proof of owned draft deletion. No production API calls, subscriptions or real subscriber data.

## Explicit limitations

The flagship source is real. The appended 72 Margins texts, initial contrast CSS wrapper, and Jetpack subscription block are SYNTHETIC fixtures. This is NOT the exact published page 6 or a deployable candidate. Inlining CSS/JS is solely to test WordPress Custom HTML serialization, not a production asset delivery recommendation.

The free Playground default theme is not WordPress.com's active Assembler v0.0.126 or its global styles, templates and hosted Jetpack/CSP behavior. This test does not measure genuine front-end rendering, keyboard behavior, WCAG 2.2 AA, 200% zoom, image network transfer sizes, Lighthouse or field CWV. NYPL image reuse rights remain unresolved; its source catalog link is preserved, but the unverified reproduction is withheld. Both genuine NYPL record links already present in the source-controlled flagship are preserved, with no extra test-only link injected.

The active WordPress account reports only production site ID 256784396; Personal plan does not supply a native staging clone. An included wpcomstaging URL is not a second staging site. No Business upgrade recommended. Apollo #158/#812 and Mind #171/#806/#813 work remain isolated.

## How to verify

The new workflow, .github/workflows/ex2-full-source-flagship-gutenberg-HOLD.yml, tests source/rights/chapters offline and then uses pinned free WordPress Playground CLI 3.1.56 and Playwright 1.56.1 to save the assembled full-source HTML in Gutenberg. PASS requires actual WordPress Save receipt, matching saved/source SHA-256, nine true preservation checks and confirmed deletion. Do not claim CI PASS before checking this exact PR head. All staging source files are deleted on the runner and are not uploaded as artifacts.

## Release gates remain open

1. Front-end saved-candidate rendering using isolated Assembler theme, responsive screenshots 320/390/768/1440/1920, 200% zoom, real network image transfer bytes and entitlement/rights.
2. Browser axe with no silent skips, keyboard/touch/reduced-motion/no-JS/Safari tests; manual WCAG 2.2 AA and assistive technology.
3. Actual live-content-derived Gutenberg candidate saved only into authorized isolated WP, complete Focus/Jetpack/72-Margins checks; no production database or subscriber export.
4. Measured Lighthouse/field CWV distinctions, independent QD, founder visual choice between three existing art directions, and explicit founder release approval.
5. No production WordPress/theme/settings/nav/plugin changes, no merge or deployment, no touch of frozen PR #49.

Status: DRAFT / HOLD until all release gates are independently qualified.
