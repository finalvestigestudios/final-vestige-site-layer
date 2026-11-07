# R261 — prevent child-process escape from the offline runtime fence

**Status: DRAFT / QD + founder HARD HOLD.** Issue #73. Isolated branch `feature/labs-r261-offline-child-process-fence-20261107` stacks on R260 [draft PR #1434](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1434) at immutable SHA `faa4168170590fb745b69cb1fb4c90c34081ebc0`, not production `main`.

## Threat and change

The R260 socket/DNS/urllib Python audit guard is **per-interpreter**. A Python application could nevertheless invoke a shell, command interpreter, browser handler, another Python interpreter, or fork a child; the new process might make network connections without the parent's audit hook. Financial client data could thus cross a process boundary despite the socket fence.

The existing, verified pre-GUI `install_offline_guard()` audit hook now additionally rejects these CPython audit events: `subprocess.Popen`, `os.system`, `os.spawn`, `os.posix_spawn`, `os.exec`, `os.fork`, `os.forkpty`, `os.startfile`, and `os.startfile/2`. That covers common Python-origin child-process and Windows shell/file-association launches. Both free and premium launchers already use the shared hook; there is **no premium, loopback, or diagnostic bypass**.

Rejections use a constant `PermissionError("External process launch is disabled for Final Vestige Labs")`. Audit arguments are never interpolated into errors or logged. The existing fixed network denial, startup verification, idempotence, local source file writes, decimal math, report provenance, offline license validation, and human-only compliance decisions are unchanged. Original financial input files are never modified by this guard.

**Boundary:** A CPython audit hook is **not an OS sandbox** and cannot constrain untrusted native extensions, code that bypasses audit events, processes launched before installation, or unrelated desktop applications. It does not eliminate the need for Windows Defender/EDR, packaging review, or OS-level network isolation tests. Direct `fvs_suite.app` imports that skip the packaged six-app launcher are outside this installation path. Native Windows `os.startfile` behavior is covered only by event simulation here, not actual Windows execution.

## Measured local verification — 2026-11-07

Testing used local **Linux CPython 3.13.5**, synthetic paths/data, and source files whose Git blob hashes match the GitHub branch. Each test's subject installs the real hook in a fresh interpreter to avoid contaminating other tests. The parent unittest runner is outside the guard.

```sh
cd products/desktop
python -W error -m unittest discover -s tests -p 'test_offline_process_r261.py' -q
# 13/13 PASS
python -OO -W error -m unittest discover -s tests -p 'test_offline_process_r261.py' -q
# 13/13 PASS
python -m compileall -q fvs_suite tests
# PASS
```

**Total: 26/26 focused executed test methods** (0 skipped). Covered actual `subprocess.run` (temporary-file marker never created), pre-imported `Popen`, actual `os.system`, `os.spawnv`, `os.posix_spawn`, `os.execv`, `os.fork` on supported Linux, nine audit-event names including Windows `os.startfile` variants, denied socket creation, local `Decimal`/file I/O, re-installation, permitted unrelated events, and `--version` dispatch. The POSIX-specific cases do **not** establish Windows behavior.

| Tested file | Identical branch Git blob SHA-1 |
| --- | --- |
| `fvs_suite/offline_network.py` | `977740eca1b7273823cfe776dbf1257636d4a9a4` |
| `tests/test_offline_process_r261.py` | `e8c4c29d5f97a754d73a5b39d30002de83f4b4bc` |
| Unchanged `fvs_suite/launcher.py` | `c5ff50b3e6ba2b96ff68a997f4a947ac6de0a35b` |

**Limitations:** This was a focused, isolated source-test environment (actual committed guard/launcher, no real financial engine, GUI, network request, customer data, or packaged EXEs). Whole-repository normal/-OO tests, GitHub Actions Ubuntu/Windows jobs, actual Windows 11 x64 six-launcher smoke tests, malware/accessibility and protected premium distribution are **not verified**.

## Blocker and next highest impact

R260 [Actions run #42389415491](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42389415491) failed before verifiable steps in **both** Ubuntu and Windows jobs; runner names and logs are unavailable. Cause unconfirmed. Inspect repository Actions billing/usage restrictions, workflow policy/permissions and runner allocation; restore runner execution and rerun the unchanged R261 PR head, requiring actual step logs.

Then run the complete six-app test suite in normal and `-OO` mode; verify child-process/network denials on real Windows 11 x64, privately build/checksum/malware-scan and smoke-test six executables, test keyboard/NVDA accessibility, verify premium authenticated delivery, and require independent QD plus founder release authorization.

**RELEASE HARD HOLD:** All six utilities remain **UNRELEASED**. No production branch, public site, payment product, unrestricted premium payload, public download or Windows executable was changed or published.
