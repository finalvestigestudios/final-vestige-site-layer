# R341 — six-app release verifier CLI fault privacy

**2026-11-10 · DRAFT / independent QD + founder HARD HOLD.** This is a source-only privacy correction to the offline verification gate shared by LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro. The draft branch is stacked on the exact R340 head `ffca61424a7fdc4cdd8d267bcaee604370cdb99a`, NOT on production `main`.

## Reproduced defect and scope

The old `release_gate.main()` grouped raw `OSError` with known-safe domain exceptions and printed `str(exc)` on stderr. A filesystem failure during candidate checking could therefore print a private path from a customer-controlled directory, for example a permission-denied exception naming `C:/PRIVATE_CLIENT_PAYROLL_2026/ledger-secret.csv`. An unexpected `RuntimeError` in report-preflight, candidate verification, or publication was uncaught, potentially emitting a traceback and private paths. The R340 report publisher's narrower fault redaction did not secure this CLI-level boundary.

**R341:** domain-controlled `GateFailure` and `ReportEvidenceError` still produce their existing actionable messages. Raw `OSError` (including `PermissionError` and `FileNotFoundError`) and `RuntimeError` are converted to the fixed line `REJECTED: Candidate verification could not be completed safely`, exit 1, without formatting the raw exception. Synthetic `KeyboardInterrupt` and `SystemExit` still propagate. The change does not approve, sign, download, execute, scan, or distribute any EXE; it does not touch the financial engines, cryptography, WordPress, premium rights, or QD rules.

## Regression evidence — exactly what was executed

- **New source:** `products/desktop/tests/test_release_gate_cli_privacy_r341.py` (Git blob `9661cad843a7a64b89a32e7a757cac29cb415384`), 18 cases. Covers OS faults at preflight/verification/publication, uncaught runtime failures, chained private causes, malicious `__str__`, no publication after verification failure, no smoke after report-preflight error, preservation of specific *safe* domain errors, interrupt behavior, and normal nonauthorization output.
- **Repro:** Against an isolated local copy of the exact **R340 CLI control flow**, new tests reported **10 failures and 3 errors** (18 total). Prior OSError text was leaked or hostile `__str__` triggered; RuntimeErrors were uncaught.
- **Fix check:** Linux CPython **3.13.5** isolated local harness of the revised CLI control flow: **18/18 PASS** with `-W error`, **18/18 PASS** with `-OO -W error` = **36/36 focused executions**, no skips; compilation PASS. The 18-test source was SHA/blob-identical to the committed Git file (local `git hash-object` = `9661cad843a7a64b89a32e7a757cac29cb415384`). Only the CLI control flow and mocked side effects were executed locally: **not a full private-repo test, and not a native Windows executable test**.
- **CI source:** `.github/workflows/desktop-build.yml` now requires these 18 cases in both modes for Ubuntu and Windows jobs, before candidate packaging. Hosted CI confirmation is pending infrastructure recovery.

## Release hold / owner action

Previously observed [R340 Actions #42919797961](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42919797961) completed **failure** with both Ubuntu and Windows jobs reporting no recorded steps or logs (2026-11-10). Their check runs report one inaccessible annotation each. No root cause has been verified. Owner should inspect GitHub Actions billing, spending caps, runner provisioning and workflow permissions, then trigger this draft PR's real Ubuntu and Windows tests; obtain complete private desktop suite including **22 genuine AES-GCM integration cases**. Only then privately build/smoke/Defender-scan/checksum and independently accessibility-test all six Windows 11 x64 binaries; gate premium downloads and require independent QD PASS + founder signoff before any release.

Do **not** interpret this sprint as a production merge, QD approval, signed executable, malware scan, Windows acceptance, or public download.
