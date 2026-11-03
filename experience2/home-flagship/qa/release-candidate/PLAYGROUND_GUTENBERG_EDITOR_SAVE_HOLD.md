# EX2 / Page 6 — real Gutenberg browser-editor Save gate (HOLD)

2026-11-03 · DRAFT / SYNTHETIC-ONLY / NO PRODUCTION WRITES OR RELEASE.
Exact parent is draft PR #802 commit 64e5e0c88928d6ad7b2684f0ec5e2526fc65dd08 (on #801, #793). This is a companion gate to the existing rights-safe NYPL fallback and accessible 72-Margins CSS; not another chapter or visual design.

## Substantive new acceptance test

PR #801/802 validates disposable WordPress CORE insertion and raw readback, but does not run the Gutenberg browser editor. A core insert can succeed even when Gutenberg modifies, sanitizes or refuses to save complex Custom HTML blocks. This gate starts official WordPress Playground CLI (WP 6.8/PHP 8.3), opens real Chromium, invokes Gutenberg editor's documented core/editor editPost + savePost action and verifies persisted post content via WordPress core.

Only the SYNTHETIC DRAFT TITLE is changed. The stored content must remain byte/SHA-256 identical. Require didPostSaveRequestSucceed, no save failure, preserved draft status, 72 Margins, the native Jetpack subscription comment, Focus Fieldbook, chapter navigation and the contrast marker. Any changed stored content, failure to save, lost block or published state fails closed.

## Safety and reproducibility

- No production page source, accounts, subscribers, secrets, real media, affiliate URLs or production WordPress API calls. Input is generated solely from the upstream synthetic fixture builder in #801.
- PHP checks HTTP request host AND installed WordPress home host are loopback, requires POST, exact synthetic marker and an ephemeral 256-bit token; only create/login/verify/cleanup actions are allowed.
- The browser authenticates only against an ephemeral local Playground administrator. Do not print credentials, cookies, token, nonce or Gutenberg HTML.
- The Node runner attempts deletion in finally after every post-create path and refuses success if deletion cannot be verified. Playground is disposed afterward. The existing PR #802 cleanup gate remains independently required.
- Native PHP adversarial tests exercise legitimate roundtrip+cleanup, no editor-save, changed stored content, wrong token, missing marker, nonlocal host or home URL, GET, duplicate draft, missing source, missing Margin, non-synthetic deletion and failed cleanup. Mock tests do not constitute a real WordPress test.
- A Node dependency-free --self-test and isolated, read-only GitHub Actions workflow are committed. The workflow pins @wp-playground/cli@3.1.56 and playwright@1.56.1, and runs exact-source PHP and Node checks before attempting real editor Save.

## Honest evidence status

SOURCE-CONTROLLED TEST CREATED; REAL EDITOR SAVE NOT YET PASSED. CI on parent PR #802 failed before any test steps. Local runtime has PHP/Node/Chromium but cannot resolve the npm registry or install WordPress Playground, so actual editor execution here was unavailable. Do not claim WordPress persistence, Assembler parity, Gutenberg editor Save, or CI green until completed exact-HEAD receipts exist.

Production page ID 6 read-only confirmed on 2026-11-03: published, last modified 2026-11-02T17:48:13, 72 Margins records, Focus Fieldbook/Jetpack, and NYPL reproduction still referenced. No site content was changed. WordPress.com Personal has NO official staging clone; its included wpcomstaging domain is not a second site. No subscription upgrade should be pursued without separate economic approval.

## Reproduction and strict PASS contract

In a clean network-enabled developer checkout of this PR exact HEAD, run .github/workflows/ex2-gutenberg-editor-save-HOLD.yml. It generates a synthetic source file in runner temporary storage, boots local Playground, performs a Gutenberg data-store Save in Chromium, proves stored SHA/content and deletion, and removes temporary files. PASS demands REAL_GUTENBERG_EDITOR_SAVE_SYNTHETIC_PLAYGROUND_ONLY, matching source/stored SHA, nine true checks, draft_removed true and release HOLD. Synthetic PASS is NOT exact live Gutenberg export or WordPress.com host acceptance.

## Remaining RELEASE HOLD gates

Real source-controlled seven-chapter candidate on isolated Assembler WordPress; actual Gutenberg render and founder visual review; 320/360/390/768/1440/1920 and 200% zoom; image response-body MIME/size/rights (NYPL image 5003296 not cleared); genuine manual WCAG 2.2 AA, axe, keyboard/touch, no-JS/reduced motion; lab Lighthouse and p75 field CWV; real Jetpack signup and host-specific CSP; independent exact-SHA QD and explicit founder release authorization.

Frozen PR #49, Apollo #158, Mind #171, theme/navigation, live page and users/subscribers untouched. No merge/deploy/publish.
