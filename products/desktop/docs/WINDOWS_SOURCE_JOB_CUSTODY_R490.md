# R490 — Windows offline source-test Job Object custody

**DRAFT / INTERNAL / QD HARD HOLD.** Tracks #73. Stacked strictly on R489 draft PR #2830 at commit `c67f0e770a2d85f801173644466d03e0303c3573`; never target or modify production `main`.

## Risk and change

The R489 offline source regression runner terminates POSIX same-process-group grandchildren but Windows previously killed only the direct unittest process. A Windows test could exit with a legitimate `OK` receipt while a quiet child continued touching local files. R490 allocates a native Windows Job Object, enables `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, and assigns the test process. Every successful, failed, timed-out or over-budget test tears down that assigned job. Failure to create, configure, assign, terminate or close the job blocks source-test success rather than reporting PASS. The direct-child kill fallback is used on teardown failure, but **must not be mistaken for a verified descendant cleanup**.

This changes only test-runner process custody. The four free and two premium engines, local-first financial privacy, Decimal calculations, deterministic audit evidence, human compliance reviews, fixed-label redacted JSON and `release_authorized=false` remain unchanged. No financial documents are uploaded.

## Evidence obtained in this sprint

- `products/desktop/windows_job_custody_r490.py`: native Win32 API adapter and fail-closed custody lifecycle, checked against mockable interfaces.
- `products/desktop/offline_source_gate_r485.py`: uses Windows job assignment, teardown on every exit, and BLOCKED on custody failure.
- `products/desktop/tests/test_windows_job_custody_r490.py`: nine mock-driven tests for creation, kill-on-close, assignment, teardown, handle ownership and private exception redaction; one additional **native Windows** quiet-grandchild integration test.
- Local Linux Python: **9 passed, 1 Windows-only skipped** in normal mode; **9 passed, 1 skipped** under `-OO`. Python compilation passed for the added helper and tests. Exact local helper blob `57a225df171ed035df879495319e0afbada7d7dc`; test blob `439da73b4ff93077efb3ea4693066f9b8beb7b01`. These match their committed GitHub blobs.
- Independent Ubuntu/Windows source workflow invokes these tests in both Python modes. **The native Windows test and the complete modified runner against the six-application repository have not run in this sprint**.
- Last observed R489 exact-commit Actions runs: source #44021310836 and Windows build #44021310871; four jobs failed before steps (`steps=null`), no tests executed. CI infrastructure cause unconfirmed.

Reproduce in a trusted full checkout:

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_windows_job_custody_r490.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_windows_job_custody_r490.py
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_offline_source_gate_r485.py
```

## Limits and next highest-impact gate

This is **not a sandbox**. The process starts before it can be assigned to the job, creating an assignment race; privileged processes and deliberately escaped work can evade ordinary Job Object control. On Windows the native integration case must execute successfully before treating this as a validated descendant-custody improvement. If existing nested-job restrictions prevent assignment, the test must report BLOCKED, not quietly fall back to an unsafe PASS.

Restore GitHub Actions runner eligibility/billing or run the exact checkout on a trusted Windows x64 test host; execute all R490 and inherited R485–R489 tests plus the complete six-app regression matrix. Then verify x64 package launch, keyboard accessibility, Windows Defender, SHA256 provenance and premium access gates. No executables, releases, premium links, or website edits are authorized; independent QD review and explicit founder approval remain mandatory.
