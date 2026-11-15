# R459 — CI-independent six-app source regression fallback (DRAFT / release HOLD)

**Issue #73.** GitHub-hosted Ubuntu/Windows jobs associated with R458 failed before any steps executed. This source-only fallback allows an engineer with the **complete checked-out R459 branch** to run real, committed Python regression tests and all six source launchers while Actions runner service is blocked. This is not a replacement for the mandated Windows x64 native release process.

Run from the repository root on an ordinary Python 3 environment:

```sh
python -B products/desktop/offline_regression_gate_r459.py
```

The gate launches exactly eight isolated interpreters: `test_csv_negative_decimal_zero_copy_r455.py`, `test_csv_safe_cell_zero_copy_r456.py`, `test_csv_incremental_render_budget_r457.py`, `test_csv_bounded_utf8_witness_r458.py`, each under both standard and `-OO`, all with `-I -B -W error`. It **requires nonzero discovered methods, zero errors/failures/skips, and the exact discovered run count**. A child writes only a tiny private structured test-count receipt. Parent emits no user paths, untrusted exceptions, or test logs. It then invokes the existing R408 six-launcher offline source gate to require **12/12 real source smokes** (normal and optimized for LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro). The combined gate verifies a bounded fingerprint of its input scripts and source files before/after testing, and fails closed if any change is observed. Tests and smokes are strictly local with no network, telemetry, or client-file input; only synthetic samples within the existing source smoke are used.

The JSON receipt reports source-only status, count of **actually executed** regression methods, 8/8 mode runs, 12/12 launcher smokes and a deterministic SHA-256 fingerprint; it always sets `release_authorized: false`. A passing receipt is not a signed provenance attestation, nor any evidence that a Windows binary was actually produced or scanned. The 18 focused R459 unittest methods under normal and optimized modes use synthetic fixtures to enforce no false 0-test pass, fail-closed subprocess statuses, redaction, fixed input inventory, source-change rejection and exact invocation. Full R455–R458 module integration and six-launcher real source execution remain **unverified in this engineering environment** until the runner is actually executed against a complete checkout.

## Release blockers and QD hold

1. Have a permitted engineer with a complete checkout run the command above and attach its **actual** JSON receipt; do not infer a pass from this document or the synthetic runner tests. A nonzero exit means HOLD, not partial success.
2. Restore GitHub Actions runner assignment; inspect the failure annotations in the repository UI and check Actions billing/spending limits, runner eligibility, and organization policies. Re-run exact-commit Ubuntu and Windows CI once available.
3. Complete the inherited six-app automated tests, native Windows x64 build/installation/smoke, Defender/EDR, screen-reader/keyboard/accessibility, signing/unsigned disclosure, SHA-256 checksums, and private premium entitlement/distribution verification. Obtain independent QD review and explicit founder approval before any production `main` merge, site change, or public/premium download.

**No production, WordPress, binary, license, premium URL or release action is authorized by R459.**
