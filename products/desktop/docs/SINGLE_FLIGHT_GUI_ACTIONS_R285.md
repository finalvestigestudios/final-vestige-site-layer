# Labs R285 — single-flight Generate / premium Review (DRAFT / QD HOLD)

**Issue:** #73. Six standalone Windows x64 desktop utilities (four free, two premium). **Stack:** R285 branch based on immutable R284 commit `de47ba18a96cafe273c779af972a39b7b035b7f3`; not production `main`.

## Failure mode and engineering change

R284 prevents *duplicate keyboard bindings*, but Tk can enter nested event loops while a Generate or Review command is still running (for example, during a modal dialog). A second queued button or keyboard command could otherwise start a second financial export, start another review window, or run Review while report generation is incomplete. Tk's command dispatch is generally synchronous but nested event processing means synchronous dispatch alone is not a sufficient single-flight guarantee.

R285 adds a per-application-window `ActionGate`, shared by the existing Generate and (for premium apps) Review buttons. The first invocation holds the gate through successful completion or failure; nested and cross-action dispatches return False without calling a second business action or queuing one for later. A `finally` clause releases the gate after any exception. The gate is created once per UI window; separate windows never share state. Original entitlement validation, human-review logic, deterministic engines and file write paths are untouched.

## Verification and scope

The new `test_action_gate_r285.py` executes **24 real Tk/ttk widget methods** covering all six app configurations: nested Generate, nested Review (premium), scheduled Tk event reentry, exception release and separate-window gate isolation. On Linux Python 3.13.5 + Xvfb, all **24/24 passed** in normal mode and **24/24 passed** with `-OO` (**48 focused test-method executions**). `python -m py_compile` on the new helper and test passed. The tested local Python modules match the committed Git blob SHA IDs:

- `fvs_suite/action_gate.py`: `d654d60da5791002a7bcb71877babbe7c55e74f1`.
- `tests/test_action_gate_r285.py`: `31d9e230bf715fe6ac38eb70289c450039ffa219`.

CI workflow adds the same two-mode tests under independent Ubuntu+Xvfb source-tests and Windows native Tk jobs. **These focused tests use synthetic callbacks and real Tk buttons; they are not a complete application GUI integration test, a full repository regression pass, or Windows EXE verification.** There is no claim of real financial output being generated in this local test.

## Required acceptance / hard hold

No production branch writes, product packaging or site changes. No binaries, public downloads or unprotected premium files. All six apps remain **UNRELEASED**. Complete repository regressions and private Windows 11 x64 executable smoke, SHA-256 verification, Defender scan, keyboard/screen-reader review, premium download gate and independent QD/founder approval must pass before merging or public release.

**Known infrastructure blocker:** GitHub Actions for R284 [run #42498017540](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42498017540) failed with zero recorded job steps on 2026-11-08; infrastructure root cause unconfirmed. Review Actions spending/billing, workflow permissions and runner allocation, then rerun the exact R285 head.

**Next highest-impact step:** execute the complete existing test suite and unmodified, private six-app Windows x64 candidate workflow on a trusted Windows 11 x64 runner, preserve full build/scan/log evidence without publishing installers, and clear QD/founder hold only after review.
