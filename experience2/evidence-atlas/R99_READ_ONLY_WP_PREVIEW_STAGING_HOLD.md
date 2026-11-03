# Apollo Experience 2.0 R99 — read-only, private preview bridge (STAGING HOLD)

## Scope and source of truth
Issue #150; original Research Desk PR #158; prior Apollo R98 PR #828 at exact parent `916fbbc107e31bda3c12f1e0ac976a51402d9b12`. New files are wholly inside `experience2/evidence-atlas/{tools,integration,tests}`, this document and an independent CI workflow. No homepage branches/PR #49, no production/hosted WordPress, no WordPress content or settings writes, no activation/deployment, no paid service.

**Problem solved:** R98 exports seven independent HTML documents with relative CSS/JS and source-navigation links. Those links break when a full document is embedded within a WordPress page URL. R99 creates a strictly reviewed, WordPress-readable **private review adapter** while preserving the original seven standalone documents, their six NASA source identities, rights warnings and no-JS meaning.

## Actual implementation
- `tools/build_wp_private_preview_r99.py` validates the 31-file R98 input against its exact, pinned receipt SHA-256 `7cd85cbf273ebf406cb7e156c01a32b0558e3506a9c219a9b9c8f2099f4fe530` and all 30 file hashes. Rejects extra/missing/symlinked/drifted assets and a changed release/rights/geo flag; no arbitrary files.
- Converts only approved relative HTML/CSS/JS/source-export references into WordPress query-based private preview URLs (`?fv_apollo_r99=<approved file>#record-id`). NASA URLs and in-document fragments are preserved. No image files, photo embedding, map markers, invented relationships, remote fonts, AJAX, or new external requests.
- `integration/r99-private-preview-template.php` compiles a complete static SHA-256 asset whitelist into the PHP adapter. Private gate is **off by default** and requires both `FV_APOLLO_R99_PRIVATE_PREVIEW === true` and `current_user_can('edit_posts')`; otherwise returns 404 or published-investigation fallback. Serves only matching on-disk bytes with no-cache, nosniff, noindex, strict HTML CSP and no database writes or settings mutations. Local shortcodes: `[fv_apollo_r99_review]` (for future explicitly authorized private staging only).
- The preview shows the integrated hub inside a bounded iframe, plus a native full-page link. Its iframe sizing and WordPress/Assembler behavior are **not production accepted**. This is a review transport, not a replacement public-page integration.
- Emits deterministic, normalized-timestamp ZIP and `R99_PRIVATE_PREVIEW_RECEIPT.json` with package hashes and explicit release hold.

## Verified locally / evidence boundary
On the previously archived R98 exact-head source:
- 12/12 adversarial Python source-custody, source-reference, deterministic-ZIP, PHP template and security tests **passed locally**.
- Generated PHP `php -l`: passed; ZIP integrity: passed; twice-built deterministic archive is tested.
- Genuine local PHP HTTP shim checks: unauthenticated source 404; authenticated gallery 200; traversal attempt 404. This is **a WordPress-hook contract fixture**, NOT an installed WordPress runtime or hosted WordPress.com.
- Local Chrome/Chromium navigation is administratively blocked; **do not claim local HTTP Playwright/axe/LCP/CLS success**. New exact-head GitHub CI contains genuine HTTP Chromium matrix (7 views × 5 widths × JS/no-JS = 70 cases), keyboard and touch, full-document axe scans, lab performance receipts, responsive screenshots and a native PDF. Its results are pending until the runner executes successfully.
- The inherited WordPress/Assembler suite tests earlier Apollo components, not this R99 adapter. Actual WordPress/Assembler authoring, native theme constraints and hosted WordPress.com/Jetpack parity remain open. **No WordPress content/settings write was performed in R99.**

## Fail-closed release restrictions
Do not merge/activate/publish/deploy; do not alter hosted WordPress content, theme, plugins or settings. Six NASA photo-specific reuse reviews remain incomplete; the `S67-19766` catalog association is provisional. Complete independent editorial/QD review, actual authorized isolated WordPress/Assembler front-end acceptance, manual NVDA/VoiceOver/physical touch, hosted CWV, and founder approval before promotion. This staging preview does not certify WCAG 2.2 AA or commercial photographic rights.

## Isolation / coordination
Stacked on R98 only. Homepage PR #49 and lead branches remain untouched; PR #158 remains the original Research Desk reference and unmodified. Issue #150 is the coordination ledger for the team.
