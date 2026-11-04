# EX2 isolated Assembler header trust preflight — HOLD (2026-11-03)

## Parent, scope and custody

Stacked on draft PR #869 at exact source SHA `beb6c530e15a5e1fa2cc900b6cf20ca7b9d549ef`. This is a safety gate for **disposable loopback WordPress Playground only**. No live CMS/theme/navigation change is authorized by this code. PR #49 is frozen; #158 (Apollo), #171 (Mind) and the existing seven-chapter design remain separate.

The actual hosted Assembler run [41746252144](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41746252144) reproduced a serious complete-document desktop axe navigation `list` failure, then fatally stopped on the nonexistent `wp_clean_post_cache()` call. Parent PR #869 replaces it with WordPress core `clean_post_cache()`. That correction has **not yet been qualified in the exact real browser**, because the latest GitHub Actions run [41750735760](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41750735760) failed before job steps.

## This branch closes an independent safety gap

Previously, the native-navigation fixture checked that its resolved header belonged to the stock Assembler theme **only in the pattern-fallback branch**. If the resolved template happened to contain exactly one `core/navigation` block, the fixture could skip the vendor digests and trust a site-customized template part. That path ultimately inserts a synthetic `wp_navigation` and `wp_template_part` record.

Now both direct-native and registered-pattern paths require the same **pre-write** checks:

1. `get_block_template('assembler//header','wp_template_part')` returns source `theme`, theme `assembler`, slug `header`. A customized database `wp_template_part` does not qualify.
2. Both resolved filesystem paths stay under the active theme; both vendor file digests match the exact previously reviewed Assembler archive: `parts/header.html` SHA-256 `3b983fa0d9d6ce9b2bc1024e215d9d63d9ecba2ad11f881ec59e87a40c28c2aa`, `patterns/header.php` SHA-256 `962d31e7fe0dccc0f3398367b28744d54683743922b79209eeaae71b9731a480`.
3. The resolved template part content **also hashes to the pinned theme header**. A filtered or otherwise altered "theme" part does not qualify.
4. All checks occur before either `wp_insert_post()` call. Unknown vendor/theme bytes **fail closed**; there is no blind fallback or new production adaptation.

Official WordPress source confirms `get_block_template()` returns unified theme/database templates and that file-backed templates are labelled `source='theme'`, while database template parts can override the theme file. See [WordPress get_block_template](https://developer.wordpress.org/reference/functions/get_block_template/) and [Template Parts Handbook](https://developer.wordpress.org/themes/templates/template-parts/).

## Verification/qualification

Source-level deterministic checks in the authoring script passed for the new unconditional digest guard, single vendor verification block, unchanged WordPress cache API, and inclusion of the two extra adversarial test contracts. **These are NOT runtime test results.** The new test cases assert all origin and digest guards precede WordPress writes, and that no digest checks are hidden inside the pattern fallback.

**Still required**: exact-head Node/PHP execution (including `php -l`), actual isolated WordPress/Assembler native header save/render, complete-document axe at 320/390/768/1440/1920, keyboard/no-JS/200% zoom/reduced-motion, first-party image-body bytes and licensing review, honest Lighthouse lab metrics, independent QD and founder visual/release decision. GitHub runner failures before tests are infrastructure *blockers*, not test passes.

The isolated WordPress test is **not** an exact WordPress.com Personal-plan hosted clone. No production data, subscriber list, credentials, Jetpack configuration, live WordPress settings, or private media are to be imported.

## Release decision

**HOLD.** No merge, deploy, public WordPress writes, plugin installation, art-direction retirement, paid subscription, or claim of WCAG 2.2 AA is permitted here.
