# R465 — Real six-product engine integration coverage in offline gate (DRAFT / HOLD)

## Gap closed in the source gate

R464 repaired missing self-tests in the isolated offline runner, but its eight mandatory Python modules covered CSV serialization, receipt/digest custody, and verifier self-tests. It did **not directly execute any six-product business engine/CSV integration modules**. A source-only "green" result could therefore lack real ledger, invoice, spend, policy, grant, and procurement end-to-end regression evidence.

R465 makes **six existing, genuine full-repository integration suites** mandatory alongside the eight existing verification modules:

| Product | Existing integration suite | Declared `test_` methods |
| --- | --- | ---: |
| LedgerDiff Lite (free) | `test_ledger_source_engine_integration_r62.py` | 9 |
| Invoice Twin Scout (free) | `test_invoice_source_engine_integration_r63.py` | 10 |
| SpendMap Lite (free) | `test_spend_engine_integration_r59.py` | 7 |
| Policy Delta Desk (free) | `test_policy_engine_r26.py` | 4 |
| GrantAudit Studio Pro (premium) | `test_grant_input_integration_r66.py` | 5 |
| ProcureGuard Studio Pro (premium) | `test_procurement_integration_r5.py` | 10 |

These six GitHub source files contain **45 declared unittest methods**, or **90 expected executions** across normal and optimized Python. The counts are source-code inventories, **not executed test passes**.

## Runtime contract

- `CORE_TESTS`: eight previous source/audit modules, unchanged in content; `PRODUCT_TESTS`: exactly the six existing integration modules above.
- `TESTS = CORE_TESTS + PRODUCT_TESTS`: 14 unique named files. Runtime refuses missing/duplicate/shortened module inventories before accepting a result.
- Each of the 14 unittest files must discover and pass **at least one test** in normal and `python -OO` modes, producing **28 successful process receipts**. Failed process, zero/partial methods, skipped tests, malformed/private receipts or a count other than 28 is HOLD.
- Each of those six product-test sources joins the descriptor-verified pre/post SHA-256 source fingerprint. The full R408 six-app import-tree digest and 12 launcher source-smoke outcomes remain mandatory. Changes during testing or smoke checks invalidate evidence.
- The six suites use synthetic local files, actual engine imports, and real CSV/policy/report creation or validation. Neither suite is a native Windows x64 executable or a paid entitlement test.

Existing CI jobs already execute `python -B products/desktop/offline_regression_gate_r459.py` in the independent source-evidence and Windows pre-packaging workflows. No production workflow, license, payment, WordPress, download or executable publication is changed by R465.

## Reproduction against a trusted complete checkout

```bash
python -W error -m unittest discover -s products/desktop/tests -p 'test_offline_regression_gate_r459.py'
python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_offline_regression_gate_r459.py'
python -W error -m unittest discover -s products/desktop/tests -p 'test_source_digest_binding_r461.py'
python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_source_digest_binding_r461.py'
python -B products/desktop/offline_regression_gate_r459.py
```

Successful full-gate output must include `regression_mode_runs:28`, `launcher_source_smokes_passed:12`, `evidence:SOURCE_ONLY_NOT_WINDOWS_BINARY`, and `release_authorized:false`. It must exit nonzero on incomplete runs. Run this against the actual branch/commit, never a reconstructed code projection, before claiming integration success.

## Evidence / no-release boundaries

At patch creation the R464 exact-commit [source run #43796255360](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43796255360) and [Windows build run #43796255491](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43796255491) had both failed before test steps. This environment can read and commit through the GitHub connector, but cannot fetch the private repository into the local interpreter to run its complete tests; GitHub's job annotations endpoint is not exposed through that connector. Static inspection of the six test files and the patched source **does not equal a passing test**. Record actual R465 Actions results separately.

The suite remains DRAFT/HOLD. No official Windows x64 builds, Defender scans, installed-binary/accessibility checks, premium access-control validation, QD approval, founder approval or live download verifications have been completed here.

**Next highest-impact action:** restore GitHub Actions runner assignment (review check failure annotations, Actions policy and billing eligibility), then execute both R465 exact-commit workflows. Resolve any real six-engine regression failures before native Windows packaging and independent QD review.
