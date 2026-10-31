# R83 — ProcureGuard exact subcent custody (DRAFT / UNRELEASED)

## Defect reproduced

ProcureGuard Studio Pro accepts unit prices through eight decimal places and
correctly accumulates quantity × price as `Decimal`. However, its CSV
`invoice_total`, `gross_invoice_total` and `credit_value` display columns
previously called `Decimal.quantize(0.01)` **without specifying rounding**.
Under Python's default `ROUND_HALF_EVEN`, an exact positive amount of `0.005`
was displayed as `0.00`. The suite's own financial input rounding uses
`ROUND_HALF_UP` (`money("0.005") == 0.01`). Thus identical half-cent amounts
could appear differently depending on whether they came from per-transaction
money imports or from procurement extended prices.

## Implementation

- Apply explicit `ROUND_HALF_UP` to all three procurement display-money
  fields. This is consistent with the existing shared `engine.money` policy.
- Give shared `engine.dollars` the same explicit rounding argument. This
  removes implicit dependence on the process-global Decimal rounding context.
- Append three **additional** report columns:
  `invoice_total_exact`, `gross_invoice_total_exact`,
  `credit_value_exact`. These use `format(decimal_value, "f")` without
  changing precision or applying a second rounding step.
- Existing column order, column names, input snapshots, source physical-line
  references, price-policy SHA-256, normalized ID review, anti-formula CSV
  rendering, report/inventory publication and human-only decisions are kept.
- **No currency conversion, tax accounting, automatic bill approval or
  compliance certification** is introduced. Financial computations and price
  comparisons remain exact, with rounding only for money display.
- The displayed net is rounded **independently** from displayed gross and
  credit. Subtracting the rounded gross and credit can differ by a cent from
  the rounded exact net. Use `*_exact` columns for audit reconciliation
  and retain the signed-off original source exports. Reading an exact field
  through a spreadsheet numeric parser may lose trailing zeros/precision;
  import it as text to preserve the decimal representation.

## Synthetic acceptance vector

| Event | Exact Decimal | Prior display | R83 display |
| --- | ---: | ---: | ---: |
| invoice 1 × 0.005 | 0.005 | 0.00 | 0.01 |
| invoice 1 × −0.005 (review flag retained) | −0.005 | −0.00 | −0.01 |
| invoice 1 × 0.015 | 0.015 | 0.02 | 0.02 |
| credit 1 × 0.005 | 0.005 | 0.00 | 0.01 |
| gross 0.015 minus credit 0.005 | 0.010 | 0.01 | 0.01 |

## Verification boundary and release hold

Repository test module: `tests/test_procurement_subcent_custody_r83.py`.
It includes 13 offline methods covering exact values, positive and negative
ties, context independence, gross/credit/net, review flags and an end-to-end
three-way CSV export with unchanged input bytes. Tests must pass under
normal and optimized `-OO` Python in full CI. Prior source-only attempts
do not establish these tests have run against a full checkout.

Release remains **HOLD** pending GitHub Actions runner recovery (issue #75),
complete repository tests, real Windows 11 x64 packaging and six-EXE smoke,
AV/signing, separate distribution verification and independent QD/founder
approval. No premium executable can be published to an unprotected URL.
