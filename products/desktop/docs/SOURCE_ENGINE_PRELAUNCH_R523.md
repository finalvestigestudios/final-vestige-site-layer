# Final Vestige Labs R523 — prelaunch engine custody and import-surface guard

**Status: DRAFT / QD HARD HOLD — NOT a release, acceptance or Windows-binary certificate.**
Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
This change is stacked solely on [R522 draft PR #3002](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3002), not production `main`.

## Reproduced R522 gaps

1. **Between-check engine substitution:** R522 hashes all shared `fvs_suite` engine modules before its test matrix, but checks them only after the **last** child exits. Child #1 could rewrite `engine.py`, child #2 could run against that substituted code and restore the original file, and the matrix would print PASS. The isolated two-command negative control reproduced this false PASS against the exact R522 runner module.
2. **Unreviewed import surface:** R522 inventories only `*.py` files directly inside `fvs_suite`. Adding a nested package (`forged/__init__.py`), sourceless `.pyc`, native `.pyd` or `.so` file could evade that inventory. Eight of the eleven new import-surface test cases failed against the exact R522 helper, including both postflight detection cases.

## R523 implementation

- `scripts/source_evidence_runner_r509.py` checks the **complete original engine snapshot before each** of 416 source commands, in addition to retaining R522's final engine postflight. Any non-true result or unexpected scanner exception fails closed with a fixed, redacted message **before spawning the next child**. This guards the observation boundaries, not filesystem writes occurring entirely inside one subprocess.
- `scripts/source_engine_custody_r522.py` refuses new subdirectories/packages, linked directories, linked data leaves and unreviewed executable/bytecode/native-extension suffixes (`.pyc`, `.pyo`, `.pyd`, `.so`, `.dll`, `.dylib`, `.pyw`) alongside the existing strict top-level `*.py` SHA-256 descriptors. A **regular, unlinked** `__pycache__` directory is allowed for normal CPython use; its contents are **not attested**, so do not claim comprehensive Python import provenance.
- **17 new committed regression methods** appended to the existing pinned `test_source_evidence_runner_r509.py` source test module: 11 package import-surface cases and six source-runner prelaunch/postflight cases (including the two-subprocess rewrite/restore negative control). The 416-command manifest remains unchanged.

## Reproducible focused Linux evidence, and its limits

- The locally executed copies of the **actual R523 production files** matched their GitHub Git blob SHAs: runner `41012656bd9bce5d145a21b008f3ebf842cf9655` (12,102 bytes), engine-custody helper `58a9c6942728adb446d616a2c987f1677659da7b` (4,183 bytes). Their R522 originals had blobs `4e8f6acb7878d79df002e1e3c0af51a28e579840` and `036af72bd251fd4c6ae0d3ea89fd92550084f720`. The unchanged descriptor helper was also byte-identical to its R522 committed blob `62c6c07a2df5aaed1bec7f8e16618038fbdde564`.
- Local synthetic isolated **17/17 PASS** on standard Linux CPython and **17/17 PASS** on `python -OO -B -W error`, for **34/34 focused method executions, zero skips**. It exercised real R523 runner `execute()`, real engine inventory/fingerprinting and real filesystem mutation; only the unrelated CI child environment, manifest reader and test-script postflight dependencies were stubbed. Full production-repository test module **not run**.
- Synthetic benchmark (112 small source files): **416 full engine receipt checks in 3.352s**, verifying 46,592 file entries, on the local Linux container. This is illustrative, **not** native Windows CI performance.
- `py_compile` passed for the focused runner, engine helper and focused regression harness. The committed 17 additions to the full test module have **not** run in the complete repository.

## Explicit security and release limits

This is **not** an atomic filesystem sandbox, does not attest CPython `__pycache__` contents or all Python imports, and cannot detect a modification made and restored entirely within one child process. The immutable 416-command manifest, app business logic, Decimal monetary rules, deterministic audit evidence, offline privacy, premium download restrictions and human compliance review are unchanged.

No hosted source matrix, native Windows x64 package smoke, Defender scan, accessibility result, file checksum, license/entitlement test, or verified distribution has passed for this R523 commit. All six standalone utilities remain **UNRELEASED**.

**Next:** Administrator resolves [Actions pre-step runner issue #75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75) and first proves one real runner can execute steps; rerun the exact R523 commit through the 416-command source matrix and Windows six-app build/smoke, Defender, accessibility, checksum and premium entitlement checks. Only after independent QD review and explicit founder approval may production or publishing be considered.
