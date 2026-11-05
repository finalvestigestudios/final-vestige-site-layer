# R212 — private exception custody for CSV callbacks and input iterables

**Status:** DRAFT / HARD RELEASE HOLD. Tracks #73. Stacked on R211 draft #1107 (commit `53e4f301f555cbc29702935c33085763ce83c60d`), never on `main`.

## Reproduced risk
R211 used `raise ... from None` **inside** a sanitizer `except` block. Although the displayed traceback omitted the private original exception, `exc.__context__` still held its financial payload, accessible to exception-inspection tools. In addition, errors raised by caller-owned field generators, row generators, and custom Mapping.items() iterators propagated their unredacted private exception text. A partially populated report was removed, but a UI or diagnostic logger could still expose it.

## Implementation
- Shared `fvs_suite.atomic_reports.write_csv_report` now raises a static `ValueError` **after** the original exception-handler block, with no hidden exception context, for sanitizer, schema-iterator, record-iterator and row-item iterator failures. The sanitizer keeps `from None` for existing caller compatibility; `__context__` and `__cause__` are now both `None`.
- Explicit `next()` distinguishes a normal iterator exhaustion (`StopIteration`) from operational exceptions. Generator rows remain lazy; no materialization of the full dataset.
- Non-`Mapping` rows, missing or duplicate columns, native-text constraints and existing report publication rules still fail closed. `KeyboardInterrupt` and `SystemExit` are not swallowed.
- Updated inherited R27 generator regression to require privacy-safe generic error text, replacing its previous expectation that financial source exception text was passed through.
- Both Ubuntu and Windows `desktop-build.yml` jobs require 16 new regression tests in normal and `-OO` Python, with test output suppressed and Windows exit-code guards.

## Reproducible local testing (2026-11-05 UTC)
Linux x86_64, CPython 3.13.5; isolated source-only reconstruction with all tested files **byte-identical to GitHub blobs**, synthetic fixtures and temporary files, `-W error` warnings-as-errors.

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_atomic_*.py' -q
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_atomic_*.py' -q
python -m compileall -q products/desktop
```

- **RED:** exact R211 baseline writer `c8767290f430748950b8063ea849982ec1f6fb44` with new R212 tests: **4 assertion failures + 6 errors / 16 tests**. Leaks verified in the sanitizer `__context__` and unredacted input exceptions.
- **GREEN:** R212 new 16/16; inherited exact R211 14/14; revised inherited R27 11/11. **41/41 PASS normal and 41/41 PASS -OO = 82/82 method executions**, zero skips in local Linux test run; Python compilation PASS.
- Synthetic fixtures cover immediate/late header, row and item iterator errors; no financial data in visible text, `__context__`, `__cause__` or formatted exception; no partial files, existing evidence preserved, 35-row lazy streaming, exact Decimal strings, BOM, newline round-trip, 5,000-row inherited stream test, private POSIX mode and non-replacing report publication.
- Git blobs verified: writer `ad9e1aec5f89bd1ebebc8ae20ea18e6a88806e4a`; new R212 tests `5faf96f3cf779305e57f91e526db47cf0fb3a2f0`; revised R27 `251bb8a94141135cfd8f1b9bc1d5b1198e59359a`; unchanged inherited R211 `8b404769c75cdc661f2b79e8988119a733bc7f52`.

## Limitations / release gates
- This was **not** a complete repository integration run, an actual Windows x64 build or physical Windows desktop acceptance. Failure of GitHub Actions before job steps remains a separate runner/account issue; only a verified runner execution can lift the hosted-CI hold.
- Errors emitted by the filesystem/OS, Python internals outside the wrapped callbacks and the caller's own untrusted error-log introspection remain outside this narrow fix. Desktop UI must still display only safe errors and must not serialize caller input objects.
- Full inherited multi-application regression, Windows 11 keyboard/screen-reader/scale acceptance, real Defender/EDR scan, six signed/appropriately disclosed binaries, checksum and smoke evidence, **protected** Pro distribution, independent QD review and founder approval are outstanding.

## Next highest-impact action
Restore GitHub Actions runner execution (check billing, usage restrictions, runners and permissions in [R211 failed run](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42051153001)), then rerun this exact R212 commit and execute the full inherited regression matrix on Ubuntu/Windows. Only after independently verifying all six native x64 builds should packaging/release approval be considered.

**Do not merge to production or publish downloads, including either Pro executable.** No financial calculations, regulatory conclusion or approval decisions were changed.
