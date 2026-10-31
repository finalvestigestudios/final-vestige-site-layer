# R89 — ProcureGuard independent Decimal exponent/trap context (DRAFT / HOLD)

## Reproduced accuracy defect

R84 improved arithmetic precision with `localcontext()`, then set its
precision to at least 64 digits. That copied caller `Emax`, `Emin`, rounding,
traps and flags. Consequently valid source data could raise `Overflow`,
report an inconsistent error, or behave differently based on the invoking
application's ambient configuration.

Synthetic accepted values: quantity `999999999.99999999`, unit price
`999999999999.99999999`, exact product
`999999999999999989990.0000000000000001`. With caller `prec=3`,
`Emax=6`, `Emin=-6`, `ROUND_DOWN` and enabled
`Overflow/Inexact/Rounded` traps, the previous wrapper raises Overflow.

## Code change and invariants

`fvs_suite/procurement.py` now uses
`localcontext(Context(prec=PROCUREMENT_PRECISION))` in
`_audit_decimal_precision`. Both `review_line` and direct
`_display_money` calculations run in a fresh 64-digit context with
independent exponent limits, traps and rounding. No global Decimal context
is changed. Documented bounded 8-place prices/quantities, up to 200,000 rows,
and 16-place extended totals fit that context.

Exact `*_exact` evidence, explicit `ROUND_HALF_UP` cent formatting,
source SHA-256/physical row references, human-only review flags, input
validation, privacy, and atomic report publication are retained.

## Verification and outstanding release gates

- Local Linux Python 3.13.5 **isolated source-equivalent** preflight:
  10/10 passed normally and 10/10 under `-OO`. Reproduced predecessor
  inherited-`Emax` Overflow and verified exact gross/credit/negative/subcent
  values, cent formatting, and unchanged caller state.
- New **13 repository regression tests** in
  `tests/test_procurement_exponent_context_r89.py`: direct review,
  custom contexts/traps, exact 100-line aggregate, physical CSV/manifest
  end-to-end, negative input nonpublication, and unchanged input bytes.
  **These committed repository tests have not been executed in a complete
  repository checkout**. Isolated source-equivalent preflight is not full CI.
- Native Windows 11 x64 six-app smoke, binary integrity checks, antivirus
  scan, entitlement verification, and actual distribution remain outstanding.
- Hosted GitHub Actions jobs fail before recorded steps; see issue #75.
  Repo admin should inspect Actions billing/spending cap, hosted-runner
  policy and run-level error banner; demonstrate one executed Linux test step
  before relying on CI evidence.

All six products remain **UNRELEASED / HOLD**. No public or premium
download may be published; independent QD and founder approval are mandatory.
