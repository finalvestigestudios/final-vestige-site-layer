# R348 — ProcureGuard Decimal callback context custody

**DRAFT / QD + founder HARD HOLD.** Issue #73. Parent is R347 draft PR #2005; never `main`. All six Windows x64 applications remain unreleased.

## Defect and boundary

`procurement.review_line` runs exact money aggregation under a fresh 64-significant-digit `decimal.Context`, but both `quantity` and `unit_cost` are injected Python parser callbacks. Before R348, `procurement_numeric_result_r345._checked` called `parser(value)` directly in that aggregation context. A parser could return the *correct* built-in `Decimal` while setting `getcontext().prec = 2`, changing rounding/traps/flags or calling `decimal.setcontext(...)`. Source-value equality still passed, but later multiplications and exact audit export fields could silently round. A synthetic `3 * 0.12345678` should be `0.37037034`; a poisoned context can yield `0.37`.

R348 puts **only callback execution** inside `with decimal.localcontext():`. Returning normally, throwing an exception, calling `setcontext`, and setting ordinary active-context flags/traps restore the parent's context. Independent source checks and returned-Decimal validation still operate outside the callback scope. Existing redacted errors, nonfinite/float/subclass rejection, 8-place precision, native source interpretation, and review-only status remain unchanged. This is **not** a security sandbox for arbitrary Python plugins: code holding a separate reference to the parent Context or otherwise executing arbitrary side effects can still mutate external state. Official shipped parsers remain the supported normal path.

## Exact evidence and reproducibility

- Original R347 helper Git blob: `a4a85721c99c376795dc269333f36b54339dc2cd`; local baseline file hashed to **exactly the same Git blob SHA**.
- Modified R348 helper Git blob: `aee0f7e48c06587392dd7045ea7c7781a2827b3d`; isolated local tested bytes and repository version match.
- R348 unit test Git blob: `e8fb36bd4ec09108bc1869af073e9d78431ef32a`; isolated local tested bytes and repository version match.
- Genuine `review_line` integration test source Git blob: `ab8a6d8750475193d550a9bfefe95e140654353e`; **syntax compiled, not executed** in the isolated local environment.
- Linux CPython **3.13.5**: **22/22 unit tests pass** under `-W error`; **22/22 pass** under `-OO -W error` (**44 passing focused executions**, no skips); source/unit/integration `py_compile` passed.
- Re-running the same 22 tests with the exact pre-fix R347 helper reproduced **20 failures / 22 methods**, including hidden exact-total rounding and precision/trap/flag mutations. Two legacy-compatible tests still passed.
- Original repo checkout, inherited procurement tests, 9 new real-engine integrations, 22 real AES-GCM integration tests, and native Windows builds **not executed locally**; no claim of release validation or Windows parity.
- Both independent Ubuntu and Windows workflow jobs now include all 22 unit and 9 `review_line` integration methods in **normal + optimized Python**, with Windows explicit exit-code checks (8 added commands). These jobs must actually execute before any confidence beyond the isolated helper is warranted.

From a trusted full checkout:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_decimal_context_r348.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_decimal_context_r348.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_decimal_context_integration_r348.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_decimal_context_integration_r348.py'
```

## Release requirements and follow-up

Restore Actions execution and run *these committed files* against the full repository, R342–R347 and the 22 genuine AES-GCM cases. Then complete the six native Windows 11 x64 build, executable smoke, Defender/EDR, SHA-256, accessibility and entitlement-controlled premium distribution checks. No production merge, public downloads, premium URL, payment authorization, QD bypass, user financial data transmission, or live site publication is permitted by this sprint. QD should review the callback-context contract and independent founder approval is required for release.
