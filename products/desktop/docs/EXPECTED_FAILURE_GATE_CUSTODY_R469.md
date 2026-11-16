# R469 — expected-failure custody in the six-app offline regression gate

**DRAFT ONLY · QD/founder release HOLD.** Stacked on R468, not production `main`. Applies to the source verification used for LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro.

## Reproducible false-positive condition

Python `unittest.TestResult.wasSuccessful()` can be true with a nonempty `expectedFailures` collection. Before R469, `offline_regression_gate_r459._TEST_CHILD` accepted those cases when `testsRun == countTestCases`, `skipped == 0`, and there were no ordinary errors/failures. An `@unittest.expectedFailure` that still fails could therefore satisfy one of the six product method floors, appearing among reported `regression_methods_passed`. The old fixed JSON receipt did not encode expected-failure counts.

## Code and regression changes

The existing isolated normal / `-OO` child now requires **both** `not result.expectedFailures` and `not result.unexpectedSuccesses` in addition to its existing `wasSuccessful()`, exact count, and no-skip requirements. A nonzero child exit already fails closed in the parent before a receipt is counted. Receipt schemas, source SHA-256 binding, test-identity parity, per-product floors (9 / 10 / 7 / 4 / 5 / 10), the 28 mandatory module/mode invocations and 12 launcher source outcomes are not weakened or changed.

Four added `test_offline_regression_gate_r459.py` regression methods exercise the production child through real isolated Python subprocesses. They cover: an expected failure rejected in both modes; an optimized-only expected failure with unchanged test identity SHA and count; one expected failure attempting to fill the full LedgerDiff Lite integration floor while all 14 modules exist; and an unexpected success remaining a HOLD.

## Evidence, boundaries and reproduction

During R469 development, a **local isolated Linux harness copying the branch's `_TEST_CHILD` source** executed six tests in standard mode and six tests under `python -OO -W error`: **12/12 probe methods passed**, confirming clean-pass acceptance and rejection of expected failures, unexpected successes, skips and normal assertion failures. These are **not the committed full-repository regression tests**, not a native Windows build, and not independent six-app launch validation. No customer data was used.

From an authorized full repository checkout, execute:

```bash
python -B -W error -m unittest discover -s products/desktop/tests -p test_offline_regression_gate_r459.py
python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_offline_regression_gate_r459.py
python -B products/desktop/offline_regression_gate_r459.py
```

To accept a release, also run all six application suites in both modes, the actual Windows x64 build and installed-app smoke/accessibility checks, Defender scans, checksums and premium entitlement-gating validation. There are no executables or distribution links in this sprint.

## Known blocker / smallest unblock

At R468, GitHub Actions runs [source evidence #43821689991](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43821689991) and [Windows internal build #43821689873](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43821689873) completed with failures **before any job steps were recorded**. Root cause unverified. Repository Actions administrator: inspect a job's failure annotation in the GitHub UI, confirm billing/spending and runner eligibility/policy, restore runner assignment, then rerun both workflows against R469's **exact commit**. Do not merge or distribute without independent QD review and explicit founder approval.
