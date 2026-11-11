# R355 — SpendMap callback Decimal context custody (2026-11-11)

## Defect and scope

SpendMap Lite uses caller-supplied `normalize_vendor`, `parse_date`,
`parse_money` and `format_money` hooks. `summarize_spend` already
enters a private `Context(prec=64)`, but a callback can call
`getcontext().prec = 2`, mutate traps/rounding/flags or replace its
thread's active context with `setcontext(Context(prec=2))`.
Without a *nested per-callback* context, subsequent exact aggregation or
review comparisons can run with the changed context. On two synthetic
`999999999999.99` source charges, 2-digit precision can make a rounded
sum appear instead of the exact `1999999999999.98`.

This fix hardens the **free SpendMap Lite** direct source interface; it
does not modify other five products, financial source files, approvals,
release state, premium entitlements, or WordPress.

## Change set

- `fvs_suite/spend_callback_context_r355.py`: tiny generic
  `invoke_spend_callback` wrapper. `decimal.localcontext()` surrounds
  each callback, restoring the caller's full active Decimal context even
  after a `setcontext` swap or an exception. It passes original values
  through without coercion.
- `fvs_suite/spend_input.py`: use isolation at **all three** source
  callbacks, retaining existing type/range/cent checks and sanitized
  source-row error paths. Per-row prevalidation remains complete before
  any iterator emits an output record.
- `fvs_suite/spend_analysis.py`: isolate **all six** report-money
  formatting invocations, so a hostile formatter cannot contaminate
  the next displayed financial field or alter aggregate arithmetic.
- `tests/test_spend_callback_context_r355.py`: 17 focused unit
  methods, including context flags, traps, precision, rounding,
  `setcontext`, exceptions, exact sums, and repeated formatting.
- `tests/test_spend_callback_engine_integration_r355.py`: 12 additional
  tests against the real summarizer/input parser, including exact
  two-charge aggregation, formatter context, spike thresholds,
  source-row evidence and untouched originals.
- `.github/workflows/desktop-build.yml`: one new Linux and one Windows
  step, each enforcing **both** new test modules in normal and
  optimized (`-OO`) Python; on Windows each command checks exit status.

## Evidence and limitations

A standalone Linux Python harness exercised the exact committed
`spend_callback_context_r355.py` and focused unit-test blobs:
**17/17 PASS normal; 17/17 PASS `-OO` = 34/34 executions**.
The committed blob SHA-1 values were independently compared to the
locally executed file bytes. Three Python files were AST-parsed locally
(helper, unit and integration tests).

The **12 full SpendMap engine tests have not been run** against the
complete trusted checkout in this sprint; CI must execute them on the
exact PR head. Native Windows acceptance, signed/unsigned binaries,
Defender, verified downloads, and all other product release gates
remain pending.

This is a Decimal-context isolation defense, not a sandbox against
arbitrary Python callbacks: such callbacks remain trusted code, can
perform side effects, and can intentionally return false values.
Result-type and monetary-domain validation remains in the established
input boundary. Neither helper nor formatter makes a compliance
decision.

## Next gate

1. Fix GitHub-hosted runner allocation (recent Ubuntu and Windows jobs
   failed before any steps; do not infer the infrastructure root cause).
2. Execute these **12 real engine integration tests**, the 17 focused
   tests, all inherited R342–R354 tests and 22 real AES-GCM integration
   checks in Linux and Windows CI, with concrete logs.
3. Require native Windows 11 x64 six-EXE smoke, SHA256/Defender and
   accessibility evidence, premium gated distribution verification,
   independent QD and founder authorization. **Draft only; no release.**
