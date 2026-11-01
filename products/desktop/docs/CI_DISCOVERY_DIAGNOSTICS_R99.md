# Labs R99 — discovery diagnostic escapes privacy sink, not financial data

Issue #73. Stacked only on R98 draft #387; not production `main`.

## Root cause, reproduced scope

R98's actual hosted Linux source gate reported nine failures and one error across seven code-owned test modules. Its committed `test_real_synthetic_import_failure_reports_discovery` regression was among the failures. Source review found that `unittest_provenance.run()` constructed an approved static discovery diagnostic but called `_emit_diagnostic()` **inside** `contextlib.redirect_stdout(os.devnull)`. Thus the marker was suppressed along with private import output, and the parent could not identify omitted test modules. This is a reporting defect, not a financial engine or entitlement bypass.

R99 computes `_discovery_summary()` under the private stdout/stderr suppression boundary, then leaves the suppression context *before* emitting the bounded source-owned marker. It raises the same error and returns the same nonzero exit. It does **not** run surviving tests when discovery is incomplete. The accepted parent validator, 12-module cap, private stderr suppression, 2,048-byte cap, ordinary/full source suite, `-OO`, source fingerprinting, six engine smokes, privacy restrictions and release gates are unchanged. It preserves legitimate results and does not write diagnostic artifacts to disk.

## New executable regressions

`tests/test_discovery_marker_r99.py` adds three synthetic-only subprocess checks:

1. Real `ImportError` with a fake private path yields validated `phase=discovery` marker in **normal and `-OO`**, the generic stderr rejection, nonzero status and zero leakage.
2. An import failure prevents execution of another valid discovered test (verified with absent sentinel file).
3. Eighteen synthetic import failures produce a sorted maximum-12 list with omitted count six; all exception text remains private.

R98's existing `test_real_synthetic_import_failure_reports_discovery` should additionally become green. No actual customer data or file paths enter CI diagnostics.

## Verification and release hold

Local Python proof reproduced why a `print` inside redirected stdout disappears while a post-context print is visible. **That proof is NOT equivalent to running the committed files.** The actual committed tests must be executed in the exact GitHub Actions checkout before claiming full pass:

```sh
PYTHONPATH=products/desktop python -m unittest -v \
  test_private_suite_diagnostics_r98 test_discovery_marker_r99
PYTHONPATH=products/desktop python -OO -m unittest -v \
  test_private_suite_diagnostics_r98 test_discovery_marker_r99
```

Run from `products/desktop/tests`, or use the repository-wide discovery gate from root as CI does. If source CI remains red, identify and fix the remaining six legacy failure modules (see R98 issue #73 comment) using a trusted full checkout and synthetic fixtures. Do not weaken, skip, or bypass source gates to manufacture Windows executables.

No WordPress changes, no release URLs, no premium license/access changes, no untested Windows EXEs. Four free and two premium apps remain **UNRELEASED**. Requires complete normal/`-OO` source green, Windows 11 x64 GUI and binary smokes, AV/checksums/accessibility, premium entitlement control, independent QD and founder approval before any merge or publication.
