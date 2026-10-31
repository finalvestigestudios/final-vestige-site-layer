# R84 — ProcureGuard exact Decimal context custody (DRAFT / UNRELEASED)

## Reproduced error: silent financial truncation

Python's default `decimal` precision is 28 significant digits. ProcureGuard
accepts quantities with eight decimal places up to 1,000,000,000 and
unit prices with eight decimal places up to 1,000,000,000,000. The exact
extended amount may need **37 significant digits**, even before adding
multiple invoices or credit/return movements. Consequently, source-valid
inputs formerly produced truncated `invoice_total_exact` amounts, contrary
to the R83 report's promise that those strings preserve exact subcent values.

Synthetic input:

- quantity: `999999999.99999999`
- unit price: `999999999999.99999999`
- default context result: `999999999999999989990.0000000` (**truncated**)
- mathematically exact result: `999999999999999989990.0000000000000001`

This is an exact-reconciliation / audit-provenance issue. The rounded cent
display happens to be the same for this vector, so a screenshot or a cents-only
test would not catch the evidence loss.

## Implementation

- A scoped `localcontext()` with **at least 64 significant digits** encloses
  all of `review_line` (PO, invoice, credits, receipts, price variance and net).
- The standalone `_display_money` helper also uses the scoped context,
  preventing `InvalidOperation` under a caller's low-precision context.
- The 64-digit bound covers the 200,000-row import cap, 9+8 quantity digits,
  12+8 unit-price digits, 16 potential product fractional digits, and
  6 additional integer digits from summing up to 200,000 lines.
- No global `decimal.getcontext()` mutation occurs. Decimal remains exact
  before the existing explicit `ROUND_HALF_UP` cents-display boundary.
- Original CSV source files, SHA-256, physical row references, unique report
  publishing, price policy, flags, customer privacy and human review remain.
- No AI inference, approval, tax, procurement or fraud determination is made.

## Acceptance and release boundary

New synthetic repository regression suite:
`tests/test_procurement_decimal_context_r84.py` (14 methods), including
default/low precision, rounding-mode isolation, normal cent behavior, gross
addition, credit offsets, negative-price review, and an actual end-to-end CSV
publication at low caller precision. Run under normal Python and `-OO`
on a complete checkout, then complete native Windows 11 x64 packaged
verification before any release. R84's isolated arithmetic preflight is
not a complete-repository or Windows build test.

All six standalone apps remain **HOLD / UNRELEASED**. The four free
executables cannot be advertised as verified downloads yet. Premium
executables must remain behind tested entitlement and paid access. Independent
QD review and founder approval are required before any production change.
