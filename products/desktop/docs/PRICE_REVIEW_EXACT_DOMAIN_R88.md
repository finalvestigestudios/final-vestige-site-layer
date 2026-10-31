# R88 — fail-closed direct price-review Decimal domain

**State:** draft source only. No desktop executable, installer, premium entitlement or website download is approved for release. Parent: issue #73; stacked on R87 draft PR #320. This change does not adjudicate procurement eligibility, authorize payment or replace human review.

## Reproduced false-negative boundary

The R87 price-review helper protected comparisons using `Context(prec=64)`, but the directly callable API checked only magnitude and finiteness. It did **not** bound coefficient length or fractional scale.

For example, compare expected `100.01` against actual `102.0102` followed by 85 zeroes and a final `1` (in the fractional part). The true deviation exceeds the 2% threshold `2.0002`, but the previous 64-digit subtraction discarded the trailing `1`, returning **no review needed**. This witness lies outside the documented CSV parser's fixed-point domain; a direct caller nevertheless could supply it.

## Correction

`fvs_suite.review.price_outside_tolerance` now enforces the existing fixed-point input domain **before** any comparison:

- Actual, expected and absolute-price thresholds: finite `Decimal` values, up to 16 *significant fractional* places (8-place quantity multiplied by 8-place unit price).
- Fraction threshold: at most 8 significant fractional places, consistent with the strict JSON price-policy parser.
- Every operand: at most 64 coefficient digits and exponent between -64 and 27; trailing fractional zeroes do not add significant monetary scale.
- Existing numeric review limits still apply: absolute amounts up to `1e27`, nonnegative absolute policy, fractional policy between zero and one. Inputs exceeding any bound raise a generic, non-sensitive `ValueError`.

The approved domain requires at most 44 significant digits to subtract two bounded prices and at most ~52 digits to multiply a 27-integer-digit total by an 8-place fraction; the private 64-digit arithmetic context remains sufficient. The routine uses `Decimal.as_tuple()` for scale checks rather than `normalize()` or `quantize()` to avoid ambient-context rounding, preserves the caller's traps/flags/rounding state, and never echoes sensitive input values.

This is a **compatibility tightening for direct unsupported inputs**, not a rewrite of valid CSV parsing or published money totals. Existing valid procurement line totals, policy settings, source hashes, row references, decisions and audit manifests remain unchanged. Genuine out-of-domain source values must be corrected at intake instead of silently rounded.

## Evidence and repeatable commands

The exact committed production source and tests were independently hashed as Git blobs and compared to a locally executed, source-bound Python environment. Regression module: `products/desktop/tests/test_price_domain_r88.py` (**15 tests**, including 512 deterministic values compared with a separate 128-digit Decimal oracle).

Local focused commands:

```sh
cd products/desktop
python -m unittest discover -s tests -p 'test_price_domain_r88.py' -v
python -OO -m unittest discover -s tests -p 'test_price_domain_r88.py' -v
python -m compileall -q fvs_suite tests
```

**Local verification:** Python 3.13.5 on Linux, focused **15/15 passed** normally and **15/15 with `-OO`**, `compileall` passed. 512 comparisons matched the independent 128-digit reference under hostile caller precision and traps. The witness reproduced a previous false negative under 64-digit arithmetic. Only the focused helper and its new tests were executed, **not** the complete repository or Windows builds.

## Remaining gates

1. Restore Actions runner allocation (issue #75): source-tests and windows-build currently fail **before recording steps**; do not mistake infrastructure failure for tested Python source.
2. Run **all** desktop tests normally and under `-OO` from a complete repository checkout, inspect results, and resolve any integration failures.
3. Produce and smoke-test all six standalone Windows 11 x64 applications; inspect installer behavior, keyboard access, antivirus scan, hashes and absence of network/telemetry by default.
4. Hold all releases behind independent QD and founder approval; verify premium entitlement and protected download access before publishing anything.

No live website, production branch, premium asset or billing state was changed.
