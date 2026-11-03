# EX2 — Assembler front-end admission, independent QA / RELEASE HOLD

**Date:** 2026-11-03. **Stack:** PR #816 exact source-controlled Gutenberg head `f211c47aa992444356e7341cee9bc95b1dcd3b10`. This PR adds a different gate: actual local WordPress *front-end* rendering with the official Assembler theme. It does not alter frozen PR #49 or production page ID 6.

## What can be claimed

PR #816 already established that Gutenberg preserves an 11-file source-controlled, 120,064-byte seven-chapter synthetic-wrapper candidate byte-for-byte. That did **not** render the candidate through Assembler. The new `playground_assembler_frontend_gate.mjs` spins up **disposable loopback-only Playground**, installs the **free official Automattic Assembler theme ZIP** as a local WordPress theme, saves the candidate through a real Gutenberg editor, and views that *saved draft* on the local WordPress front end.

The theme ZIP URL is `https://public-api.wordpress.com/rest/v1/themes/download/assembler.zip`, linked directly from WordPress.com's free Assembler listing; the workflow prints its downloaded SHA-256 and checks ZIP integrity. **Do not interpret this as a byte-identical copy of the hosted theme version**: WordPress.com presently reports active stylesheet `assembler`, but hosted global-style options, custom templates, plugin effects and theme version may differ. A passing test is isolated theme-family evidence, **not hosted parity**.

The full seven chapter source, six CSS files and four scripts are real GitHub material, but the **72 Margins records, contrast wrapper and Jetpack subscription marker are synthetic fixtures**. No subscriber records, production WXR/database, current page 6 source, author cookies, WP admin tokens or secret material is written to GitHub. The flagged NYPL capture is excluded; two catalog links remain. Public first-party Apollo/Franklin image requests may be observed from GitHub's browser but are never published back to WordPress.

## New independent gates (fail closed)

1. Source manifest exact SHA-256, 11-file custody, 72 synthetic Margins, 2 NYPL record links, 4 scripts and 6 styles, HOLD status.
2. Disposable private draft ownership/token, actual Gutenberg save, raw database byte-identical readback and hard deletion confirmation.
3. Browser sees Assembler in body classes, all seven chapter anchors, full 3-case evidence panels, all 72 Margins records, original CSS and script tags; screens at **320 / 390 / 768 / 1440 / 1920**. No horizontal overflow. Stored screenshots of real **isolated WordPress front end**, not a pasted standalone HTML study.
4. Actual source case-selector tap/click at mobile 390, and authenticated local no-JavaScript preview verifying all cases and source navigation remain present. Manual keyboard/touch parity, screen-reader audits, Safari, zoom and reduced motion remain independent gates; this sprint does not assert them.
5. Require successful public image **response body bytes** for at least one first-party archival asset; record path/status/bytes, never infer bytes from WP media metadata. Full media-rights signoff still required.
6. Run real Chromium axe WCAG 2/2.1/2.2 A/AA tagged checks at 390 and 1440, fail if unavailable or if any violations. Axe passing is **not** WCAG 2.2 AA certification.
7. Artifact includes screenshots/JSON partial results on failure, no production HTML or cookies. No `GITHUB_TOKEN` used beyond read-only checkout.

## CI command and scope

```bash
python -I experience2/home-flagship/qa/release-candidate/write_source_flagship_playground_candidate.py --output /tmp/fv-candidate.html --manifest /tmp/fv-manifest.json
npm install --no-save --no-package-lock --no-audit --no-fund @wp-playground/cli@3.1.56 playwright@1.56.1 @axe-core/playwright@4.10.2
node experience2/home-flagship/qa/release-candidate/playground_assembler_frontend_gate.mjs --self-test
node experience2/home-flagship/qa/release-candidate/playground_assembler_frontend_gate.mjs --candidate /tmp/fv-candidate.html --manifest /tmp/fv-manifest.json --out /tmp/fv-assembler-qa
```

Dedicated workflow: `.github/workflows/ex2-assembler-frontend-gate-HOLD.yml`. Outcome must be checked at **exact PR head**, not inherited CI or local simulation. Archive only the synthetic/local screenshots and concise bounded test receipts. Avoid storing generated rendered HTML or full WordPress databases.

## Release decision / coordination

**HOLD.** This is the missing independent Assembler-family rendering gate, **not** an approved WordPress.com production candidate. Hosted Assembler version/global style/template parity; actual saved page-6-derived content; real 72 Margins items; 52-page Focus delivery; Jetpack signup and deliverability; NYPL image-specific rights; comprehensive keyboard, touch, zoom, reduced motion, no-JS, Safari, assistive-technology and WCAG manual audit; Lighthouse lab measurements and CrUX field CWV; founder art direction and independent QD remain required.

Do not require a native staging clone on the existing WordPress.com Personal plan; the included wpcomstaging.com address is not a staging clone. No spending approval or change in subscription requested. Do not install plugins, deploy, publish, merge, or write to production. This lane owns the homepage only. Apollo #158 and Mind & Perception #171 remain independent. Maintain the three unselected art directions Black Dossier, Museum After Hours, Observatory, and preserve the 7-chapter existing architecture rather than adding new concepts.
