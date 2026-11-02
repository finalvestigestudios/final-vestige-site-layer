# Unified local Playground execution admission — 2026-10-31

**DRAFT / RELEASE HOLD.** This is a narrow security-and-correctness improvement to the existing unified **seven-chapter** isolated stage from PR #297 (exact parent `113d03a7e271f39f6a768d9df623b1fce9fa18d7`). Frozen PR #49, Apollo PR #158, WordPress production page ID 6, visuals and media are untouched.

## Three reproduced PR #297 false positives

In synthetic local Git/staging fixtures, the old `bind()` accepted all three of these unsafe inputs:

1. An extra `--host=0.0.0.0` CLI flag alongside the required arguments. We did not run a server or establish that Playground actually exposed a listener.
2. A modified Blueprint step with an additional unexpected PHP/network operation and a *matching recomputed companion receipt hash*. A mutable receipt hash cannot independently authorize executable staging instructions. No injected PHP was executed.
3. Replacing `mounts/` with a symlink to a directory outside the intended kit; the old binder then wrote its generated parity mount through that symlink **inside a temporary test directory**. No production or private files were touched.

## Implemented fail-closed boundaries

The binder now requires the exact parent-builder Blueprint structure and canonical local-only PHP preview seed, unchanged local environment configuration, editor-only preview path, and precisely the expected CLI flags and mounts. It rejects extra CLI flags, added Blueprint actions, modified seed PHP, outbound site URL overrides, duplicate Blueprint overrides, stage-root/mount-root symlinks and symlinked theme/plugin entry points.

The original twelve regression tests remain; **nine adversarial cases were added**. The tests operate only on synthetic temporary Git repositories and source files, not on a running WordPress installation.

## Verified results and source custody

- **21/21 Python unit tests passed**, plus Python compilation and PHP syntax verification.
- Original PR #297 GitHub blobs matched the tested pre-change ZIP: binder `d6b9572da42770e5df6b7b01e5f26c73946771fe`, tests `83a7adb869aa04547c0b619b8a61964cad8a881c`.
- Updated committed Git blobs matched locally tested files: binder `43744e0845d10b035e28c90a0954867756c6af62`, tests `c977a6845508389061610f3521cf8a4aeae0c425`.
- A **real system Chromium/Playwright localhost HTTP probe** was attempted. The browser launched, but navigation returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`. This is a **sandbox restriction**, not a WordPress staging result.
- **No WordPress installation, source-rendered seven-chapter screenshot, axe, Lighthouse, real archival-image transfer, hosted CI, independent QD or production modification is claimed.**

## Continued release gate

Official Assembler 0.0.126 ZIP origin and SHA pin, actual WordPress Playground execution on an authorized firewall-restricted local environment, exact-head homepage/browser/keyboard/no-JS tests, first-party photo payloads and rights, visual review, lab Lighthouse and independent QD/CI still block release. The CLI's default network bind behavior was **not independently verified**; accepting only expected args does not replace an OS firewall or runtime listener check. WordPress Playground does **not** certify WordPress.com/Jetpack behavior or field CWV. Preserve all seven chapters, three art directions, Focus Fieldbook, Jetpack and 72 Margins records. **HOLD; no merges or deployments.**
