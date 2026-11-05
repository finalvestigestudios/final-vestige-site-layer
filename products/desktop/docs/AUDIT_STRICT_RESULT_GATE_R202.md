# Final Vestige Labs R202 — strict pass-only audit regression gate

Status: **DRAFT / HARD RELEASE HOLD**. Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked only on R201 draft #1041 at exact parent `803365c1ec8dab76f98e8cd007df68469a791a9c`, never production.

## Defect and repair

The existing private R200/R201 runner considered a suite successful when **some** tests were skipped, even if the mandated minimum discovery count was met. Python's `unittest.TestResult.wasSuccessful()` is also true when tests have `@expectedFailure` outcomes. Thus a required audit regression could stop passing while the CI gate stayed green. A test raising `KeyboardInterrupt` or `SystemExit` bypassed the runner's `except Exception` guard, with a potential Python traceback exposing private synthetic fixture content.

R202 makes every audited case a genuine pass requirement: any skipped test, expected failure, unexpected success, failed assertion, error, incomplete execution or below-minimum count results in **HOLD**. It catches `BaseException` around test discovery/execution and replaces private exception text with static HOLD output. The six audited selectors remain unchanged (R194–R199, **148 minimum cases per Python mode**). The runner never loads customers' data, uploads reports or makes compliance decisions.

The R201 partial-skip test is updated to require HOLD, while keeping skip reasons private. Two platform jobs now run 17 additional synthetic strict-result tests in both normal and optimized Python modes before executing the 148-case matrix.

## Local reproducible verification

Environment: Linux, CPython **3.13**, local isolated working copy of the exact connector-retrieved R201 runner and inherited R200/R201 tests. Synthetic temporary files only.

- `PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_recent_regression*'`: **50/50 PASS** (16 R200 + 17 R201 + 17 R202).
- `PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_recent_regression*'`: **50/50 PASS**.
- **Total: 100/100 focused local test executions**, zero skips, and Python module compilation succeeds.
- Git blob SHA-1 identities of locally tested files: runner `7b118cf827eefaa7c57f8bfd3f186bf8eb0c1315`, R201 tests `0e0325eb3a8be8d9a86af2f20b7a3599c147bf40`, new R202 tests `3e30ad6708cdc15bdb350dadd4e15a6eeb22eb1d`.
- Red-phase baseline confirmed a mixed skip or expected failure could yield a passing result. An interrupting synthetic test propagated an uncaught traceback on the prior runner. **Do not treat previous CI as passing these new cases.**
- Workflow placement inspected: source-tests (Ubuntu) and windows-build (PowerShell, explicit `$LASTEXITCODE`) run normal and `-OO` R202 tests.

## Limits / conservative interpretation

These are focused synthetic runner tests, **not** the full inherited six-app suite or Windows executable evidence. The R197 real-file symlink test can `skipTest` when a platform forbids symlink creation: under R202 that becomes an intentional HOLD; supply executable native-Windows symlink acceptance evidence or revise the specific test only after independent QD assessment. Do not silently downgrade the strict gate.

Python stdout/stderr are suppressed during test execution; native fd writes or independent subprocesses remain outside the guarantee. No premium binaries, unrestricted downloads, public URLs, production edits, signed executables, malware scan, physical Windows 11 accessibility acceptance, or QD/founder authorization are claimed.

## Next high-impact step

Restore GitHub Actions runner execution (both Ubuntu and Windows previously failed before step 1, cause unconfirmed), rerun the **unchanged R202 head** and inspect any legitimate platform skip. Run the full inherited suite and then produce sealed/private six-app Windows x64 build, hash, malware-scan and native smoke evidence. Keep draft PR and QD workflow; **no merge/release** absent explicit approval.
