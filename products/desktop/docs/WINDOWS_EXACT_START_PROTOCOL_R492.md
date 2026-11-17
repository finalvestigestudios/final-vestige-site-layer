# Final Vestige Labs R492 — exact Windows source authorization (DRAFT / QD HOLD)

## Measurable change
Issue #73; stacked **only** on R491 draft PR #2841 at `ba0a31959a9b6084e88996d8814f77c00e41af8b`, not `main`. This improves the *internal source-test harness* for LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro. No product engine, public catalog, premium entitlement, release or executable is modified.

R491's isolated `python -I -S` bootstrap accepted **any input starting with `G`**, even `GG`, `GX`, or `G\x00`, and began unittest imports immediately after that first byte while the parent's control pipe was still open. It also validated the argument tail but did not bind the interpreter executable identity to the current Python runtime. In an unexpectedly altered invocation, the intended startup/Job custody guarantee could be misleading.

R492 changes:
- Bootstrap uses `sys.stdin.buffer.read(2) == b'G'`, requiring **the exact single authorization byte followed by EOF**. Source test imports cannot begin until the parent closes the write end. The runner already writes `G` then closes its control pipe after successful Windows Job Object assignment.
- `guarded_windows_command` requires an exact built-in string executable matching `sys.executable` (already used by the runner) before generating a guarded invocation; untrusted executable substitutions fail closed.
- New `test_windows_source_protocol_r492.py` checks good ordinary and optimized executions, malformed/trailing/duplicate bytes, delayed EOF, executable substitution, and forged string subclasses through **real isolated child Python subprocesses**.
- Ubuntu and Windows independent source workflow invokes all R492 regressions in normal and optimized Python.

## Local executed proof — 2026-11-17
- Ubuntu-like Linux, CPython 3.13.5; test and helper Git blob bytes matched exact committed source: `windows_source_start_custody_r491.py` blob **`ce583b20479921415930b74a39bd2f2165852e37`**, new test blob **`cda9d80829fab688990461794a126985c9227f86`**.
- `PYTHONPATH=. python -B -W error -m unittest discover -s tests -p test_windows_source_protocol_r492.py -q`: **9/9 PASS**.
- Same with `-OO`: **9/9 PASS**.
- Together with locally reconstructed inherited R491 tests: **17/17 standard PASS; 17/17 optimized PASS**. Inherited tests were recreated for this local check; they were not independently blob-matched.
- Negative control using the **exact R491 parent helper blob `dba0e732cb5a71a698fee54cd8c16958ebbd9c7a`**: **4 expected failures of 9 tests**, reproducing accepted trailing authorization and unbound executable.
- Python compilation of helper and R492 tests passed. Test fixtures are synthetic; **the complete source-runner integration and native Windows Job assignment have not executed locally**.

## Boundaries and next action
This is a *source-test handoff correctness* fix, not a sandbox, evidence of all six finished Windows apps, or proof of native Win32 Job Object protection. It does not constrain native Python startup/DLL loading and it relies on parent-held pipe custody. Internal redacted JSON receipts, zero telemetry/default networking, Decimal-safe money primitives, traceable exports and human compliance review are unchanged. No website updates, binaries or download links are authorized.

R491 exact-commit [six-engine CI run #44035655079](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44035655079) and [Windows build #44035655337](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44035655337) both failed with four jobs reporting no executed steps. Root cause remains **unverified**. Check new R492 exact-head actions; an authorized GitHub administrator should review Actions account/billing and runner allocation, then use a real Windows x64 machine to run R492 plus the inherited source/engine matrix and validate process-tree termination. Only after native packaging smoke, SHA-256 provenance, Defender/EDR, accessibility and authenticated premium delivery may independent QD review and explicit founder approval consider release.

**QD HARD HOLD:** draft PR only; do not merge into production, publish executables, expose premium files, or treat audit/compliance flags as automated decisions.
