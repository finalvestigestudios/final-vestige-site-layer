# R86 — shared financial parser and legacy reconciliation context custody

**Status: DRAFT only, all six Windows desktop apps UNRELEASED.** See issue #73.
No payment, grant eligibility, procurement compliance, or fraud decision is
automatic; all exceptions require human review.

## Reproduced bug and risk

Under a caller Decimal context with `prec=6`, applying unary negation to
`Decimal("999999999999.12345678")` produces `-1.00000E+12`, destroying the
original negative unit price. Likewise `Decimal.normalize()` rounds before
testing an eight-place quantity/price scale; it can turn an invalid 9-place
value into an apparently valid integer. The shared `money()` and `dollars()`
cent quantizers inherited precision/rounding/trap settings, and legacy
LedgerDiff/GrantAudit aggregations used that same mutable context.

## R86 correction

- `_exact_amount`: context-independent `copy_negate()` rather than unary
  minus; retain accounting syntax, amount bound, and source-privacy errors.
- `_fractional_places`: inspect raw Decimal coefficient/exponent to enforce
  eight **significant fractional places**, permitting trailing zeroes and
  exact zeros without rounding.
- `_cent_value`: fresh local 64-digit Context and explicit `ROUND_HALF_UP`
  for `money` and `dollars`; no caller precision, trap, or flag mutations.
- `_exact_reconciliation_context`: local 64-digit Context around complete
  LedgerDiff and GrantAudit reconciliation, including linked-grant handling.
  This covers bounded 200,000-row import totals at up to 1 trillion per row.
- The invoice candidate parser and the R85 SpendMap summarizer inherit
  context-safe shared money parsing. ProcureGuard retains its scoped R84
  exact subcent arithmetic; no approvals or review thresholds changed.

The fixed-point Decimal source coefficients, SHA-256 source custody, physical
CSV row references, normalization-collision flags, non-destructive exports,
and optional human review workflows remain intact. No floating point or
network upload was introduced.

## Verification and acceptance gates

On an isolated Linux/Python local source-equivalent boundary, 6 focused
unittest methods passed normally and under `python -OO`. These tests covered
multiple ambient Decimal precisions, hostile traps, signed sources, exact
quantity/price precision, half-up display, preservation of caller context,
and a synthetic 200,000-entry accumulation. This does **not** count as
execution of the new repository integration test file.

The committed `tests/test_engine_decimal_context_r86.py` contains 12
full-source regression methods spanning direct parsers, ledger reconciliation,
legacy grant totals, invoice candidates, SpendMap, and premium three-way
procurement. They must execute in a full checkout when GitHub Actions runner
infrastructure issue #75 is fixed. Then run complete source tests normal and
optimized, Windows 11 x64 executable packaging/install/GUI-accessibility
smokes, security and SHA256 checks, premium entitlement-gating verification,
and independent QD/founder approvals before release.

No executable or public download was created in this sprint.
