# Labs R486 — offline source receipt integrity (DRAFT / QD HARD HOLD)

## Scope and reproducible change

Stacked **only on R485 draft PR #2809**, parent commit `9525081cd4cbd19c038f182795f587696bc0dfa4`; this is not production `main`. Applies to the operator-run fallback source gate for the **six Windows x64 applications** (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro). No business logic, pricing, payment/license distribution, Windows executable, or WordPress production asset is changed.

R485 accepted `Ran N tests` and `OK` anywhere within only the final 16 KiB of a child log. A zero-exit simulated process with a malformed tail, trailing output, `OK (expected failures=1)`, or an earlier hidden `FAIL:` could be marked PASS. `all([])` also allowed empty check/mode configurations to report success. Symlinked test files/directories were followed before running the child.

R486:
- Requires exactly one unittest test-count summary, a 70-dash separator, a positive count, and an **unqualified terminal `OK`** (Linux/Windows line endings accepted); rejects skips, expected failures and trailing output.
- Scans **all** captured output for unittest failure markers rather than only the last 16 KiB. A spool exceeding **1 MiB after subprocess completion** is a FAIL and is not copied into JSON. This is an acceptance threshold, **not a hard disk-write limit**; a child can still consume disk before timeout. Use quotas/isolation for untrusted code.
- Refuses symlinked desktop/test directories and test files, treats OS/path errors as BLOCKED, and refuses empty check/mode lists.
- Preserves fixed-label private-path-free JSON, child credential/proxy scrubbing, explicit `release_authorized=false`, standard + `-OO` modes, and no automatic approval.

These checks improve evidence parsing, **not** cryptographic attestation of test provenance; malicious test code can still print plausible unittest output. Treat the repository checkout as trusted and independently verify actual source and release artifacts.

## Executed evidence (local Linux, Python 3.13.5)

Source/test files were reconstructed from the **exact R485 Git blobs**, then edited and tested locally. The parent source blob `d800d29245d551d0fbb1e2ed07919118e9298244` was independently reconstituted and hash-checked.

- `python -B -W error -m unittest discover -s . -p 'test_offline_source_gate*.py' -q` — **18/18 methods PASS**.
- `python -OO -B -W error -m unittest discover -s . -p 'test_offline_source_gate*.py' -q` — **18/18 methods PASS**.
- `python -m py_compile offline_source_gate_r485.py test_offline_source_gate_r485.py test_offline_source_gate_strict_r486.py` — **PASS**.
- The ten new methods include **real subprocess** positive and negative fixtures, exercising all eight configured child checks in each case. They are **synthetic** Python test modules, not the actual full six-app regression matrix.
- **Parent negative control:** the ten new regression methods against the exact R485 parent generated **11 failures**, reproducing the previously accepted forged receipts, empty-gate success and linked-fixture acceptance.
- Committed source blob `dcb6eb6f6392aa0e216ebddcf9b58ded9e3013d3`, adjusted inherited test blob `760f2f0b034775088a0e3b52198cba84aa956571`, new regression blob `ad9b3697131d5b110afce78ac4b576f504dd6b18`, all matched local executed files when written and read back.

New R486 regression file is explicitly wired into the independent source CI workflow for **ubuntu-24.04 and windows-latest**, normal and optimized. **Hosted CI has not executed these tests.**

## Acceptance / next action

From a full trusted checkout, with dependencies already installed, run `python -I products/desktop/offline_source_gate_r485.py > source-evidence-r486.json`. Exit 0 only indicates eight selected source checks passed and `release_authorized=false`; it does **not** certify any Windows EXE.

R485's exact-commit source Actions [#43992660539](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43992660539) and internal Windows [#43992660661](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43992660661) both failed with **four jobs showing `steps=null`**; the root cause is not verified. Administrator: inspect Actions account/runner/billing annotations and restore job step execution. Then run R486, the full six-app regression matrix, native Windows x64 packaging/smoke, Defender, SHA-256 manifest checks, physical accessibility, and premium entitlement/download gating.

**HARD HOLD:** No production merge, no public binaries/downloads, no unrestricted premium assets, no automated compliance approvals. Independent QD review and explicit founder authorization remain required.
