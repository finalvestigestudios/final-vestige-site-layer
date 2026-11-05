# Labs R215 — leading formula-prefix custody for six-app CSV evidence

**2026-11-05 UTC — DRAFT / QD HOLD / NOT FOR RELEASE.** Feature branch feature/labs-r215-csv-leading-formula-20261105 extends immutable R214 commit 3ea06433797e18262218946ef1058f23663e6e25 (draft #1128), **not main**. No public binary, premium URL, payment activation, or WordPress production edit.

## Finding and concrete change

R214's shared write_csv_report boundary rejected formulas starting immediately with =, + or @ but accepted a rendered cell prefixed by whitespace or invisible formatting marks (e.g., TAB plus =1+1, nonbreaking-space plus +SUM(1), or zero-width-space plus @SUM(1)). CSV quoting is not a guarantee of spreadsheet-safe interpretation: import paths may normalize leading whitespace/format marks. Actual execution across spreadsheet implementations is **not** proven here; defense-in-depth is appropriate for financial audit exports.

R215 adds fvs_suite/csv_formula_guard.py and invokes has_unescaped_formula_prefix from the central _render_cell validator. It skips Unicode whitespace and a conservative set of invisible prefix marks (U+FEFF, U+200B/C/D, U+2060, U+200E/F) before testing the first non-prefix character for =, +, or @. It does **not** skip the apostrophe escape: intentionally escaped formula-like data can be preserved. It does **not** reject negative Decimal values, ordinary whitespace, or embedded multiline evidence that does not start with a formula. The caller-owned safe-cell sanitizer remains mandatory; this is an additional fail-closed guard, not a complete spreadsheet security guarantee.

Headers, report cells, and sanitized-but-ignored extra fields all use the same validator. Rejected values raise a static privacy-safe ValueError, do not leave partial files, do not consume later rows, and cannot overwrite existing evidence. No money calculations, input formats, compliance approvals, or provenance rules changed. No telemetry/uploads were added.

## Reproducible local test evidence (synthetic fixtures only)

Reconstructed parent R214 atomic_reports.py from exact Git blob 1356f6e0b4f102d8640295fca04141b4b6afa628 and independently checked with git hash-object. Against that unchanged baseline, the new R215 tests were **RED: 17 tests, 6 failures, 1 error**. The baseline accepted leading-whitespace and zero-width formula-like cells, including extras and headers, or reached exclusive publication before rejection.

After the fix, the local tests operated against exact Git source and inherited test blobs:

| File | Verified Git blob |
| --- | --- |
| fvs_suite/atomic_reports.py | 4d08b277b063fbf77d924e8e0dc71c0d25fb5c5b |
| fvs_suite/csv_formula_guard.py | 9600f6f1b9cbd6c47fda9d2a2b8473763b02275e |
| tests/test_atomic_formula_prefix_r215.py | 250ba2fd49eeac7898904757b6de7fdea7896cf6 |
| Inherited unchanged R214 tests | 298c969bf5809533fc1b1d0a87d85341836b64f8 |
| Inherited unchanged R27 tests | 251bb8a94141135cfd8f1b9bc1d5b1198e59359a |

Executed on Linux CPython 3.13.5 using local byte-identical reconstructed Git source and inherited tests, no customer data:

- cd products/desktop
- PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_atomic_*.py' -q
- PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_atomic_*.py' -q
- python -m compileall -q fvs_suite tests

Results: R215 **17/17 PASS**, inherited R214 **17/17 PASS**, inherited R27 **11/11 PASS**, or **45/45 ordinary** and **45/45 optimized (-OO), 90/90 total test-method executions**. Python compilation PASS; no local skips. The glob is scoped to the three files in the local reconstruction: **not** a full-repository regression claim.

.github/workflows/desktop-build.yml now requires R215 on Ubuntu and Windows, both modes, with redirected output and fail-closed PowerShell exit handling. Workflow declaration is **not** proof of hosted execution.

## Unverified release gates and next highest-impact action

The R214 hosted [Actions run #42081020805](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42081020805) failed: both source-tests and windows-build jobs returned steps:null. Exact infrastructure root cause remains unknown. Inspect the Actions run failure banner, billing/usage, repository Actions policy and hosted runner allocation; restore execution, then run the unchanged R215 HEAD on both platforms and the full inherited six-engine suite. Test all six GUI-to-CSV exports with actual supported spreadsheet import apps.

Hard release HOLD until six private Windows x64 portable EXE builds are reproducible, checksummed, Defender-scanned and smoke-tested; real Windows 11 keyboard/NVDA/high-DPI acceptance is witnessed; premium downloads are entitlement-gated; independent QD review and founder approval are recorded. No main merge or untested public binary distribution.
