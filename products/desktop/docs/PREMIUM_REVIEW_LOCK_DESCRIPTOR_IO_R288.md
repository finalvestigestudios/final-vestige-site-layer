# R288 — premium review-lock descriptor IO path-custody regression

**State: draft, local-focused verification only.** Issue #73; parent R287 \`bc2ca693f53c7da08bc6662c7d045a4a1feb7cab\`. No main, live website, payment, or executable changes. Independent QD and founder HOLD.

## Concrete defect and fix

R287 redacted path-carrying OS errors from \`open\`, \`lstat\`, and \`unlink\`, but the same premium lock used unsanitized \`fstat\`, \`write\`, \`fsync\`, and \`close\`. Injected OS errors with a confidential local path escaped via their raw exception text and traceback. Both GrantAudit Studio Pro and ProcureGuard Studio Pro share this lock in the offline human-review journal workflow.

R288 adds fixed-message, no-chained-OS-exception wrappers at those four descriptor operations; rejects zero/partial writes and preserves indeterminate lock files for manual investigation. It also withholds automatic lock cleanup after failed live descriptor custody checks. It updates the older R48 test to require the new sanitized \`ValueError\` contract on failed \`fsync\`. Normal successful lock cleanup is unchanged. The four free apps, Decimal financial engines, append-only review events, offline posture, premium entitlements, and human approvals were not altered.

## Actually executed (local, 2026-11-08)

Run under Linux CPython 3.13.5 using **full byte-identical committed R287 \`review_lock.py\` and \`csv_snapshot.py\` dependencies**; new R288 source was tested before GitHub commit and matched the Git blob created for the PR.

\`\`\`bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_lock_io_privacy_r288.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_review_lock_io_privacy_r288.py' -v
python -m py_compile products/desktop/fvs_suite/review_lock.py products/desktop/fvs_suite/csv_snapshot.py
\`\`\`

- **9/9 PASS standard; 9/9 PASS \`-OO -W error\` = 18/18 focused executions**, Python compilation PASS.
- Nine methods cover initial/post-sync/live descriptor failure, raw write failure, short-write then failure, zero-write, failed sync, failed close, and three successive normal exclusive lock rounds. Injected exceptions contain a synthetic confidential path, and each resulting error is checked for exact redacted text, no \`__cause__\`, and no \`__context__\`; unexpected or uncertain locks are preserved.
- Negative control: the **exact original R287 source Git blob \`de5b5b8bfa09498f1ec55bb719a82ff89073c10e\`** yields **8/9 errors** in the new test file, including raw private-path exceptions. The patched candidate passes all nine under both modes.
- Exact tested dependency Git blob: \`csv_snapshot.py\` \`08c08598ac3575e3baf53ee3275db9aadc315f4d\`. Candidate source Git blob: \`review_lock.py\` \`7fef850eadf47049fe0b9768a45910f0d8571a4e\`. New test Git blob: \`cc2e16e23ca3c33ae8c74f87f557e65c86b5b52a\`. These hashes identify the **locally executed** source and tests, not a complete repository checkout.
- New two-mode CI gates added to **both Ubuntu source-tests and native Windows-build** jobs. They are committed but **have not executed in GitHub Actions**.

## Current blockers / next acceptance

[Parent R287 workflow run #42512815769](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42512815769) failed on 2026-11-08 with both \`source-tests\` and \`windows-build\` reporting \`steps:null\`; no runner or step-execution evidence. CI root cause not confirmed; investigate Actions billing/spend, workflow access, and runner allocation, then rerun the exact R288 head. The full inherited desktop test suite, actual Windows 11 x64 build, PE and SHA-256 witness, executable smoke tests, Defender scan, physical keyboard/screen-reader test, and gated premium distribution **remain unverified**. Do not publish downloads or merge without independent QD + founder authorization.
