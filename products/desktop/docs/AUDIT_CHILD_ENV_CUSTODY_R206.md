# R206 — Audit child environment custody (DRAFT / HOLD)

Tracks issue #73. Stacked on R205 draft PR #1067 (exact parent commit 0c77387f4a78f40d77d5e935d175b162a38dc360), **not** main/production. No accounting formulas, compliance decisions, shipped files, release locations, or entitlement rules change.

## Reproduced defect and change

R205 isolated the strict R194–R199 financial/policy audit matrix's stdin/stdout/stderr at OS-descriptor level, but subprocess.run() **implicitly inherited the entire CI environment**. Python's -I prevents interpreter use of PYTHONPATH, but does **not** remove sensitive entries from os.environ visible to imported tests or their subprocesses. A synthetic GITHUB_TOKEN/cloud credential canary was readable inside the child before R206.

R206 explicitly supplies env=_child_environment() to subprocess.run. This is an **allowlist**, not a blocklist: only PATH, PATHEXT, SystemRoot, WINDIR, TEMP, TMP, and TMPDIR (case-insensitive names for Windows) are forwarded. It excludes CI tokens, license secrets, cloud credentials, proxy credentials, Python overrides, home/profile variables and arbitrary unknown keys. It preserves normal/optimized -OO behavior, absolute Python executable, source preflight, existing DEVNULL output isolation, strict returncode/HOLD, and local temporary-file use.

This mitigates accidental inherited environment-secret exposure; **it is not sandboxing**. Tests can still read repository files, invoke network calls, or use credentials embedded in the allowed PATH/TEMP values or files. CI must not load real customer financial data or secrets into test fixtures; separate workflow token permissions and network policy should be assessed independently.

## Local execution evidence

Linux CPython 3.13.5, isolated local copy matching the exact R205 GitHub 14-test regression blob 07d6b38c05222590c74a3cc4431b5b5fbaee4b59 plus R206 files. Runs:

- Before patch, R206 eight initial tests: **2 failures + 1 error**, demonstrating inherited token visibility and absent explicit env contract.
- After patch, **12/12 R206** and **14/14 inherited R205** in ordinary Python = **26/26 PASS**.
- The same **26/26 PASS** under Python -OO = **52/52 focused passing executions**; zero skips.
- Python compilation: PASS.
- R206 patched wrapper and test Git blob hashes matched local execution: wrapper 6197180b4a607dd5af54d1b031ab9406630767b0; test c397b9e90e1323aba5bfba06a9c7e4d1a72ee26c.

The new cases run actual Python child processes to witness no inherited CI tokens, protected exception output, PATH/TMP and native tempfile survival, Windows-style launch variable preservation (mocked on Linux), case-folded secret filtering, -OO propagation, absolute interpreter execution, and explicit subprocess env.

Both source-tests (Ubuntu) and windows-build (Windows) jobs now invoke 12 R206 tests in ordinary and optimized modes **before** launching the existing protected six-suite matrix. Windows checks LASTEXITCODE after each command. Workflow wiring is not execution evidence.

## Not verified / acceptance HOLD

Full inherited R194–R199 148-case matrix, actual hosted Ubuntu/Windows execution, native Win11 environment/path compatibility, x64 EXEs, Defender scans, checksum/signature, keyboard/Narrator/NVDA/high-DPI accessibility and premium entitlement protection are **not verified**. On R205 parent, Actions #41999756449 failed with no job steps available; infrastructure cause remains unconfirmed. GitHub owner must inspect Actions billing/allowance, permissions, runner provisioning and failure banner, then run unchanged R206 HEAD on both platforms.

Release is **HARD HOLD**. No main/production merge, public downloads, ungated premium artifacts, payment auto-approval or website publication. Independent QD evidence and founder approval are mandatory.

## Next highest-impact action

Restore hosted CI, execute the unchanged R206 branch's full inherited strict regression matrix on both OSes, resolve any cross-platform environment dependency **without reintroducing blanket env inheritance**, then privately build and verify all six Windows x64 candidates and premium access controls.
