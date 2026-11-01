# Experience 2.0 — private WordPress/Assembler complete-home staging orchestration

**DRAFT / RELEASE HOLD.** Child of PR #438 at exact 3c584484063dca6bbf7c7881475521c0319be2e6. No edits to frozen PR #49, production page 6, theme, navigation, plugins, Apollo #158, Mind #171, Jetpack signup or 72 Margins.

## Scope and new capability

The existing isolated source components cover selective Gutenberg hero replacement (#408), a private integrated 19-step Playground Blueprint (#414), complete-home browser/axe gate (#420), lazy photo navigation (#426), and browser-consumed original HTTP image identity (#438). The new launcher brings these into a single, reproducible **actual local WordPress/Assembler execution path**. No new chapter, visual treatment, subscription or WordPress.com upgrade.

Files:
- launch_integrated_staging.py: guarded offline preflight plus optional executable local stage. Rejects old seven-chapter-only Blueprint, unapproved SHA, a missing 72-Margins/Jetpack Gutenberg integration, wrong Assembler source, production environments, unreviewed plugin/media paths, image CDN substitutions, unsafe file permissions, missing independent archive SHA manifest and missing axe-core SHA. With --execute, starts an installed @wp-playground/cli on loopback, runs #438's exact Chromium/axe harness, records screens/receipts, runs mobile and desktop Lighthouse lab audits, then kills temporary stage. No production WordPress API calls.
- test_launch_integrated_staging.py: 15 Python unittest cases, all passed on byte-for-byte GitHub committed code. An older actual PR #388 19-step standalone Blueprint was independently rejected for lacking the integrated protected Gutenberg content.
- ARCHIVAL_SOURCE_RIGHTS_REVIEW_20261101.md: source-grounded NASA, Franklin/RMG and NYPL provenance/rights gaps. No image download or rights certification.

## Setup on a developer workstation

1. Check out exact PR #438 head or a separately reviewed stack. Read public page 6 only and generate a privately stored complete Gutenberg Blueprint with existing make_integrated_playground_bridge.cjs (PR #414) and independently reviewed page/media hashes. Never import WordPress database, subscribers, credentials, users, private metadata or site settings. The generated Blueprint contains public page content and stays outside Git, mode 0600, in a 0700 private folder.
2. Independently obtain the three original media files, verify their exact HTTP bytes and rights, and construct the expected isolated-staging-media-review original identity manifest. WordPress Media API metadata alone is not a fingerprint.
3. Install the free official @wp-playground/cli and Lighthouse locally; obtain verified local axe-core JS and its independently approved SHA-256. Use Node >=20.18. Official current CLI docs: https://developer.wordpress.org/playground/handbook/guides/programmatic-playground-cli/ .
4. From the reviewed source checkout, run Python launch_integrated_staging.py with arguments --private-dir /private/fv-stage --blueprint /private/fv-stage/integrated.blueprint.json --blueprint-sha256 <APPROVED_HASH> --media-manifest /private/fv-stage/reviewed-media.json --axe-js /private/fv-stage/axe.min.js --axe-sha256 <APPROVED_AXE_HASH> --browser-runner experience2/home-flagship/qa/playground/verify_playground_browser.py --output-dir /private/fv-stage/results .
5. Preflight success means PRIVATE_BLUEPRINT_PREFLIGHT_PASSED_NOT_WORDPRESS_EXECUTED. To execute actual WordPress rendering and lab evidence, add --execute --playground-cli /absolute/path/to/wp-playground --lighthouse-cli /absolute/path/to/lighthouse . The temporary CLI server listens at 127.0.0.1:19400; only loopback is admitted. Inspect resulting private screenshots, source image HTTP SHA receipts, axe and Lighthouse mobile/desktop JSON. Final success label remains ISOLATED_WORDPRESS_LAB_EVIDENCE_COLLECTED_RELEASE_HOLD.

## Executed vs blocked

On 2026-11-01, 15/15 executable regression tests PASS on exact committed source. New launcher Git blob d2ffcef5b62393e7aa2322f5b79ea13f8aba3748, tests daf3f752e191ba391aef3ca2e4e40b6dd448abff. Actual legacy PR #388 standalone Blueprint was correctly refused. Independent official CLI documentation confirms local server + Blueprint support.

**Actual WordPress/Assembler stage NOT EXECUTED:** this runtime cannot resolve network DNS for official theme/media and lacks downloaded WordPress/Playground CLI. Chromium localhost is policy-blocked (net::ERR_BLOCKED_BY_ADMINISTRATOR), although the Python HTTP client connects. No axe/Lighthouse/real media or Jetpack certification claimed. Private Playground is not production WordPress.com Atomic and cannot certify hosted redirects, Jetpack, cookies or field CWV; independent QD/CI, item-specific rights and founder selection/release approval still required. No production writes, merges, deployments, releases or additional subscriptions occurred.

**Release: HOLD.**