# FV Experience 2.0 • Sealed WordPress Playground ZIP admission — 2026-11-01

**DRAFT / RELEASE HOLD.** Stacked on PR #459 at 87e3cd34b6b95219a7bb4d6dc72ec6025e5c3e46. Frozen PR #49 and production page ID 6 remain unchanged.

## The integration defect this fixes

PR #459 builds an official offline WordPress Playground Blueprint ZIP. The earlier launch_integrated_staging.py only accepted the unbundled JSON version. Using ZIP mode without validating the four bundled substitutions would bypass the original source, media and safety gate. WordPress officially supports local ZIP bundles via its CLI blueprint argument: https://developer.wordpress.org/playground/blueprints/bundles/

The companion launch_offline_bundle_stage.py verifies BOTH the original independently SHA-256-pinned 19-step integrated Gutenberg JSON and the bundled ZIP. It applies only the four already-reviewed URL-to-bundled transformations (Assembler theme plus Apollo, Franklin and NYPL media), serializes canonically, and requires byte-for-byte equality to the sealed archive Blueprint. It checks the approved theme ZIP structure and SHA-256, the three image bytes/metadata/source URLs against a separately SHA-pinned manifest, inventory/duplicate paths, symlinks, ZIP CRC and private directory/file permissions. No original image, confidential data, credentials or bundle is committed to the repository.

The original 19-step Blueprint check retains the local-only environment guard, exact allowed WordPress/plugin paths, integrated preservation conditions (72 Margins, native Jetpack block, Focus Fieldbook), seven chapters and image provenance handling. On --execute the new adapter passes the validated ZIP file directly to the EXISTING launcher, which handles loopback-only Playground, real HTTP readiness, Chromium/image-byte/axe interaction checks, mobile/desktop Lighthouse and immutable receipts. The original launcher is not modified.

## Reproduce

Place independently approved original JSON, complete offline ZIP, media manifest, official Assembler theme fingerprint, original image hashes, pinned axe-core and browser/CLI binaries in a pre-existing private staging directory. Use chmod 700 on directory and chmod 600 on the protected source files.

Preflight (no WordPress execution):

    python3 experience2/home-flagship/qa/playground/launch_offline_bundle_stage.py --private-dir /private/fv-stage --output-dir /private/fv-stage/reports --bundle /private/fv-stage/review.zip --bundle-sha256 "$BUNDLE_SHA" --original-blueprint /private/fv-stage/integrated-original.json --original-blueprint-sha256 "$SOURCE_SHA" --media-manifest /private/fv-stage/reviewed-media.json --media-manifest-sha256 "$MANIFEST_SHA" --assembler-sha256 "$ASSEMBLER_SHA"

For full isolated WordPress execution, add --execute with independently fingerprint-pinned --axe-js, --axe-sha256, --browser-runner, --browser-runner-sha256, --playground-cli, --playground-cli-sha256, --lighthouse-cli, --lighthouse-cli-sha256. Never insert production credentials, subscriber database or site tokens. No production/CMS API write operation exists here.

Run synthetic unit regressions:

    python3 -m unittest -q test_launch_integrated_staging test_offline_bundle test_launch_offline_bundle_stage

Source-only tests use controlled fake JPEG/WebP data. They DO NOT establish historical image authenticity or production permission. One test re-pins the modified malicious ZIP, then verifies the independent original image/source guard still rejects it. Another verifies execution hands off the exact admitted ZIP path to the unchanged launcher.

## Honest admission status

The local test run on these sources passed 52/52 unique regression tests (24 inherited launcher, 11 ZIP builder, 17 new sealed-ZIP acceptance). New code is reviewed for local harness behavior, NOT actually WordPress-executed.

Required before release: authentic approved image bytes and specific reproduction rights, independently approved official Assembler theme ZIP, a real sealed ZIP from those originals, installed native WordPress Playground with exact integrated Gutenberg, genuine first-party image network receipts, axe and manual WCAG 2.2 AA, 320–1920 responsive screenshots and 200% zoom, reduced motion/no-JS/touch/keyboard, lab Lighthouse and real field CWV separately, hosted WordPress.com/Jetpack functional acceptance, founder art-direction review and independent exact-SHA QD/CI. Do not claim hosted Atomic equivalence. Personal-plan native staging is not offered, and no Business upgrade is recommended.

## Nonoverlap and handoff

This PR only adds a sealed-bundle launch adapter, adversarial suite and this note under experience2/home-flagship/qa/playground. It makes no artistic/chapter/affiliate changes; Apollo 1 Atlas PR #461 and Mind & Perception #171 are separate. Release remains HOLD.