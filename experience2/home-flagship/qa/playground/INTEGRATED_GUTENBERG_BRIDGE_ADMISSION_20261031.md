# Seven-Chapter + Live Gutenberg: Isolated WordPress Acceptance Bridge

**Draft / release HOLD. No production writes, merges, theme edits or install permission.** This companion is stacked directly on selective homepage migration PR #408 at `0ef9c9b33f9009fbbd2e1e7aa2b1d528679edcb4`; frozen PR #49 is unchanged. Apollo Research Desk PR #158 and Mind/affiliate Issue #171 remain independent.

## Why this matters

The previous Playground Blueprint in PR #395 inserted *only* the seven-chapter shortcode. That could not test the **actual integrated Gutenberg page** retaining 72 Hidden in the Margins records, Jetpack subscriptions, original Focus CTA, and original query/editorial blocks. PR #408 made a successful **read-only source migration** but did not wire its complete candidate into native WordPress staging. The new `make_integrated_playground_bridge.cjs` joins these reviewed lanes without introducing another chapter or graphic concept.

The bridge generates PR #395's original **19-step** local WordPress/Assembler Blueprint, verifies an independently supplied **PUBLIC** page-6 raw Gutenberg SHA-256 and the exact approved seven-chapter fragment SHA-256 (`a868423c033a179d1821bb9eb1cf7b5c6c07106097e18cce6afe58b79f908cc1`), invokes the existing selective hero-block assembler and replaces the isolated Blueprint's `runPHP` bootstrap. WordPress creates a local front page using the **full** integrated Gutenberg content. The complete page is encoded inside the private Blueprint bootstrap **not** added as a directly requestable plugin file. An exact-content `render_block` hook substitutes only the flagship Custom HTML block with the existing media-authenticated local shortcode. Other Gutenberg blocks are left to WordPress to render normally; no fake Jetpack email endpoint is introduced.

Original controls retained: Assembler theme, local environment + explicit permission, 15 source/media file writes, SHA-256 archival media checks, rejection of changed page/fragment content, no database importer, no production host and no existing-output overwrite. **Without independently verified image-original SHA-256 values the local preview remains CLOSED**; this code neither invents hashes nor claims rights approval.

## Reproduce from exact Git checkout (private files only)

```bash
node experience2/home-flagship/qa/playground/make_integrated_playground_bridge.cjs \
  --public-page /private/page6-public-gutenberg.html \
  --page-sha256 <FRESH_VERIFIED_SHA256_OF_PAGE_ID_6> \
  --trusted-media-manifest /private/reviewed-media.json \
  --output /private/fv-integrated.blueprint.json \
  --receipt /private/fv-integrated.receipt.json

node --test experience2/home-flagship/qa/playground/test_integrated_playground_bridge.cjs
```

Only a **public page-content snapshot** is admissible: never feed a WordPress database export, passwords, site settings, subscribers or user records. The previous public page fingerprint `52f3a353d092c025b2c527058d2ae695a3d3f2d21bbaf4722955c30f3b784cab` is an observation, **not** a permanent source assumption; re-read page ID 6. Generated Blueprints contain that public page and must remain private (file mode 0600); do not commit or serve them publicly.

## Actual executed evidence vs outstanding gates

- **5/5 executable Node regression tests passed** against the original PR #382 seven-chapter fragment, PR #408 actual selective migration code and a previously generated PR #388 Blueprint (the media-metadata-only precursor). Tests cover protected content, exact source fingerprints, negative controls, no direct-public integrated file, PHP lint of plugin/bootstrap and **real PHP CLI execution** of the selective `render_block` callback in a controlled WordPress-function mock.
- Tested original JS blob IDs: bridge `fb6f7b9a89bfbadfabc1c6ca5bb70eaf66955ae0`, tests `b98115ce29c711876238fe62c3e7956d2b441cba`. Actual final PR head and GitHub CI status must be checked separately.
- **NOT TESTED:** a running WordPress Playground/Assembler instance, authentic media bytes or rights, real Jetpack form/confirmation/delivery, archive image loading in browser, mobile/keyboard/zoom/reduced-motion/screen-reader acceptance of the combined WordPress page, axe, Safari, Lighthouse/CWV, hosted cookies/CSP, QD or CI. The local environment's DNS cannot retrieve the official theme/media resources.

**Next release gate:** run this integrated Blueprint on a free, isolated WordPress Playground or local WordPress installation with verified originals; gather first-party HTTP images, screenshot matrix at 320/360/390/768/1024/1440/1920 and 200% zoom, axe WCAG 2.2 AA, no-JS/keyboard/touch/reduced-motion, and measured Lighthouse; explicitly compare Playground to WordPress.com Atomic and Jetpack limitations. No upgrade to a paid WordPress plan is proposed. Founder design choice, rights, CI/QD and exact release authorization remain **HOLD**.
