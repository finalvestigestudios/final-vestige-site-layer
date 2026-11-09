# R296 — CSV source snapshot exception-context privacy

**State: DRAFT / no merge or distribution.** Parent: R295 `10f8a8acf85737c74d536f123bf3f19dfb18b876`. Tracks issue #73. Independent QD and founder sign-off remain mandatory.

## Reproducible source defect

`fvs_suite/csv_snapshot.py` previously sanitized visible errors for `Path.lstat`, `os.open`, `os.fdopen`, `os.fstat`, and stream read/close failures with `raise ValueError(...) from None` **inside** the active `except` handler. Python suppresses normal traceback display but retains the source exception under `ValueError.__context__`, including synthetic customer file paths and OS error messages. A structured UI/debug log inspecting that chain can leak source identities despite a safe visible error.

## Implemented correction

- Each routine filesystem error sets a bounded, fixed failure marker during the handler and raises a fresh sanitized `ValueError` **outside** it, leaving both `__context__` and `__cause__` empty.
- Preserve original fixed user-facing messages and regular-file/size/identity/timestamp checks, point-in-time original CSV bytes, no-mutating-originals behavior, and Windows ctime compatibility.
- If `fdopen` fails before adopting a descriptor, close the original descriptor. Preserve `KeyboardInterrupt`, `SystemExit`, `GeneratorExit` and `MemoryError` semantics rather than converting them to success.
- No changes to Decimal money handling, engines, licensing, audit decisions, network access, premium gating, executable artifact uploads or site publication.

## Actual local evidence (Linux CPython 3.13.5, synthetic inputs)

- Exact Git blobs locally executed:
  - `products/desktop/fvs_suite/csv_snapshot.py`: `a695123f1adc133dfac2cc38726540fe373618fe`.
  - `products/desktop/tests/test_csv_snapshot_exception_privacy_r296.py`: `6c13f4ca134322a56231353b5a2e17105209752a`.
- New test file: **19/19 PASS** standard (`python -W error`), **19/19 PASS** optimized (`python -OO -W error`); **38 passing method executions**, source and tests compile.
- Exact previous R295 source blob `08c08598ac3575e3baf53ee3275db9aadc315f4d` with the **same** new tests: **14/19 failures** from the unprotected context introspection, validating a real preexisting defect (5 tests still pass).
- Test cases cover initial/final metadata errors, file open, descriptor adoption, initial/final `fstat`, read and close errors, actual descriptor closure, exact BOM/amount source bytes, size/symlink controls, and interrupt handling. No customer files were read.
- **Not verified:** full 300+ test inherited repository suite, GitHub-hosted Ubuntu/Windows execution, Windows 11 x64 executable build and smoke, Defender, accessibility, or premium delivery. This change is a focused shared CSV-source privacy improvement, **not** a completed release gate.

## Reproduction

From repo root:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_csv_snapshot_exception_privacy_r296.py' -q
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_csv_snapshot_exception_privacy_r296.py' -q
python -m py_compile products/desktop/fvs_suite/csv_snapshot.py products/desktop/tests/test_csv_snapshot_exception_privacy_r296.py
```

The existing `offline_source_gate.py` inventories and runs the suite's `test_*.py` files automatically, so the new test is included without widening the reviewed Actions workflow.

## Follow-up release gates

1. **Owner:** investigate GitHub Actions billing/spending cap, workflow permissions and runner availability; rerun unchanged R296 head once jobs can start and inspect full normal/`-OO` evidence.
2. Native Windows 11 x64: privately build six distinct executables, scan with current Defender, perform actual input/report smoke, keyboard/screen-reader checks, SHA-256 manifest validation, and verify premium entitlement/download segregation.
3. Independent QD and founder authorization **before** any merge, download publication or premium access change.
