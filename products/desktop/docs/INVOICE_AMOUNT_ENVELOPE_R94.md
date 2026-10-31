# R94 — Invoice Twin Scout direct amount-domain guard (DRAFT / HOLD)

## Problem and scope

The normal local CSV import parses monetary amounts with a **one-trillion absolute ceiling** and a bounded 80-character input. The reusable `candidate_pairs(records)` API independently validates dates, normalized identifiers, physical CSV rows, nonfinite money, candidate limits and source limits, but previously allowed *any finite Decimal coefficient/exponent*. A direct caller could submit `Decimal("1E+999999")`, `Decimal("1E-999999")`, or a nine-significant-decimal-place amount and produce a review match for an amount outside the suite's expected financial envelope. This is **input integrity / reproducibility risk**, not proof of fraud, mispayment or an observed production exploit.

The change touches **only** `fvs_suite/invoice_match.py` and a new focused test module. It does not modify imported source files, provenance hashes, review classifications, GUI, pricing, payment entitlements, or any website release path.

## Contract and implementation

Before grouping, direct-API amounts now must be finite Decimals with:

- absolute value **<= 1,000,000,000,000** (matching the shared CSV parser's value boundary);
- coefficient **<= 80 digits** and Decimal exponent in **[-80, 12]**, preventing unbounded direct-call representations;
- at most **eight significant fractional places**; trailing zeros are not counted as significant fractional precision.

The last boundary intentionally preserves the pre-existing **R67 direct-engine half-cent behavior** (`Decimal("0.005")`) and eight-place exact evidence. Ordinary `engine.invoice_twins()` CSV amounts are still parsed and rounded to cents *before* candidate discovery. The direct API does **not** silently round overprecision values; it rejects them. This permits additional direct analysis precision without claiming such records were produced by the CSV importer.

Validation uses `Decimal.as_tuple()`, `copy_abs()` and exact comparison, not arithmetic or ambient Decimal rounding. Negative values and boundary amounts are supported. Any bad record fails before the function returns candidates, with an error that does **not** include confidential cell content. This is not input authenticity: a calling application must still bind the records to the descriptor-verified source snapshot for audited reports.

## Test evidence and limitations

Linux x86_64, Python 3.13.5, isolated **exact GitHub-source** `invoice_match.py` and a minimal `review.ascii_case_identity` stub (not exercised by these 19 tests):

- **Red phase:** 12 of 19 new tests failed against **unchanged R93** source blob `d1befc13cdc248585a802dfb9ad8b0462220d1d2`, reproducing out-of-domain acceptance.
- **Green phase:** **19/19 passed** normally; **19/19 passed** with `python -OO`; `compileall` passed.
- **Stress:** **200,000 reverse-ordered distinct-vendor records**, with `Decimal("1000000000000.00")` under hostile precision/exponent/trap settings, yielded **0 false candidates**, passed in 2.485 seconds (maximum local RSS 326,600 KiB). This is a synthetic isolated source test, not native app benchmarking.
- Verified updated implementation **Git blob `8c6bb54e30b4cbaf9f3806682d0f15a1664ec5bd`** and 19-test **Git blob `2852dc094cc52722ecade4c8209d9a6983c3c05b`** against the locally executed exact files.
- Direct boundary examples exercised: exact positive/negative ceiling, positive/negative overage, huge positive/negative exponents, anomalous zero exponent, excessive coefficient length, ninth fractional digit, trailing zero equivalence, preserved half-cent/eighth-place amounts, negative zero, order stability, no partial results, no amount leakage, unmodified caller records, and hostile Decimal context.

Run the committed focused tests in a **complete checkout**, once runners are available:

```sh
cd products/desktop
python -m unittest discover -s tests -p 'test_invoice_amount_envelope_r94.py' -v
python -OO -m unittest discover -s tests -p 'test_invoice_amount_envelope_r94.py' -v
```

**Unverified:** complete repository tests, full imported CSV→GUI→export integration, Windows 11 x64 native executables, installation/AV scans, verified online downloads, accessibility and QD/founder review. Previous GitHub Actions jobs under issue #75 have failed before executing steps; local tests are **not CI passing evidence**.

## Release gate

All six tools remain **DRAFT / UNRELEASED**: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk (free); GrantAudit Studio Pro and ProcureGuard Studio Pro (premium). Preserve local financial privacy, provenance, offline processing, human review and gated premium distribution. Do not merge to `main`, publish executables/download links or remove independent QD/founder approval until the complete release gates pass.

**Next highest-impact step:** restore GitHub Actions runner startup, rerun full Python regression tests and Windows six-launcher packaging; perform native Windows 11 x64 smoke/accessibility/integrity review before considering distribution.
