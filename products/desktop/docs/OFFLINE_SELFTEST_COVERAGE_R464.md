# R464 — offline verifier self-test coverage (source-only, release HOLD)

## Specific verified gap
The R459 independent offline fallback's `TESTS` manifest executed the R455–R458 financial CSV regressions and R461/R462 receipt/digest tests, **but omitted its own R459 source-fingerprint and R460 strict smoke-receipt regression modules**. Thus `python -B products/desktop/offline_regression_gate_r459.py` could return a successful source-only receipt while never executing those two high-trust validator suites. GitHub CI separately listed the suites, but its runners have repeatedly failed before test steps. This defect matters especially when the fallback is the only available engineering evidence.

## Actual changes in R464
1. The offline runner now executes **eight explicit real repository unittest modules**, once in normal Python and once in `-OO` (16 module/mode child subprocesses; previously 6×2=12). Both R459 self-tests and R460 source-smoke receipt tests are mandatory.
2. Its bounded, descriptor-attested `SOURCE_INPUTS` fingerprint now includes each of the eight test module files **exactly once**, rather than repeating the R459/R460/R461 test sources.
3. The parent refuses a claimed green receipt unless native integer `regression_mode_runs == 16` and native integer passing method count is at least 16. Zero methods, boolean/string/spurious counts, or a legacy 12-run outcome fail **before any source smoke is accepted**. Existing per-child exit, `tests == expected > 0`, no failure/error/skip, strict JSON, source-change and R408 digest binding remain mandatory.
4. Updated inherited R459 and R461 mocks/count assertions, and added **eight focused R464 regression methods** in `test_offline_regression_gate_r459.py`: exact test matrix, unique fingerprint, self-test edit sensitivity, rejected legacy coverage, missing methods, forged mode/method counts, and release HOLD.
5. Both the independent Ubuntu/Windows source-evidence workflow and Windows pre-packaging workflow now run the actual R459 offline end-to-end fallback (not merely individual unit modules). A successful source-only gate never approves Windows binaries.

## How to execute against a complete authorized checkout
```bash
python -W error -m unittest discover -s products/desktop/tests -p 'test_offline_regression_gate_r459.py'
python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_offline_regression_gate_r459.py'
python -W error -m unittest discover -s products/desktop/tests -p 'test_source_digest_binding_r461.py'
python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_source_digest_binding_r461.py'
python -B products/desktop/offline_regression_gate_r459.py
```
The last command requires a complete local checkout and executes eight test modules in two isolated modes, then six real launchers in both modes. It emits only a bounded source-only verification receipt; source files are read without destructive writes or external customer data. The expected success fields include `regression_mode_runs:16`, `launcher_source_smokes_passed:12`, `evidence:SOURCE_ONLY_NOT_WINDOWS_BINARY`, and `release_authorized:false`.

## Evidence and release policy
The modifications are committed to an isolated feature branch stacked on R463's draft PR; there is **no merge to main**. At authoring time the earlier R463 exact-head Actions jobs had failed with zero execution steps (source workflow run 43790217919; Windows internal run 43790217959), so **this documentation does not claim a complete checkout unit pass or native Windows x64 build**. Any local focused projection or static audit is not production or integration evidence.

No changes to the six applications' Decimal money, source data, offline/privacy posture, compliance human review, premium entitlement, or financial report rules. No installer, executable, license, premium URL or WordPress publication is authorized. Independent QD review and explicit founder approval are mandatory.

## Next highest-impact verification
Repository owner reviews GitHub Actions job-level failure annotations and checks billing/spending limits, Actions policies, and runner eligibility. Re-run source and Windows workflows on the **exact R464 commit**. If hosted CI remains blocked, an engineer with a trusted full checkout runs the above commands and attaches their raw exit codes plus the **redacted source-only JSON**. Only after genuine full-source success: native Windows x64 packaging and installed app smoke, Defender scanning, accessibility, SHA256 checksums, premium download/entitlement verification, QD and founder review. 
