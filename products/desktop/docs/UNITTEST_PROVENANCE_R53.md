# R53: full unittest discovery and privacy-safe provenance

**Development only.** No Windows binaries, premium downloads, license keys, customer data or QD approval are produced by this sprint.

## Failure mode fixed

Python's standard `unittest discover` can exit successfully when it executes **zero tests** or silently misses a `test_*.py` module. R52 only checked its exit code, so an incomplete regression suite could be represented as a pass. R53 makes the R52 runner-independent source gate fail closed on absent/partial coverage.

## Behavior

- `scripts/unittest_provenance.py` inventories every `test_*.py` module (including nested paths), runs the discovered tests using `unittest.TestResult`, and demands an executed test from **every** inventoried module. It rejects zero tests, duplicate test IDs, omitted modules, failed/import-error tests, and an entirely skipped suite. Inventory bounds: 256 modules and 20,000 test cases.
- It emits **only** a compact JSON summary: schema, case count, module count, skip count, and a SHA-256 digest of the sorted test IDs. Test output and stack traces are redirected to the null sink, not included in evidence.
- `scripts/offline_source_gate.py` validates that summary against an exact schema and bounded values, then compares **all** fields between normal and `-OO` runs. Different discovered test IDs, test counts or skip counts reject evidence. The existing descriptor-checked source/test fingerprinting and all six synthetic source smokes remain required.
- The release flags remain `released=false`, `qd_approved=false`, `windows_executables_verified=false`, `premium_download_authorized=false`.

## Operator verification

In a trusted complete checkout with Python and desktop dependencies available:

```powershell
python -m unittest discover -s products/desktop/tests -p test_unittest_provenance_r53.py -v
python -OO -m unittest discover -s products/desktop/tests -p test_unittest_provenance_r53.py -v
python -m unittest discover -s products/desktop/tests -p test_offline_source_gate_r52.py -v
python -OO -m unittest discover -s products/desktop/tests -p test_offline_source_gate_r52.py -v
python products/desktop/scripts/offline_source_gate.py --report C:\\fvs-private-evidence\\new-r53-evidence.json
```

The evidence folder must already exist, reside outside the checkout and contain no file at the proposed report path. If a test file is intentionally only a helper, name it without the `test_` prefix. Legitimate platform-conditional skips are counted, but **a difference between normal and optimized skips** cannot be certified until investigated. On a failure, run ordinary unittest discovery locally for diagnostic tracebacks; do **not** attach those private logs to issue #73.

## Verification limits

R53's synthetic regressions exercise module omission, zero tests, all skipped, import failures, successful/failing private output, and an optimization-dependent skip. It does not by itself execute the complete repository suite or test real Windows x64 GUIs. Hosted GitHub Actions has repeatedly failed before executing steps; a workflow failure or absence of artifacts is not a pass. Windows candidate builds, real executable smoke tests, malware scans, checksums, premium gates and independent QD review remain mandatory. All six products remain unreleased.

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
