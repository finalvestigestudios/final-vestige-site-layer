# Apollo R147 | actual WordPress source-custody gate | 2026-11-05

**BUILT, isolated staging only.** Issue #150, conversion issue #820, charter #818. Independent from homepage PR #49 and Research Desk PR #158.

## Actual WordPress authorized-read audit
Read-only content for WordPress page 2017 (published Apollo 1 Evidence Atlas), modified 2026-11-04T17:09:24. Canonical URL: https://finalvestige.com/apollo-1-evidence-atlas/ . The raw Gutenberg content has 96,274 JavaScript characters, UTF-8 SHA-256 cdaca5ae9d10534a067a8f4095a1362eb1078af48694238860d7f470233849bc. This is not the full rendered WordPress page.

The R143–R145 *committed* source validator was executed in V8 on those actual raw WordPress bytes: BEFORE one blocker PUBLISHED_GALLERY_ENHANCEMENT_DEFECT, 1 chronology, 1 gallery, 3 figures, 3 original source links and 0 parser warnings. In-memory one-character repair yields 96,275 characters, SHA-256 39dd5adcfe1a4ad1d501a1a94d760b1037111a487908698e649ecaa5103334e7. AFTER: 0 source structure blockers. No actual browser evidence is implied.

## Added code
r147_snapshot_gate.cjs pins raw and repaired hashes, CMS record ID, status, date, canonical permalink, and a separately authenticated read export metadata contract. Any source changes cause fail-closed rejection; do not merely change hash to get a PASS. The existing R145 review preview runs ONLY after metadata/hash checks. Only a NEW local output directory can be created. The original WP content is NOT included in this PR and cannot be published by this script. test_r147_snapshot_gate.cjs contains adversarial Node test cases for both provenance and staged-release guards.

## Reproduction
Create locally the exact read-only WP page 2017 Gutenberg content as input.html. Save separate metadata.json containing id 2017; slug apollo-1-evidence-atlas; status publish; modified 2026-11-04T17:09:24; link https://finalvestige.com/apollo-1-evidence-atlas/; source WORDPRESS_AUTHORIZED_READ. Then:

    node --test experience2/apollo-creator-bridge/test_r147_snapshot_gate.cjs
    node experience2/apollo-creator-bridge/r147_snapshot_gate.cjs --input input.html --metadata metadata.json --out new-review-directory
    python experience2/apollo-creator-bridge/r146_offline_browser_acceptance.py --input new-review-directory/apollo-r147-offline-review.html --out another-new-browser-directory

No actual export file or browser output was generated in this run because the local container/Python runtime returned a system error. Browser fixtures from R146 do not substitute for actual WP export, WordPress theme, or p75 CWV. No axe, native Node execution or screenshot success is claimed here.

## Conversion and release
Audience hypothesis: Grok Apollo long-form/Shorts traffic -> published Atlas -> single existing Read the full investigation action -> potential rights-cleared educator dossier ONLY after merchant and founder verification -> independently verified paid purchases minus fees/refunds. No matching paid Apollo SKU, Grok published asset, qualified traffic or realized revenue verified. No paid CTA or tracking script introduced.

**STAGING HOLD:** actual-export Playwright/axe/keyboard/touch/320–1920 screenshots, live WordPress-theme smoke, image delivery, LCP/CLS, historical claims, photograph-specific commercial rights, existing sellable offer and checkout, exact-head CI, independent QD and founder approval are all outstanding. No production, WordPress, social, merchant, email or expense changes.