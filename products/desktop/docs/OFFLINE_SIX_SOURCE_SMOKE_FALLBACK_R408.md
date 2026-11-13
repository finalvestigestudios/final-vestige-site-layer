# R408 — local six-launcher source smoke fallback (issue #73)

**DRAFT ONLY; source evidence, NOT a Windows release gate.** GitHub Actions jobs for R407 [source #43478734706](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43478734706) and [build #43478734715](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43478734715) failed before runner assignment (all four jobs had no steps). This fallback allows a trusted operator to obtain bounded, *offline* evidence for the **real six source launchers** while hosted CI is unavailable. It does not manufacture a CI result.

## Run in a trusted complete checkout

From repository root, using Python 3.12 with the project's required offline crypto dependencies installed:

```powershell
python -W error -m unittest discover -s products/desktop/tests -p test_offline_source_smoke_r408.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_offline_source_smoke_r408.py
python -I products/desktop/offline_source_smoke_r408.py
```

The final command launches `LedgerDiffLite.py`, `InvoiceTwinScout.py`, `SpendMapLite.py`, `PolicyDeltaDesk.py`, `GrantAuditStudioPro.py`, and `ProcureGuardStudioPro.py` with their existing `--smoke-test` source entrypoint in **normal and optimized Python**. Each runs in an isolated Python child, with standard input disabled, no shell, bounded timeout and captured/discarded stdout/stderr. Real launchers already install the offline network guard before their synthetic engine checks; the fallback does not disable that guard or grant premium entitlements. Only synthetic data from `fvs_suite.smoke` should be used, never customer data.

The last command emits a single JSON receipt containing **12 individual pass/fail statuses**, an SHA-256 inventory fingerprint of the suite Python source files, six launchers and fallback runner, and `release_authorized: false`. A missing, empty or symlinked required source file, incomplete inventory or source drift between checks is rejected. A failure or timeout is recorded as `fail` with a nonzero process exit; no private subprocess message, traceback or file path is printed. The source fingerprint is **not** a Git commit proof, cryptographic signature or binary identity. No file is uploaded automatically.

## Exact local test evidence / limitations (2026-11-13)

The new `test_offline_source_smoke_r408.py` contains **9 regression methods**. On local Linux with source and test files matching their exact Git blobs, `python -W error` passed **9/9**, and `python -OO -W error` passed **9/9** (**18 total methods**). The tests exercised twelve genuinely spawned *synthetic* Python launchers, source fingerprint stability/drift, missing/zero-byte/symlinked input, process failure and private text redaction, timeout, no-spawn preflight and safe subprocess flags. Python compilation passed. These are **not** full-checkout or actual financial engine tests; no native Windows test, standalone PE, Defender/EDR run, signing, screen-reader trial or premium distribution test was performed in this sprint.

The independent Windows/Ubuntu source-evidence workflow now invokes both R408 test modes **and the real twelve source-launcher smoke checks** once runners execute. Their outcomes are **unknown until a real runner runs them**. The GitHub Actions root cause is still unconfirmed; zero steps and no runner assigned are insufficient to prove a billing failure.

## Next action and release hold

Owner: inspect the GitHub Actions failure banner, spending/billing status and hosted-runner eligibility; restore runner allocation, then rerun exact R408 head on Windows and Ubuntu. An operator with a *complete trusted checkout* can invoke the three commands locally as a narrower immediate alternative, sharing only the fixed-status JSON and exit code. Once hosted source tests pass, run genuine six Windows x64 executables, Defender scans, NVDA/high-DPI acceptance, SHA-256/PE verification, protected premium distribution and independent QD review. **No executable may be published, no premium access control weakened, no website published, no production merge, and no release without explicit founder approval.**
