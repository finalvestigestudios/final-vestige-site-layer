# R356 — SpendMap Lite original monetary source custody (2026-11-11)

**State: DRAFT ONLY. No merge, build distribution, premium entitlement change or site publication. QD/founder review remains required.**

## Reason for this change

The prior SpendMap direct-API boundary validated only the **returned**
`parse_money` Decimal, not the original imported `amount` text. An injected
parser could convert `$100.00` to `1000.00`, discard a negative sign on
`-0.00`, or convert otherwise-invalid input into an apparently legitimate
Decimal. Neither the report's source SHA nor its line references by themselves
prove that the reported number matches the underlying text.

## Implemented behavior

* `fvs_suite/spend_source_custody_r356.py` independently reads the **native
  source string**, enforces the same grouped/signed/accounting amount syntax
  and monetary range as `engine._exact_amount`, and applies the same
  `ROUND_HALF_UP` cent quantization under a private 64-digit Decimal context.
  No floats, Unicode digits, exponent notation, arbitrary object methods or
  malformed monetary syntax are permitted.
* `validated_spend_rows` now prevalidates **every** original amount across
  the frozen source collection **before invoking any caller callback**.
  A later invalid source cannot be hidden by a parser or trigger an earlier
  parser before source lexical preflight completes.
* After parsing, the native returned Decimal must equal the original
  canonical cent amount, including the sign bit of zero. Valid accounting
  parentheses, leading currency signs, grouping, and legitimate half-up
  cent rounding remain supported. CSV inputs and source records are not
  changed; mismatches raise a sanitized row-specific ValueError.
* Unit tests cover 26 methods. A separate 14-method integration module
  cross-checks the actual shared `engine.money`, full input boundary, and
  `summarize_spend` including conservative human review and source
  provenance. CI runs both modules in standard and optimized Python on
  Ubuntu and Windows.

## Executed evidence vs unverified gates

* **Executed:** CPython 3.13.5 Linux, synthetic local standalone harness,
  exact committed `spend_source_custody_r356.py` and unit test file:
  **26/26 passed** normal and **26/26 passed** with `python -OO`, both
  under `-W error` (**52 focused executions**). `compileall` passed.
  The committed GitHub blob SHA must be checked against the local
  `git hash-object` values before treating it as exact source proof.
* **Not executed:** 14 integration methods against the private repository,
  existing R342–R355 regressions and 22 AES-GCM cases, full Linux/Windows
  workflow, actual six Windows x64 EXEs, Defender, accessibility or
  protected premium distribution. They MUST NOT be counted as passing.
* **Known infrastructure blocker:** R355 GitHub Actions
  [#43035338611](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43035338611)
  reported both jobs failed **before runner assignment and before any steps**.
  Root cause not confirmed; examine failed-check annotations, billing/spend
  limits and runner eligibility. Re-evaluate the R356 run separately.
* **Boundaries:** This is not source authentication, a sandbox for arbitrary
  injected Python callbacks, or a financial/compliance decision. An actor
  controlling original CSV files and digest can still fabricate a consistent
  replacement. All findings require human review; no customer data uploaded.

## Reproduction once trusted checkout/runner is available

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_spend_source_custody_r356.py' -v
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_spend_source_engine_integration_r356.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_spend_source_engine_integration_r356.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
```

Next highest-impact release gate: restore hosted CI; execute **full integration
and inherited suites on the exact R356 head** before any Windows 11 x64
packaging/AV/UX and QD/founder approval review. No executable is published.
