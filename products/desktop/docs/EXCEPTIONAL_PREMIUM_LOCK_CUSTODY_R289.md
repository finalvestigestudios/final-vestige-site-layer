# R289 — premium review-lock exceptional-exit descriptor custody

**Status:** DRAFT; issue #73; stacked on immutable R288 head `bea2bcd8ccffaca8b8a5b20cea161e137996b2be`. Independent QD/founder **HARD HOLD**. No changes to production, payment, premium distribution, or released executables.

## Reproduced defect

The R288 premium review-journal lock checks its *live descriptor* following the `yield` only when the caller exits normally. If a caller raises an exception or is interrupted, that check is bypassed, and the `finally` block may unlink the lock based solely on its apparently unchanged pathname. With synthetic `os.fstat` failure or descriptor metadata drift, the original R288 code removes a lock whose live ownership was never rechecked, permitting a new writer despite indeterminate custody.

**Fix:** Before closing the descriptor on every exit path, invoke the existing `assert_owned()` check while the descriptor is still open. Ownership uncertainty marks the lock unissued for cleanup, so the on-disk lock remains for manual investigation. Ordinary caller exceptions (`RuntimeError`, `KeyboardInterrupt`, `SystemExit`) retain their original type. On the rare late custody failure *after otherwise successful completion*, return a fixed `ValueError` instead of reporting a successful review action. Previously verified normal cleanup remains in place.

This is cooperative local writer coordination, not a kernel-enforced lock or protection against privileged filesystem mutation. A pathname check plus unlink is not an atomic cross-platform operation. Do not auto-break an uncertain lock.

## Local execution and negative control (2026-11-08)

Linux Python, real temporary files and descriptors, synthetic failure injection. Reconstructed the **exact committed R288 source blob** `7fef850eadf47049fe0b9768a45910f0d8571a4e` and the **exact shared dependency blob** `08c08598ac3575e3baf53ee3275db9aadc315f4d`, then applied the source patch and executed:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_lock_exception_exit_r289.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_review_lock_exception_exit_r289.py' -v
python -m py_compile products/desktop/fvs_suite/review_lock.py products/desktop/tests/test_review_lock_exception_exit_r289.py
```

- **8/8 PASS normal; 8/8 PASS optimized (`-OO -W error`): 16/16 focused executions**; compilation PASS.
- Six of eight methods **fail against the original exact R288 source** (negative control), including simulated interruptions, exception-path descriptor drift/failure, and late post-success drift.
- Remaining cases confirm normal exception cleanup and successful cleanup still work.
- Locally executed new source blob: `c86879d4a9374a49b059d810a570e03fe01b3288`; new test blob: `e238a2a70038668d04d50e2993d83a99b8db84f5`. Both match committed GitHub blob hashes.
- Explicit normal/-OO R289 gates were added to both Ubuntu `source-tests` and Windows `windows-build` jobs; **hosted CI remains unexecuted**.
- No native Windows EXEs, Defender scans, release URLs or customer data were created.

## Blockers and next acceptance

At last verified parent R288 CI [run #42517812253](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42517812253) the Ubuntu and Windows jobs both reported `steps: null`, failure before execution. Root cause **not confirmed**. Owner needs to inspect GitHub Actions billing/spending limits, workflow policy and runner availability, then rerun the unchanged R289 commit. If hosted runners remain blocked, run the existing private `products/desktop/scripts/offline_windows_candidate_r269.py` gate on a trusted Windows 11 x64 system with full regression, six real EXE smokes, SHA-256, Defender and receipt evidence.

The full inherited repository suite, real native build, physical accessibility and protected premium distribution remain unverified. **Do not merge, release, publish premium binaries or bypass independent QD and founder sign-off.**
