# Experience 2.0 — local WordPress execution bridge (2026-11-07)

**DRAFT / release HOLD.** Isolated child of PR #1393 at \`94181f88f0de0a3b735ed125842205f38cc9eb1a\`. Frozen PR #49 and public WordPress Page 6 are not modified.

## Why this is a substantive integration step

Previous PRs #1386 and #1393 delivered a pinned, guarded local Playground ZIP but did not connect **starting real WordPress** to the existing exact-page acceptance harness. Repeated local Python/PHP fixture passes did not establish native Assembler behavior. This change adds one source-controlled runner that handles that handoff and refuses source drift, non-loopback probes, wrong port, unexpected redirects, missing WordPress shell, and the absence of an actual flagship.

It deliberately does **not** add another visual chapter, commerce script, merchant link, popup, or analytics tracking. It reuses \`verify_integrated_playground.py\` instead of writing another unqualified accessibility checker.

## Exact pins and artifacts

- Parent protected local bundle SHA-256: \`9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d\`.
- Underlying candidate Blueprint SHA-256: \`300c79f7936d7fdf58294bb96e7b0cd1ebc0b349cdf4d2c4d13e5ec52000b23f\`.
- Assembler theme Git commit: \`75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f\`.
- This runner checks ZIP bytes, **all five allowed members**, two PHP payload hashes, approved steps/order, first-step local admission, Assembler pin, and opening page before starting npm.
- It launches the actual WordPress Playground CLI in an isolated temporary directory, forces a \`127.0.0.1\` site URL on port 9400–9499, probes read-only and refuses redirects, then invokes the existing native Playwright/Assembler acceptance at the real loopback URL. The runner never invokes WordPress.com REST writes, subscribers, checkout, email delivery, or production administration.
- Source receipts are labelled **source only**; runtime receipts and process logs are separate and cannot be misread as production/WCAG qualification.

## Reproduction on a machine with npm/Assembler network access

Place the protected ZIP from PR #1393 outside the repository. Keep the two new scripts alongside the existing \`verify_integrated_playground.py\`. From this repository checkout:

\`\`\`bash
python -m unittest experience2.home-flagship.playground.test_run_local_wordpress_acceptance
\`\`\`

The folder name contains a hyphen; if Python module loading does not work in your shell, use:

\`\`\`bash
python experience2/home-flagship/playground/test_run_local_wordpress_acceptance.py -v
FV_EX2_BUNDLE_PATH=/absolute/path/fv-ex2-local-cli-preflight-guarded.zip \
  python experience2/home-flagship/playground/test_run_local_wordpress_acceptance.py -v
python experience2/home-flagship/playground/run_local_wordpress_acceptance.py \
  --bundle /absolute/path/fv-ex2-local-cli-preflight-guarded.zip \
  --output ./fv-ex2-acceptance --preflight-only
python experience2/home-flagship/playground/run_local_wordpress_acceptance.py \
  --bundle /absolute/path/fv-ex2-local-cli-preflight-guarded.zip \
  --audit experience2/home-flagship/playground/verify_integrated_playground.py \
  --axe /absolute/path/to/official/axe.min.js \
  --output ./fv-ex2-acceptance --port 9400 --timeout 90
\`\`\`

The last command requires Node.js and the documented \`@wp-playground/cli\` runtime plus network access to GitHub for the pinned Assembler source. The runner intentionally returns **nonzero** even when the native browser audit executed: that audit itself keeps Lighthouse, real CWV and other release gates open. A \`SOURCE_ONLY_PASS\` printed by \`--preflight-only\` certifies **nothing** about WordPress execution. Keep ZIP files and QA output private; no subscriber or authentication data should be imported.

Official WordPress support:
- Blueprint ZIP bundles: https://developer.wordpress.org/playground/blueprints/bundles/
- CLI server, port and site URL: https://wordpress.github.io/wordpress-playground/tl/developers/local-development/wp-playground-cli/

## Actual evidence collected this run

- Seven **synthetic/offline** controls PASS; synthetic fixture is clearly labelled.
- Additional optional exact **real protected ZIP** test PASS: 8/8 including the real pinned bundle.
- Exact uploaded runner Git blob \`efc091ecb2a48f299942fd9c4ef1c17f25037664\` matches tested local source (8,552 UTF-8 bytes).
- Actual npm registry resolution attempted and returned **EAI_AGAIN** for \`registry.npmjs.org\`. WordPress CLI did **not** start. No Assembler-rendered screenshot, screenshot diff, network image transfer, accessibility audit, Lighthouse or field CWV was produced.
- Production account discovery found only \`finalvestige.com\` site 256784396; no authorized staging clone. Personal plan does not offer native staging; **no paid upgrade requested**.

## Source/rights and visual continuity

Read-only WordPress media: Apollo photo #473 1041×810 WebP, 78,346-byte metadata; Franklin note #474 960×1526 JPEG, 466,043-byte metadata; the legacy published NYPL #1258 is a 5667×3831 map, 5,553,669-byte metadata. These sizes are NOT transferred bytes.

Apollo 1 official NASA image record (photo of crew, not proof of ignition mechanism): https://www.nasa.gov/image-detail/apollo-1-crew-honored/ . Franklin published scan is explicitly a printed 1869 reproduction of an 1847/1848 record, not a modern photograph of the museum object: https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg . NYPL's guide links image ID 5003296 as a 1903 BRT context map, not a reconstruction of the 1918 Malbone temporary curve: https://libguides.nypl.org/nyc-rail-transit/companies . NYPL's exact catalogue URL was inaccessible in this run, so keep the **candidate's NYPL image exclusion** and rights/source reconciliation open. The already-public page contains the map; do not edit it without release authorization. No artwork was copied from Blue Corridors.

The existing candidate's seven chapters, 72 historical fragments, five \`/focus/\` destinations, teal/obsidian/antique-gold visual language, Franklin parchment folio, Jetpack/Fieldbook boundary and Mind & Perception disclosure remain untouched.

## Conversion priority

**Offer → funnel step → blocker → change → evidence → owner:** Existing 52-page Seven Day Focus Fieldbook → first-screen evidence-to-Focus action → no actual WordPress/Assembler end-to-end acceptance despite many static passes → source-guarded launch + reuse existing native admission → local source and negative controls PASS / npm-host resolution FAIL / no confirmed leads, sales or net revenue → Interim Engineering + Site QA. Claude owns production instrumentation and checkout; Grok/Praxxis own audience acquisition. The controlling KPI remains verified **net revenue per 1,000 qualified human sessions**, not pageviews or clicks.

## Hold gates

Actual local WordPress/Assembler startup; Chromium screenshots at 320/360/390/768/1440/1920 and 200% zoom; independent axe and manual WCAG 2.2 AA keyboard/touch/reduced-motion/no-JS; genuine image network response bodies and origin/provenance; Lighthouse lab measurements and hosted/field CWV; Focus Jetpack form and delivery verification without subscribing test users; rights signoff; CI/QD exact-head review; founder art-direction and release approval.

No merge, theme/plugin install on public WordPress, subscriber data import, production API write, merchant activation, analytics deployment, social post, email campaign or spending.
