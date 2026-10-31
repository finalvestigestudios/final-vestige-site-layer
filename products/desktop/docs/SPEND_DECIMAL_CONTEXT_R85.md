# R85 — SpendMap Lite fixed-point aggregation and median custody

**Status: draft source change; all six desktop products UNRELEASED.**
This is a focused source-preflight, not full-checkout or native Windows x64 verification.

## Reproduced defect

Python Decimal unary minus honors ambient precision: with prec=6,
-Decimal("123456789012.01") yields -1.23457E+11, not the
exact negative. The running median's two heaps used unary minus for
insertion, comparison, rebalancing and lookup, silently corrupting
rank order and historical spike baselines. SpendMap monthly addition
and the 2×-baseline comparison also inherited low precision and Emax.

For two vendor-month entries of 999999999999.99 the exact total must be
1999999999999.98, independent of caller context.

## Correction

1. Median heaps now use Decimal.copy_negate() (context-independent).
   Even-sized medians use an isolated Context sized from the integer
   and fractional places of both operands to retain half-cent evidence.
2. SpendMap summary runs in fresh localcontext(Context(prec=64)).
   This keeps all aggregation, parser callbacks and spike comparisons
   independent of caller rounding, traps and exponent limits without
   modifying the ambient process context.
3. Direct spend parser callbacks must return finite Decimal cents with
   absolute per-row value <= 1 trillion. This matches the ordinary
   engine.money CSV import contract. Nonzero subcent results are rejected;
   trailing zero representations such as 1.0000 remain allowed. The
   direct validator checks cents under a separate private Context.
   This is an intentional stricter contract for custom callbacks.

## Precision proof and preservation

200,000 verified import rows × 1 trillion per row yields at most 2×10^17
in absolute monthly total (20 integer digits and two cents), well below
the 64 significant digits used. The fixed direct-callback range stops
external callbacks from bypassing that guarantee. Financial values remain
Decimal. Original CSV input bytes, descriptor-verified SHA-256 fingerprints,
physical row citations, normalization collisions and review-only flags
are unchanged. The app does not approve expenses or decide compliance.

## Test evidence (Linux Python 3.13.5)

- 17/17 R85 isolated source-boundary tests passed normally.
- 17/17 passed with Python -OO.
- Compilation succeeded.
- Four Python implementation/test files matched committed Git blob hashes
  after reconstructing their exact bytes locally.
- An additional synthetic 200,000-row spend aggregation under prec=3
  gave exact total 200000000000000000.00 and retained every physical
  source row reference. A 50,000-entry running-median exercise passed.
- Original unary-minus/addition precision loss was reproduced.

The complete repository test suite and actual Windows 11 x64 executable
smoke were NOT run. GitHub hosted source and Windows jobs have been
failing before executing recorded steps (see infrastructure issue #75).
This preflight does not replace full CI, malware testing, accessibility,
verified checksums, or protected premium distribution.

**Release hold:** no binaries, public premium URLs, site publication, or
merges without independent QD and founder review.
