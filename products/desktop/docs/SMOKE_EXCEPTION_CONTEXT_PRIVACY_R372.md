# Labs R372 — release-smoke exception-chain privacy (DRAFT / QD + founder HOLD)

## Scope
Applies to the shared Windows x64 release verifier for **all six** apps: free LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite and Policy Delta Desk; premium GrantAudit Studio Pro and ProcureGuard Studio Pro.

Prior R336/R371 smoke execution already used no inherited secret environment, discarded stdout/stderr, required a real integer zero exit status, and redacted human-visible fault strings. The remaining defect was **programmatic**: `raise SmokeRunError(...) from None` inside an `except` suite only suppressed *display* of a preceding exception. Python still retained the underlying `TimeoutExpired`, `OSError`, `SubprocessError`, or malicious `returncode` getter failure in `SmokeRunError.__context__`. Those original exceptions may contain private client paths, subprocess commands, or output bytes. A downstream logger/diagnostic that traverses `__context__` could expose them.

## Code change
In `smoke_runner_r336.py`, classify subprocess timeout versus other launch failures, **leave the exception handler**, and only then construct `SmokeRunError`. Treat a failed `returncode` property read as an invalid result without re-raising from the active handler. This makes normal boundary failures have both `__cause__ is None` and `__context__ is None` while preserving the existing outward error messages, normal/nonzero exit semantics, exact-int checks, private child env, timeout limit, no stdout/stderr, and propagation of `KeyboardInterrupt`/`SystemExit`.

No exception details, private paths, commands, or output bytes are logged or written to evidence. This is a Python exception-custody fix, **not** an OS sandbox or a security guarantee about running untrusted executables.

## Reproduction and local evidence
- Synthetic isolated Linux Python reproduction against original R371-equivalent smoke runner: **7 failing cases of 11** because `SmokeRunError.__context__` retained prior failures (timeout, OS, subprocess, runtime, environment construction, returncode accessor, missing returncode). Four control cases passed.
- Updated isolated copy: **11/11 PASS** `python -W error -m unittest -v test_privacy_r372.py` and **11/11 PASS** `python -OO -W error -m unittest -q test_privacy_r372.py`; `compileall` passed. These tests use **synthetic canaries only**, not customer data or a Windows executable.
- Committed **11 additional tests** to the existing `products/desktop/tests/test_smoke_runner_r336.py`; this test module is already required by the existing desktop GitHub Actions workflow on Ubuntu and Windows in both normal and `-OO` modes. No workflow edit needed.
- Distinguish **locally executed isolated reproduction** from the **committed full 32-test module**, which has **not yet been run** on an exact-head full checkout. Local copy was assembled from source snippets and was not checked against a Git blob hash. Do not claim a verified whole-repository pass.

## CI/release hold
R371 parent [Actions run 43165351901](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43165351901) completed failed: both `source-tests` and `windows-build` had `steps=null`; no test execution evidence. The cause remains unconfirmed. An R372 run must be inspected separately.

**Smallest owner action:** inspect GitHub Actions failed-check annotations, billing/spending limits, and eligible runner provision; restore job step dispatch and rerun this exact branch's Ubuntu/Windows tests.

**Next acceptance:** exact-head inherited desktop regressions including 32 R336/R372 test cases, genuine 22 AES-GCM cases, six Windows 11 x64 executable builds/smokes, PE/SHA checks, Defender scan, keyboard accessibility, premium entitlement/access-controlled distribution, QD and founder review.

**Release authorization:** none. All six apps remain UNRELEASED; no production changes, downloads, unrestricted premium files, approval bypass, or automatic compliance/payment decision.
