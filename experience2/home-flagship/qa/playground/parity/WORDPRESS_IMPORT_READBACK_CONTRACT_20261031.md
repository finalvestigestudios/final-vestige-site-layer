# Experience 2.0 — WordPress local importer: preflight and readback QA

**2026-10-31 · DRAFT / RELEASE HOLD · No production CMS writes**

Scope: The *existing* seven-chapter flagship staging importer in `apply_local_parity.php`; stacked on #310 (`f443e9d8f0fc86534bcbf253a79105cd0674b52a`). Does not alter homepage assets, art directions, Franklin folio, frozen #49, or Apollo #158.

## Reproducible pre-existing defects

Used the **unaltered PHP source from #310** with only the test bootstrap/manifest absolute paths redirected to disposable PHP WordPress API stubs. These are implementation contract tests, **not a real WordPress installation**.

| Adversarial local-only fixture | BEFORE — original #310 importer | AFTER — this branch |
| --- | --- | --- |
| Header is an existing non-FV local override | Rejected *after* creating a separate page override (1 partial write) | Rejects during full five-record preflight (**0 writes**) |
| Two FV-tagged header overrides (ambiguous winner) | Returns success after 5 insert/update attempts; duplicate still exists | Rejects duplicate before first write (**0 writes**) |
| `wp_insert_post()` returns ID but saved template content differs | False positive: reports success after 5 writes | Refuses after actual `get_post()` readback (**1 write attempted**) |
| Theme taxonomy association dropped despite successful insertion return | False positive: reports success after 5 writes | Refuses after `wp_get_object_terms()` verification (**1 write attempted**) |

These failures were reproduced with **synthetic WordPress API behavior**, not evidence of problems on production.

## Implementation

- Preflight **all five fixed records** (page, header, footer, overlay, global styles) before the first write; reject both unowned and duplicate existing records.
- Require source-owned existing objects for idempotent updates; no arbitrary page, subscriber or analytics import.
- Read stored content/type/slug/status/ownership back through `get_post()`/`get_post_meta()`, and verify Assembler `wp_theme` and template-part area term assignments.
- Preserve the local-only hostname, WordPress environment, Assembler 0.0.126, tracker exclusion and CSS safeguards.
- No new plugin, SaaS, chapter, remote script or asset.

**Important boundary:** A failed *post-write* readback may still leave a partial local-only import. This is an honest HOLD requiring that the disposable Playground environment be discarded and rebuilt, **not a transaction or production-safe rollback**.

## Reproduction / results

```bash
cd experience2/home-flagship/qa/playground/parity
php -l apply_local_parity.php
python -m unittest test_wp_runtime_contract.py -v
python -m unittest discover -p 'test_*.py' -v
```

On local PHP 8.4.24 / Python 3.13: **11/11 importer-contract tests PASS**, **42/42 total parity tests PASS**, PHP lint PASS, Python compilation PASS. The committed PHP blob is `4f6d8fa5b598733fad12bdcb5d3085c49fb0c2ef` and committed test blob is `1929465933f5646069bd20a0c1ba6b42485dfc7d`; these match the bytes executed locally.

## Release gate still CLOSED

These tests prove only the WordPress-facing code's behavior under deterministic fakes. No real WordPress database, Assembler runtime, first-screen visual preview, seven-width actual Chromium/axe, real archival HTTP transfers, Lighthouse/p75 CWV, image reproduction rights, hosted CI or independent QD has been accepted. The isolated WordPress Playground route remains the $0 target because WordPress.com Personal has **no separate native staging clone**. Playground is **not** equivalent to WordPress.com Atomic hosting; Jetpack, redirects, host-specific cookies and field CWV need later hosted acceptance.

Founder visual signoff on one of three art directions remains open. Do not install, activate, merge, deploy, publish, or touch WordPress.com production without explicit release approval.

**Production read-only conservation check on 2026-10-31:** WP page 6 remains published with 72 indexed Margins fragments (0–71), two links to `/focus/`, and the `jetpack/subscriptions` block. No updates issued.
