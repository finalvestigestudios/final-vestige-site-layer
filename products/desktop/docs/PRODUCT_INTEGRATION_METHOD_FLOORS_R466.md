# R466 — Per-product integration method floors and normal/-OO parity

**Status: DRAFT / QD HARD HOLD.** This is source-only verification, not an executable-release approval.

## Failure closed

R465 made six actual integration modules mandatory, but `_run_tests` only required **one** discovered unittest method per module. Six reduced one-test placeholders could pass the 28-child gate while the real application tests disappeared. Also, an optimized run could discover fewer tests than its standard run without triggering a rejection if all discovered tests passed.

R466 enforces the methods already declared in the checked-in six modules:

| Product | Module | Minimum methods per Python mode |
| --- | --- | ---: |
| LedgerDiff Lite | `test_ledger_source_engine_integration_r62.py` | 9 |
| Invoice Twin Scout | `test_invoice_source_engine_integration_r63.py` | 10 |
| SpendMap Lite | `test_spend_engine_integration_r59.py` | 7 |
| Policy Delta Desk | `test_policy_engine_r26.py` | 4 |
| GrantAudit Studio Pro | `test_grant_input_integration_r66.py` | 5 |
| ProcureGuard Studio Pro | `test_procurement_integration_r5.py` | 10 |

These are **45 required product test discoveries per mode, 90 across both** (not 90 observed passing results). Each of 14 modules must report identical positive unittest counts across normal and `-OO` modes; all methods must pass without skips/errors. Adding tests remains allowed. Missing or depleted suite, mode discrepancy, bad receipt, missing source, source mutation or incomplete smokes stays HOLD.

The source-only receipt continues to report `release_authorized:false`. No financial data, licensing, executables, publication or production approvals are changed.

## Reproduce after restoring an authorized full checkout/runner

```bash
python -W error -m unittest discover -s products/desktop/tests -p test_offline_regression_gate_r459.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_offline_regression_gate_r459.py
python -B products/desktop/offline_regression_gate_r459.py
```

The newly added five tests cover all six shortened product suites, standard/optimized method-count mismatch, expanded suites, floor manifest tampering, and declared count mapping. The existing synthetic child test now writes the same minimum methods as the actual product suites.

**Release gates still missing:** full checkout execution, true Windows x64 packaging, installed-application smoke, Defender, accessibility, checksums, premium access controls, independent QD review and founder approval. No executables or download links may be published before those gates pass.
