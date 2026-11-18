# Final Vestige Labs R518 — source OS-error privacy and descriptor ownership

**Status:** Draft engineering change only. Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R517 draft [#2976](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2976), never on production `main`. No Windows EXEs, CMS publication, premium downloads, or compliance decisions.

## Root cause and fix

The previous `source_fingerprint` converted `OSError` to `SourceSnapshotRejected` **inside** an `except` block using `raise ... from None`. This hides the original exception from ordinary printed traces but leaves the original OS exception reachable through `error.__context__`, including private checkout filenames or raw OS diagnostics. A second failure mode chained `os.open` directly into `os.fdopen`; when `fdopen` failed before adopting ownership, the raw descriptor could leak.

The R518 change in `products/desktop/scripts/source_path_snapshot_r515.py`:
- Leaves the exception handler before raising the fixed, private-data-free `SourceSnapshotRejected`; verifies both `__context__` and `__cause__` are `None`.
- Explicitly closes a raw source descriptor if `os.fdopen` raises `OSError` or `ValueError`, preserving interruption behavior.
- Preserves bounded SHA-256 bytes, same-view / cross-view Windows metadata parity, regular unique-file / hardlink / symlink checks, and fail-closed digest comparisons.

## Regression evidence (2026-11-18)

Ten synthetic privacy/ownership tests were added to the **existing pinned-matrix-listed** `products/desktop/tests/test_source_evidence_runner_r509.py` module, exercised by its inherited normal and `-OO` command entries. They test missing file, private `os.open` and `os.fstat` errors, both `fdopen` exception classes and raw-descriptor cleanup, normal hash consistency, changed source rejection, interrupt propagation, invalid arguments, and linked source rejection.

- Local isolated Linux CPython focused test run against **byte-identical** production helper: **10/10 PASS** normal and **10/10 PASS** optimized (`-OO`), `py_compile` PASS. Checked exact helper Git blob SHA `62c6c07a2df5aaed1bec7f8e16618038fbdde564`.
- Negative control against exact R517 helper Git blob `324238969e892c0249f6ece9282034d41e9b27db`: **6 of 10 new tests FAILED** as expected, including private `__context__` retention and unadopted raw descriptors.
- The complete repository test module, all 416 pinned source commands, native Windows x64 execution, six EXE packaging, Defender scan and premium entitlement/download checks have **not** executed locally. The focused tests are not a full-suite or Windows result.

## Hold and next gate

The inherited exact-R517 GitHub Actions runs [desktop build 44263226771](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44263226771), [source 44263226784](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44263226784), and [identity 44263226838](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44263226838) all concluded failure before job steps with no assigned runner evidence. Root cause has not been proven. A repository/account administrator should inspect Actions billing/spend limits, workflow policy and runner eligibility, then rerun the exact-commit Ubuntu/Windows source matrix and six-image pipeline.

Keep the four free and two premium launchers distinct; no telemetry, public untested binaries, unrestricted premium payloads, payment approval, or automatic legal/compliance decisions. Independent QD review and explicit founder approval are required before any production merge or site publication.
