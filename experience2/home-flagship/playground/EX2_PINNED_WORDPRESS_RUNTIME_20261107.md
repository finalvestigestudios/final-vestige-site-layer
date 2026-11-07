# EX2 — Pinned WordPress integration runtime (2026-11-07)

**DRAFT / STAGING ONLY / RELEASE HOLD.** Stacked on PR #1422 exact parent `622fd681078c532cdc77b7048a7d0393422e50b5`. Frozen PR #49 `10495883299d53596992c26a8987f629b2904670` and production WordPress Page 6 are untouched.

## Reproduced source-level gap and remedy

Original [local runner](./run_local_wordpress_acceptance.py) invoked `@wp-playground/cli@latest` with floating WordPress/PHP versions. Identical source commits could generate different integration-test outputs following a new upstream release. This is an exact-source **reproducibility defect**, not proof that WordPress is currently running or that the DNS failure was caused by version drift.

The changed runner pins `@wp-playground/cli@3.1.55`, `--wp=7.1.4` and `--php=8.3`; source-controlled `playground_launch_command` rejects external host/port drift. Reviewed Assembler commit `75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f` and protected bundle SHA-256 `9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d` are unchanged. The selected WordPress release corresponds to a 2026-10-28 maintenance/security update; WP.com host parity remains unverified.

Authoritative references: [official Playground CLI](https://developer.wordpress.org/playground/developers/local-development/wp-playground-cli/), [official Blueprint ZIP bundles](https://developer.wordpress.org/playground/blueprints/bundles/), [WordPress release register](https://wordpress.org/documentation/article/wordpress-versions/), [npm Playground CLI release](https://www.npmjs.com/package/@wp-playground/cli).

## Local acceptance evidence

With the identical pinned ZIP and code, `FV_EX2_BUNDLE_PATH=/path/to/fv-ex2-local-cli-preflight-guarded.zip python -m unittest -v test_native_identity test_run_local_wordpress_acceptance test_runtime_source_pins` gave **30/30 PASS** on a local offline Python interpreter: 12 previous mock-host negatives, 8 prior runner checks and 10 new runtime/host tests. Source syntax also compiled. Original ZIP admission and protected PHP custody passed. This is a local test receipt, **not a completed WordPress launch**.

No real WordPress/Assembler pages, archival response bytes, independent axe WCAG 2.2 AA, Lighthouse/CWV, Jetpack subscriber confirmation, Payhip transaction or independently paid affiliate conversion were observed. The environment cannot retrieve npm/GitHub runtime dependencies. Release HOLD is mandatory.

## Editorial and conversion protection

The candidate stays seven chapters with 72 Margins fragments and five Focus destinations. Historical image references remain Apollo 1 (NASA WP media #473) and Franklin (1869 reproduction WP #474); rights-pending NYPL media #1258 stays excluded. Metadata are not transferred image bytes, and artwork is not copied from Blue Corridors. The 52-page Focus Fieldbook and Jetpack subscription remain untouched.

**OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER:** Free Fieldbook → homepage evidence to unobstructed Focus CTA → inaccurate lab acceptance possible from changing dependencies → pinned runtime for real local WordPress QA → **30 offline tests PASS; actual WordPress FAIL/BLOCKED** → Homepage QA, with independent Site QA/QD; Claude owns attribution/commerce and Grok/Praxxis owns social distribution. No verified new signup, order, refund, affiliate payout, or net revenue is asserted.

## Release admission still required

Run the exact pinned bundle on an authorized network-enabled **isolated local** WordPress Playground, verify actual CLI/WordPress/PHP/Assembler versions and render, 320–1920px real-browser image transfers and byte hashes, no-JS/touch/keyboard/zoom/reduced-motion, genuine independent axe, honest measured Lighthouse, source rights, CI/QD, founder art direction and explicit release approval. WordPress.com Personal has no native staging clone. No production CMS/merchant/email/social changes authorized.
