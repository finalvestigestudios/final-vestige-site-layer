# Labs R511 — Source script, manifest ancestry and interpreter-startup custody

**Scope:** Issue #73; DRAFT / QD HARD HOLD. Six Windows x64 desktop tools (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, ProcureGuard Studio Pro). This is CI source evidence hardening, **not** native EXE validation, a product license gate, release or compliance approval.

## Verified defect on exact parent R510

The R509/R510 SHA-pinned 416-command runner checked ancestry for every discovered Python test, but **not the four preapproved executable script commands**. Its entrypoint opened the command manifest without checking the manifest path's ancestry. A missing or symlinked approved script was accepted as an instruction (then only failed or ran after process launch). The child environment could also inherit `PYTHONOPTIMIZE`, `PYTHONWARNINGS`, and loader-injection variables, allowing tests to run under different semantics than declared.

A local reconstruction of the *exact* parent Git blob `7d68f33748a5e73fee7ef2a874afdae753353d0d` reproduced acceptance of a missing script, acceptance of a symlinked script, and propagation of `PYTHONOPTIMIZE` and `LD_PRELOAD` to the subprocess environment. This is a local negative control, not evidence of an actual attacker.

## Change

- `products/desktop/scripts/source_evidence_runner_r509.py`: one shared no-link custody predicate now validates tests, all four approved script entrypoints and the manifest (regular files, unlinked ancestry, Windows junctions when supported). Unknown commands remain rejected. The manifest SHA-1 Git-blob pin and its 416 ordered commands do **not** change.
- Child test processes no longer inherit `PYTHONOPTIMIZE`, `PYTHONWARNINGS`, `PYTHONBREAKPOINT`, `PYTHONPYCACHEPREFIX`, `LD_PRELOAD`, `LD_LIBRARY_PATH`, `DYLD_INSERT_LIBRARIES` or `DYLD_LIBRARY_PATH`. Prior R510 credential and GitHub command-file scrubbing remains.
- `products/desktop/tests/test_source_evidence_runner_r509.py`: 12 additional committed regression methods in the **existing manifest-listed module**; both normal and optimized Python invocations already exist in the immutable 416-command source matrix. Tests cover normal paths, all four preapproved commands, missing files, linked script leaf/parent, linked manifest leaf/parent and entrypoint rejection, bad path segments, environment isolation.
- No GitHub workflow byte limit, workflow command inventory, dependency pin or release workflow permission changed. No production branch, WordPress, installer, premium entitlement or financial-engine change.

**Boundary:** preflight path checks are not atomic/openat custody. Races between validation and launch remain outside this sprint; Linux native and Windows reparse-point behavior require respective hosted tests. Source evidence does not prove six binary identities or that executables are safe.

## Executed local evidence

- Local Linux Python against byte-identical R511 production runner Git blob `2b5b8c89016f65358b2ba14721f7bae83489c212`: 10/10 isolated synthetic focused tests PASS in `-B -W error`, and 10/10 PASS in `-OO -B -W error`; zero skips reported; runner `py_compile` PASS.
- Negative control against exact parent blob `7d68f33748a5e73fee7ef2a874afdae753353d0d`: missing and linked approved scripts accepted, `PYTHONOPTIMIZE` and `LD_PRELOAD` propagated.
- The 12 new *committed* tests and the complete 416-command repository matrix **have not been executed locally as a checked-out whole repository**, because this environment has no authenticated clone/network checkout. They are invoked by the existing R509 inventory when hosted CI executes. Do not substitute focused/probe passes for repository or Windows certification.

## Release hold / next highest-impact step

The most recent R510 workflows failed before runner allocation/steps, not on source assertions. Admin/owner should inspect private-repo Actions billing, spending limits, runner entitlement and workflow policy; then rerun R511 exact SHA on Ubuntu and Windows. Review warnings/errors and skips, execute all 416 ordered source commands and complete native Windows x64 six-app build, smoke, Defender/EDR, SHA256, keyboard/accessibility and protected premium-delivery checks. Independent QD review and explicit founder approval remain mandatory. Never publish unsigned/untested binaries or unrestricted premium EXEs.

Local-first financial privacy, deterministic audit trails, Decimal-safe money and human compliance reviews remain unchanged.
