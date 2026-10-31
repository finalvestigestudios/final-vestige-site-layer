# R95 — SpendMap Lite direct Decimal representation envelope

**Scope:** products/desktop/fvs_suite/spend_input.py and its focused tests. Draft branch only; no production branch or website changes. All six Windows x64 utilities remain unreleased and require QD/founder approval.

## Problem and reproducible predecessor behavior

The regular CSV path parses financial values with strict bounds, but summarize_spend allows a caller-supplied parse_money callback. The reusable validated_spend_rows checked absolute dollar value and cent equivalence but **not the underlying Decimal tuple**. Decimal("0E-999999999"), negative signed zero with that exponent, and Decimal("0E+999999999") are finite and compare equal to zero; they passed the previous input guard.

An extreme negative exponent is not a valid financial cent representation. It can survive the direct helper, contaminate downstream month totals and generate unexpectedly large fixed-point baseline display strings. A callback can also return an unbounded coefficient with trailing zeros. This is a local direct-API robustness and audit-evidence problem, **not evidence of exploitation or a flaw in ordinary bounded CSV import**.

Minimal predecessor witness:

    from datetime import date
    from decimal import Decimal
    from fvs_suite.spend_input import validated_spend_rows

    rows = [{"row":"2","vendor":"ACME","date":"2026-01-01",
             "amount":"synthetic","category":"Parts"}]
    list(validated_spend_rows(rows, normalize_vendor=lambda _: "ACME",
         parse_date=date.fromisoformat,
         parse_money=lambda _: Decimal("0E-999999999")))

Before R95 this succeeds; after R95 it raises a private-input-safe ValueError with physical row number and **no source financial cell**.

## Fix and bounds

Before quantization, inspect Decimal.as_tuple() without converting the input to a string or performing context-dependent rounding. Reject direct-parser results with:

- More than **80 coefficient digits**.
- An exponent less than **-80** or greater than **12**, including for signed zero.
- More than **two significant fractional places**, ignoring trailing zeros. Cent precision is not inferred by silently rounding source values.

Retain the existing **$1 trillion absolute amount bound**, finite-Decimal-only checks, canonical physical row identity, 200,000-row cap, privacy-safe errors and private 64-digit quantization context. Ordinary cents, trailing-zero cents, negative amounts, refunds, the exact range boundary and non-mutated original records continue to work. No network access, telemetry, approval, payment, or compliance inference was introduced.

**Compatibility boundary:** This intentionally rejects nonstandard zero encodings and high-coefficient direct callback returns previously accepted. These representations have no meaningful place in the documented fixed-point financial import contract. Callers needing such encodings must normalize and validate their input explicitly *before* invoking SpendMap's public financial engine; never modify original source evidence.

## Test evidence and remaining release gate

Reproduction and test execution: Linux x86_64 Python 3.13.5, source file fetched from R94 and locally verified as the exact Git blob 5a5ade537fb9ae0f94abbfd77df6d63ee34892a7. The fixed source and 21-test module were exercised in a partial source environment. Focused tests passed **21/21 in regular Python and 21/21 under python -OO**, including 200,000 synthetic rows, hostile Decimal precision/traps, redaction, source preservation and boundary values. Python compilation succeeded. Before applying the code correction, the corrected test suite had **10 failures out of 21**, demonstrating previously accepted out-of-bound representations.

**Not verified:** full repository suite, all six Windows 11 x64 portable EXEs, GUI accessibility, malware scanning, packaging and actual distribution, premium entitlement, or QD sign-off. No executables or private financial data were uploaded.

**Next:** Repository owner restores GitHub Actions runner/job execution (see issue #75); run full desktop regression tests in normal/optimized Python and six native Windows x64 build/smoke checks, with artifact hashing and independent QD/founder review. Never merge/release solely on this focused preflight.
