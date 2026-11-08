# R274 — Integer-only private source-suite receipt evidence

**Issue #73. DRAFT / UNMERGED. Independent QD and founder approval required.**
This is a parser and regression increment, **not** a Windows build, antivirus clearance, release, or premium distribution approval. All four free and both premium utilities remain behind existing release gates.

## Reproduced gap in R273

R273 rejects duplicate object members and literal `NaN`/`Infinity`, but Python's `json.loads` still quietly accepts JSON exponent and fractional syntax. A legal JSON token `1e400` decodes to Python `float('inf')`; `1e-9999` becomes `0.0`; decimal fractions lose precision. The existing real source-suite producer (`scripts/offline_source_gate.py` + `scripts/source_smoke_gate.py`) emits **integer-only numeric counts**; no JSON fractions are part of its schema. This is an ambiguity in retained private evidence, not evidence of a compromised real build.

A new R274 numeric test suite was executed against the **byte-exact parent R273 decoder blob `6573efa690c287f3e931cbca011b4e8ca93b1f73`**: **12 of 19 tests failed**, demonstrating the baseline admits float syntax.

## Change and boundaries

- `scripts/strict_source_receipt_r273.py` now passes `parse_float=_reject_fractional_number` to `json.loads`. It rejects **all** fractional and exponent-form numbers at every nesting depth, including `18.0`, `1e2`, overflow, underflow, and rounded decimals. Exact JSON integer counts, booleans, strings, valid Unicode, duplicate-key detection, and fixed path-safe rejection remain intact.
- `tests/test_strict_source_receipt_numbers_r274.py`: **19 new methods** for exact integers, nested evidence, float overflow/underflow, rounding, duplicate and privacy regressions, and an actual isolated `python -I` subprocess with a hostile cwd/`PYTHONPATH` shadow import.
- `.github/workflows/desktop-build.yml`: both source-tests (Ubuntu) and Windows-build jobs explicitly run the new module under normal and `-OO` Python.
- No changes to executable-build orchestration, GUI decisions, financial calculations, premium entitlements, Windows download links, or website production.

The strict JSON decoder does **not** independently certify receipt schema, test provenance, file custody, installed toolchain, Windows PE characteristics, malware clearance, signing, native GUI behavior, or release approval. Existing gates remain mandatory.

## Locally executed evidence — 2026-11-08 UTC

Environment: Linux, CPython 3.13.5; source-only synthetic fixtures, and actual isolated child interpreter. The local baseline decoder and existing R273 test suite both matched their GitHub Git blob hashes exactly before modification:
- Parent decoder: `6573efa690c287f3e931cbca011b4e8ca93b1f73`
- Existing R273 17-method suite: `c2d7d83b97b80598917ef6817c05fc12ad9e8a55`
- Updated decoder Git blob: `9de54dd6b6d9f0f2f07298fe90ebeaa77bf0ade4`
- New R274 suite Git blob: `9de0f06626bb8d9e2a55ac3c544ebc676bd3bda8`

Local commands:
```bash
python -W error -m unittest discover -s products/desktop/tests -p 'test_strict_source_receipt*.py'
python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_strict_source_receipt*.py'
python -m compileall -q products/desktop/scripts/strict_source_receipt_r273.py products/desktop/tests/test_strict_source_receipt_numbers_r274.py
```
Results: **36/36 normal PASS**, **36/36 optimized PASS** = **72/72 focused test executions**, no skips or failures; compilation PASS. The 19 new tests include a real `-I` child process. Exact local Git blob hashes match the branch's committed Python files.

**Not executed or claimed:** the complete inherited repository regression suite, R273's 8 runner integration tests, hosted Ubuntu/Windows CI, Windows 11 x64 candidate builds, actual six EXE smoke, Defender scan, native accessibility, code signing, protected premium delivery, or independent QD/founder acceptance. Do not equate decoder tests with build verification.

## Next highest-impact step / owner unblock

Restore GitHub Actions hosted runners by checking spending/billing caps, workflow policy and runner provisioning; rerun the unchanged R274 head and inspect the full inherited suite. On a trusted Windows 11 x64 checkout with preinstalled audited tooling, use the previously added **private** offline candidate runner with an access-controlled workspace outside source. Preserve actual six portable EXEs and source/native evidence privately, scan and smoke-test each, verify hashes and keyboard/high-DPI/screen-reader behavior, and separately test that premium files cannot be obtained without entitlement. Independent QD and founder authorization are required before merge or distribution.
