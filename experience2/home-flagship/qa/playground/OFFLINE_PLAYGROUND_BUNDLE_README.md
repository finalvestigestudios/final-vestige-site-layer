# Final Vestige — private, self-contained WordPress Playground bundle

**Status: SOURCE-ONLY engineering; actual WordPress/Assembler rendering NOT performed; production RELEASE HOLD.**

## Actual blocker addressed

The current exact-head 19-step integrated Playground Blueprint obtains the Assembler theme and all three archival media originals via remote `resource: url` instructions at runtime. The current automation container has PHP 8.4 and Chromium but cannot resolve/download the official theme, archival images, WordPress runtime or `@wp-playground/cli`. The existing network-fetching Blueprint cannot run here even after its HTML source is assembled. WordPress official Blueprint Bundles documentation (updated Oct 14, 2026) expressly supports ZIPs containing `blueprint.json`, bundled `installTheme.themeData` and `writeFile.data` resources, run through the free Playground CLI with `--blueprint=/local/path/bundle.zip`.

This new tool creates exactly that **private, self-contained resource bundle** from separately acquired and SHA-256-reviewed files. It converts **only four existing runtime URL resources** (Assembler plus Apollo, Franklin and NYPL) to `resource: bundled`; it does not touch content, scripts, archive findings or live WordPress. The original Blueprint remains untouched. The bundle is not licensed for public distribution and is never an accepted public homepage.

## Preconditions

- Exact 19-step integrated Blueprint generated from independently checked GitHub source at the approved HEAD, including PR #537's WordPress `wp_slash`/post-save custody and customized template precedence check. Record its SHA-256 *before* running the packager.
- Separately authenticated and locally downloaded official Assembler theme ZIP, with independently recorded SHA-256.
- Original first-party media files named `apollo.webp`, `franklin.jpg`, `nypl.jpg`, 78,346 / 466,043 / 5,553,669 bytes respectively, and independently reviewed `isolated-staging-media-review` manifest with original URLs and SHA-256 for each. This manifest does **not** substitute for image-specific reproduction rights.
- All source input files `chmod 600`; output directory created before execution with `chmod 700`. No subscriber exports, keys, production database, cookies or user records.

## Usage

```bash
python3 package_offline_playground_bundle.py \
  --blueprint /private/integrated-blueprint.json \
  --blueprint-sha256 <independently-reviewed-64hex> \
  --theme /private/assembler.zip \
  --theme-sha256 <independently-reviewed-64hex> \
  --media-dir /private/media \
  --media-manifest /private/media-attestation.json \
  --output /private/fv-integrated-offline-stage.zip
```

The generated ZIP has `blueprint.json`, `assets/assembler.zip`, `assets/apollo.webp`, `assets/franklin.jpg`, and `assets/nypl.jpg`. The source Blueprint is **never overwritten**, and the private ZIP is created mode 0600 with stable member metadata. The receipt explicitly states `OFFLINE_BUNDLE_SEALED_NOT_WORDPRESS_EXECUTED_RELEASE_HOLD`.

Run on an authorized developer machine with installed CLI: `wp-playground server --blueprint=/private/fv-integrated-offline-stage.zip --port=19400` (or your installed CLI's documented equivalent). Run exact-head browser QA with Chromium, axe, reduced-motion, keyboard/touch/no-JS, 320–1920px/200% zoom, Lighthouse and genuine image bytes. The previous `launch_integrated_staging.py` runner **only accepts URL-resource JSON Blueprints**, not this new ZIP; it cannot be pointed at the offline ZIP without an independently reviewed adapter update. Do not quietly mark that separate gate passed.

## Local verification / limits

Run `python3 -m unittest -v test_package_offline_playground_bundle.py`. The 12 tests use deliberately synthetic images/theme and validate ZIP layout, byte identity, deterministic output, no overwrite, restrictive permissions, source guarding and adversarial failures. No actual Assembler theme, original media or WordPress runtime is included in the tests. A successful bundle alone **does not** establish WCAG, original-image rights, host parity, real performance, homepage visual acceptance, CI/QD or release approval. WordPress.com's Personal plan still has no native staging clone; a free local Playground instance is not the WordPress.com Atomic environment.

Reference: https://developer.wordpress.org/playground/blueprints/bundles/ (WordPress Playground official documentation, Oct 14, 2026 revision).
