# Final Vestige Labs R345 — ProcureGuard numeric callback custody

**Status:** engineering draft, not released or approved. Issue #73. Branch:
`feature/labs-r345-procure-callback-decimal-custody-20261110`.
Stacked on R344 draft PR #1989 (exact parent `2bb635329277683a306a8bbd516fc4deb71284b7`),
**not** on production `main`. Independent QD review + founder authorization still required.

## Defect / scope

`fvs_suite.procurement.review_line` takes two injectable numeric callbacks
(`quantity` and `unit_cost`). Normal CSV imports call the bounded
`engine.qty` and `engine.unit_cost` parsers, but direct API callers can
supply callbacks that return a negative quantity, NaN/Infinity, a binary float,
an unexpected object, or an incorrectly precise Decimal. The previous code
used callback outputs directly in invoice, credit, PO and receipt totals.
Negative credit quantities could then invert an intended offset; nonfinite
results could lead to invalid totals or Decimal exceptions. Callback exceptions
might also contain private financial paths.

## Implemented

- `procurement_numeric_result_r345.py` verifies **native input storage**
  before invoking either callback: ordinary `str`, `int`, `Decimal` only;
  rejects subclasses/objects and huge integers before hooks.
- Requires callback output to have `type(result) is Decimal`, be finite,
  at most eight meaningful fractional digits, quantity in
  `[0, 1,000,000,000]`, and price in
  `[-1,000,000,000,000, 1,000,000,000,000]`.
  Negative prices remain possible but flagged for **human review**, preserving
  existing review behavior. Subcents and trailing zeros remain exact.
- Rejects extreme Decimal exponents outside [-80, 80], including enormous
  zero-scale values that could otherwise expand into megabyte-sized text
  during exact evidence rendering, despite having numerical value zero.
- Uses `Decimal.copy_abs()`, not context-sensitive unary `abs()`, so
  a low-precision ambient context cannot round a small over-limit amount into
  the allowed range. No binary float conversion is performed.
- Catches numeric-parser `Exception` with a stable redacted `ValueError`
  and suppressed exception cause. Intentional interrupts are not swallowed.
- Wires validation into all **five** numeric callback uses in
  `review_line`: order quantity and unit price, invoice quantity and unit
  price, receipt quantity. No original CSV data, audit row identities, or
  source digests are mutated.
- Adds 42 standalone adversarial unit tests and **21** separate full-engine
  integration tests. Both suites are blocking Ubuntu + Windows actions steps
  for normal and optimized `-OO` Python prior to packaging.

## Verification completed in this sprint

Environment: Linux CPython 3.13.5, entirely synthetic data, isolated
`fvs_suite` helper source with no customer files and no network.

```sh
PYTHONPATH=/mnt/data/labs_r345 python -W error -m unittest discover \
    -s /mnt/data/labs_r345/tests -p 'test_procurement_numeric_result_r345.py'
# Ran 42 tests ... OK
PYTHONPATH=/mnt/data/labs_r345 python -OO -W error -m unittest discover \
    -s /mnt/data/labs_r345/tests -p 'test_procurement_numeric_result_r345.py'
# Ran 42 tests ... OK
```

**84/84 focused executions passed; zero skips.** Both local files were
confirmed byte-identical to their GitHub committed blobs:
- helper `e8ee399d081d27b60b14338c3f6d2d33e9bc80cc`;
- unit tests `0edbfb48a22c6a9bd722c3cd1c82f6cfeebfae3b`.

**Not executed locally:** the changed `procurement.py` integration, 21 new
full-engine tests, inherited procurement tests, six EXE smoke tests, 22 genuine
AES-GCM integration tests, actual Windows x64 packaging, malware scans, or
premium entitlement verification. These are NOT claimed to pass. The
added integration test suite is a required hosted CI gate, not evidence of a
hosted pass while GitHub Actions runners remain blocked.

## CI / release blocker

The immediate predecessor [R344 Actions #42950162887](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42950162887)
returned failed `source-tests` and `windows-build` jobs on 2026-11-11
03:03 UTC; both report `steps=null`, no job logs, and one check annotation
per job. Available connector access cannot fetch the annotations, so the
cause is not established. The smallest owner action is to inspect the
GitHub Actions UI failed-job annotation and confirm billing/spending caps,
runner eligibility, and workflow permissions. A real step log is required.

## Hard release hold / next high-impact action

After CI provisioning returns, run **all** desktop tests including R342–R345
and 22 actual AES-GCM cases, then build and smoke-test all six Windows 11 x64
portable EXEs in a private environment; verify PE format, SHA-256 inventory,
Defender scan, accessibility and premium access controls before any QD/founder
approval. No downloadable product, public endpoint, unattended payment
authorization, AI compliance determination or live site change occurred.
