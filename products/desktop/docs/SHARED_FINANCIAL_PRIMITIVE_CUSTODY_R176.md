# R176 — Shared financial primitive custody (DRAFT / HARD RELEASE HOLD)

## Threat and scope

The common `engine._exact_amount` and `engine.qty` parsing boundaries previously used `isinstance(value, (float, bool))` and then `str(value)`. A direct Python caller could supply a `str`, `int`, or `Decimal` subclass with an overridden `__str__` method. For example, an object whose stored amount is 999999999999999 could print as "0" and pass the exact-money parser as zero; a malicious conversion could also execute code or raise while financial evidence was being prepared. The CSV import path normally provides ordinary strings, but shared parsers are independently callable by downstream integrations and tests.

## Correction

- `money` and `unit_cost` now inherit `_exact_amount`'s **exact-native-type** gate. `qty` applies the same gate independently. Only exact built-in `str`, `int`, and `decimal.Decimal` values proceed; bool, binary floats, subclasses and arbitrary `__str__` objects are rejected without invoking their conversion hooks.
- An actual, built-in integer larger than 269 bits is rejected before `str()`, avoiding an expensive or version-dependent thousands-of-digits conversion. The unchanged 80-character, grouped-number, sign, cent rounding, quantity-scale and maximum-amount boundaries still apply afterward.
- Error messages are generic; they do not echo financial source values. No input file is modified, no telemetry or network use is introduced, and no review finding is converted to a compliance or payment approval.
- Standard accounting strings from offline CSV readers remain unchanged. Native integer and Decimal convenience arguments still work when their lexical format is otherwise acceptable.

## Evidence / acceptance

`tests/test_shared_financial_primitives_r176.py`: **30 explicit synthetic test methods**, including forged and hook-raising subclasses across all three public numeric parser entrypoints; float/bool/object rejection; ordinary string/int/Decimal examples; huge native integer; exact limits and invalid exponent syntax.

`scripts/safe_unittest_r176.py`: fixed 30-name inventory, fixed test class, no skips/unexpected successes, stdout/stderr suppressed, nonzero exit for inventory drift or test failures. Cross-platform `.github/workflows/desktop-build.yml` requires this gate in **normal and `-OO` Python on both Ubuntu and Windows** (up to 120 CI method executions if jobs can allocate runners). Local focused execution cannot substitute for the native Windows executable or independent real-machine acceptance.

Run locally from repository root:

```sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r176.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r176.py
```

This change is a direct-API trust-boundary hardening, not a substitute for a complete full-suite test, an x64 executable smoke test, physical Windows 11 accessibility (46 observations), genuine Defender/EDR, code signing, authenticated premium distribution, independent QD approval, or founder release authorization. **Do not merge into production or distribute executables until the existing release gates are satisfied.** Maintain the feature-branch/draft-PR review chain.
