# R319 — Bind executed premium AES integration source to witnessed SHA-256

**DRAFT / independent QD and founder HARD HOLD.** Tracks desktop mandate #73. Parent is R318 draft #1825 at `123eb04e9cda8b145c3c3a4a458aaa0660c81e31`. No production, WordPress, catalog, premium binary, entitlement, money, or release changes.

## Actual defect closed

R317 snapshots each real AES-GCM integration test source's filesystem identity and SHA-256 before and after loading. R318 compiles Python source bytes directly rather than cached bytecode. However, R318's loader **re-read** source bytes independently of the witness; a transient modification **only during that second read** could execute passing or side-effect-bearing code while the earlier/later source checks still saw the original bytes. The source identity test and no-skips policy alone cannot catch this execution of unvetted bytes.

R319 passes the exact SHA-256 digest from the gate's earlier source witness into `load_source_suite`, compares it with a digest of the **actual bytes about to be compiled**, and fails before `compile`/module import on mismatch. Digest input is optional for legacy direct loader consumers but **mandatory at the production gate call site**. Native `bytes` of length 32 are required when supplied. The gate's privacy-safe fixed HOLD, exact four-module / 22 genuine-case inventory, source identity checks and no-skips contract remain in force.

This is source-test integrity, **not** a fix to AES-GCM, a new payment authorization, or evidence of Windows executable acceptance. The source and interpreter are not protected against malicious privileged local administrators; dependencies, sub-millisecond swaps of **byte-identical** content, compromised interpreters and live runner integrity remain out of scope.

## Changed paths

- `scripts/source_only_test_loader_r318.py`: compare SHA-256 of exactly the read-and-compiled source against the supplied witness before executing it.
- `scripts/vault_crypto_gate_r316.py`: forward `initial_witness[-1]` to loader.
- `tests/test_vault_source_digest_bind_r319.py`: ten adversarial synthetic methods, including same-size source changes, Unicode byte distinctions, wrong digest inputs, full gate call-site binding, transient false PASS, and blocked unwitnessed import side effects.
- `.github/workflows/desktop-build.yml`: add **explicit normal and `-OO` fail-closed R319 tests** to both independent Ubuntu source and Windows packaging jobs. The pre-existing full source gate remains mandatory.

## Executed reproducible evidence, Nov 9, 2026 Pacific

Linux CPython **3.13.5**, synthetic local temp files only, no financial records, no cryptography library or live binaries:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_source_digest_bind_r319.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_source_digest_bind_r319.py'
python -m py_compile products/desktop/scripts/{source_only_test_loader_r318,vault_crypto_gate_r316}.py products/desktop/tests/test_vault_source_digest_bind_r319.py
```

Result: **10/10 normal PASS, 10/10 optimized PASS (20/20 focused method executions)**; Python compilation passed. These tests imported the exact reconstructed R318 gate (original Git blob `05d1d973b51dd7d2730339636a01aa7fb97af2ff` verified locally) with only the one-line R319 digest-forwarding change. Exact locally executed Git blobs equal the source-controlled update: loader `2c16839d8cf58b9d7baf0e413cc7626ea332fd62`, gate `682f8d2a785a81e8aac6a21debc691312574b575`, and regression `9db5d41bf426f99bc659a50cc8d1e6851e4d9233`.

**Predecessor reproduction:** Reverting the gate's one-line digest argument while retaining the new optional-loader API makes `test_transient_swap_during_loader_read_fails_gate` fail with **"IntegrationHold not raised"**. Under the new gate it holds; another regression proves unverified import code cannot create a marker file. No real 22-case AES-GCM integration, full repository tests, hosted CI, or native Windows tests were executed during local reproduction.

## Blockers, governance and next highest-impact action

Latest inspected R318 Actions [#42739876335](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42739876335) completed failure; both Ubuntu and Windows jobs reported **null steps and logs**. The infrastructure cause remains unconfirmed. Restore GitHub Actions job scheduling (check billing/spending restrictions, permissions, and hosted runner eligibility) **or** run a trusted full private checkout locally with `cryptography` installed, execute all 22 genuine AES-GCM integration cases and full source suite, record sanitized signed test receipts, then perform private Windows 11 x64 six-EXE acceptance, SHA-256/Defender/accessibility and authenticated premium delivery validation.

**Never merge, publish, unlock premium files, announce downloads or declare six apps released without independent QD review and founder approval.**
