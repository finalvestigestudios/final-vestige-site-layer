# Experience 2.0 — archival media identity gate: executed regression

**Status: DRAFT / RELEASE HOLD.** This is an isolated QA/security correction stacked directly on PR #388 exact parent `6dc99ac90f35b89c5e0c74c21f0f7374fe9be2f5`. PR #49, published WordPress, other agent lanes and historic narrative content are untouched.

## Reproduced defect (before)
The proposed WordPress Playground adapter accepted imported archival images on *file size and dimensions only*, with no cryptographic identity or MIME check. Using the generated PHP from PR #388 and controlled **synthetic GIF headers** (not historical images), padded to exactly the three expected byte counts, `fv_ex2_safe_stage()=true`, `fv_ex2_integrity()=true`, `fv_ex2_ready()=true`. Thus a replaced file named `apollo.webp` containing GIF bytes could be misrepresented as an authenticated source original. This is a release-admission integrity defect, not evidence of malicious live content.

## Correction
The adapter now requires, for **each of the three** local images, exact filename, bytes, dimensions, MIME **and constant-time SHA-256 equality** against independently supplied, source-specific fingerprints. The Blueprint generator accepts `--trusted-media-manifest /private/media-fingerprints.json`, validates exactly three records, all canonical original URLs, byte counts, digest hex syntax and no unreviewed extra keys. It embeds the reviewed hashes in its PHP renderer. If no manifest is provided, Blueprint source generation remains possible for structural inspection but its plugin **refuses to render the homepage** with `CLOSED_MISSING_MEDIA_FINGERPRINTS`. No default, guessed or fake digest is ever trusted.

The helper `make_media_fingerprint_manifest.py` computes local byte witnesses for **independently checked originals**, enforcing the three WordPress media records' exact sizes, dimensions, MIME types, and URLs. **This does not independently authenticate a downloaded image or settle its copyright/reproduction rights.** Human source verification remains a separate release gate. Synthetic test hashes must never be used in a real stage.

## Reproduction / gates
Run from an **exact new branch checkout**, with Node 22+, Python 3 and PHP 8+ available:

```sh
node --test experience2/home-flagship/qa/playground/test_media_identity_gate.cjs
node --test experience2/home-flagship/qa/playground/test_playground_blueprint.cjs
python experience2/home-flagship/qa/playground/make_media_fingerprint_manifest.py \
    --media-dir /private/verified-public-archival-originals \
    --output /private/archival-media-sha256-reviewed.json
node experience2/home-flagship/qa/playground/make_playground_blueprint.cjs \
    --output /private/NEW-ex2-staging-blueprint.json \
    --trusted-media-manifest /private/archival-media-sha256-reviewed.json
```

Never upload source photographs, media manifests or a Playground ZIP to the public WordPress site. The media files must be obtained separately as public source assets and manually checked for origin/rights.

## Executed evidence — 2026-10-31
- **PR #388 generated PHP before fix:** independent PHP 8.4 CLI with faked WordPress guards returned `{stage:true,integrity:true,ready:true,mime:"image/gif"}` for three padded synthetic GIF records with correct byte counts and dimensions.
- **Corrected PHP test program:** `node --test test_media_identity_gate.cjs`, **6/6 PASS** in local PHP 8.4 and Node 22: approved synthetic fixture, byte mutation with unchanged MIME/size/geometry, GIF substitution, missing manifest, missing file, production host / absent authorization.
- **Manifest generator:** `python -m py_compile` PASS; accepted controlled JPEG/WebP metadata+size fixtures and refused overwriting the existing manifest. These are synthetic fixtures only, not archival transfers.
- **Exact committed Blueprint generator:** fetched by GitHub blob, parsed in V8 and run against an isolated virtual filesystem: **19 steps** in both configurations, unreviewed-media mode produces PHP `array()` and explicit CLOSED receipt, validated three-record fixture manifest embeds PHP array/digests, invalid bytes in a record are rejected. This execution is source-transform verification, **not WordPress Playground runtime**.
- PHP lint of a locally reconstructed equivalent renderer: PASS. All source SHA/commit references are in the associated PR.

## Still unverified — all stay HOLD
Actual authenticated private WordPress/Assembler render (WordPress.com Personal has no native clone); public media HTTP transfer/hash comparison against independently obtained originals; exact NASA/Commons image identity, Franklin reproduction and RMG versus Wikimedia rights, record-specific NYPL rights; native page/Jetpack retention; real 7-width Playwright/axe WCAG 2.2 AA, Safari/touch/zoom, Lighthouse/CWV, GitHub CI, QD and founder art-direction approval.

The original media evidence map is Apollo WP 473 (78,346 B, 1041×810), Franklin WP 474 (466,043 B, 960×1526), NYPL WP 1258 (5,553,669 B, 5667×3831). These metadata alone are **not** reproduction-rights or byte-identical proof. Coordinate rights custody PR #329, private seal PR #224, homepage PR #382 and Apollo R&D PR #158. No direct Inspire3 offer or new subscription.
