# R413 — Local-first source import file custody (DRAFT; issue #73)

**Release hold:** This is **source-only** offline validation for LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro. It is **not** Windows x64 binary validation, a compliance determination, an entitlement grant or permission to release. QD review and founder approval remain required.

## Reproduced failure on exact R412 source

R412 SHA-256 inventory measured `fvs_suite/**/*.py`, only six explicitly named launcher files, and the offline runner. Its directory scan rejected linked directories and compiled modules but did **not** reject non-Python file symlinks, FIFOs, Windows file reparse points or hardlinks; a linked `policy.json` could point outside the trusted checkout. An ordinary JSON/CSV asset or newly added Python file in `launchers/` could change without altering the source digest.

Tested the 14 R413 regression methods against the exact original R412 runner blob `8c30aa8192114fc4a7a66fec8b662423ef79dc20`: **12 tests failed**, as expected, before any patch. The two existing-compatible positive cases passed.

## Patch

- Check **every file** found under both import roots with `lstat`, refusing symlinks, nonregular files, Windows file reparse points and files with multiple hardlinks. These tests run before any source child process.
- Include **all regular files** under `fvs_suite/` and `launchers/` in the deterministic SHA-256 inventory (including local JSON/CSV assets and additional Python modules). Retain the exact six required launcher checks.
- Apply the existing per-file size cap (2,000,000 bytes) and per-child pre/post inventory checks to the expanded inventory; mid-run asset changes halt further child execution.
- Preserve `-I -B` Python isolation, minimal child environment, `DEVNULL` stdout/stderr, `release_authorized=false`, all six fixed launchers and standard/optimized source-only receipt semantics.

Source changes are limited to `products/desktop/offline_source_smoke_r408.py`. No changes to financial calculations, input files, compliance review, cryptographic entitlement validation, WordPress, or production.

## Local measurement (Linux, Python 3.13.5)

- 14 new synthetic regression methods **PASS** with `python -W error -m unittest -v test_import_file_custody_r413.py`.
- Same 14 methods **PASS** with `python -OO -W error -m unittest -v test_import_file_custody_r413.py`: **28/28 method executions**.
- Both runs included genuine subprocess execution of **12 synthetic launcher smokes** each in the positive case, not six actual financial engines.
- `python -m py_compile` on exact Git-matched modified gate and test files **PASS**.
- Gate Git blob: `52e9ec8a0de6437d7fc76deab4d36ae5ba49b7ff`; test Git blob: `3338152f4686290e985996caa17c870710b48233`.
- The R412 original was reproduced locally with matching Git blob SHA before patching. Tests are synthetic reconstruction; **the full trusted repository was not available locally**, and the Windows workflow has not executed.

## Invariants and blockers

- Nothing can confer a software release: the receipt continues to say `SOURCE_ONLY_NOT_WINDOWS_BINARY` with `release_authorized=false`.
- No customer uploads, telemetry or network calls were introduced. Any rejected path details remain private.
- A full checkout may contain legitimate linked assets or larger templates, which this fail-closed policy will reject. Validate the complete real source tree before treating a green synthetic test as integration evidence.
- Exact-commit hosted CI previously failed before runner allocation (R412 source run #43523805987 and Windows build #43523805981, four jobs with no steps). Root cause not independently established.

**Next high-impact step:** restore hosted GitHub Actions runner execution or run the full repository on trusted Windows and Ubuntu machines. Execute inherited R408–R413 and financial/crypto/entitlement gates, then build and verify Windows x64 binaries, scan with Defender, perform keyboard/NVDA acceptance and verify premium distribution access controls. Independent QD review and explicit founder approval are required before any public changes.
