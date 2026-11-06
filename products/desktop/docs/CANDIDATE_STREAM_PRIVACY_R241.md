# R241 — post-handoff candidate stream privacy and descriptor custody (DRAFT / HARD HOLD)

Date: 2026-11-06 UTC. Parent: [R240 draft PR #1299](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1299), immutable parent commit `61c8e74b7983370829733284d8b5e81db12ff5dd`. Scope: [Labs issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).

## Defect and fix

The release-candidate `candidate_guard._inspect` hashes all six staged Windows x64 EXE candidates and reads `SHA256SUMS.txt`. R239 closed descriptors on `os.fdopen` failure but did not own the descriptor if the returned stream's `__enter__` raised. It also caught only `OSError` during post-open stream reads, `fileno`, and stream exit. Other ordinary exceptions could expose private customer/path strings. R241 introduces a scoped private stream context that explicitly attempts to close on failed context entry, translates ordinary unexpected stream errors to a constant `CandidateGuardError` (with suppressed cause), and retains validated guard errors, `KeyboardInterrupt`, and `SystemExit` semantics.

**No security gate is weakened:** symlink/hardlink checks, regular-file requirement, strict byte limits, path/descriptor pre/post identity, deterministic SHA-256, checksum inventory custody, no network use, and private-only release remain unchanged. This is defensive I/O code, **not** signature verification, Windows malware scanning or release approval.

## Reproducible local evidence

Exact Git blob `cc92c58246196f284ea12659621a347bd96e4fe9` for patched `products/desktop/candidate_guard.py`; exact Git blob `eef21f558957409d21351d485781a6f50c5a2f52` for the new 18-case `products/desktop/tests/test_candidate_stream_privacy_r241.py`. The inherited R239 regression file used locally matched Git blob `a609a35b054be2af8e0ddb6037ae18811b9deac1`.

Control: prior R239 `candidate_guard.py` was recovered byte-identical to blob `6092e69f8d09c78f874c763b625c5ff2043b9c62`. Running the new 18 methods against it reproduced **4 test failures and 6 errors** (failed context entry left descriptors open, and unexpected exceptions leaked); those original failures are not acceptance passes.

After fix on **Linux x86_64 CPython 3.13.5**, synthetic local files with actual OS file descriptors:
- `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_candidate*.py'` — **38/38 PASS, 0 skips** (18 R241 + 20 inherited R239).
- Same invocation with `python -OO -W error` — **38/38 PASS, 0 skips**.
- Total **76/76 local test method executions PASS**, affected Python compilation PASS.
- R241 tests cover both EXE SHA-256 and manifest read: stream entry/read/fileno/exit OSErrors and non-OSErrors, fixed messages/no cause/private path, FD cleanup, preserved interrupts, no input mutation, exact successful hash and manifest bytes.

CI: mandatory **normal and `-OO`** R241 gates are inserted into both Ubuntu `source-tests` and Windows `windows-build` before package generation; the source-only workflow cannot authorize publication. No full repository regression and no native Windows build/run, Defender scan, real-machine accessibility, or premium access-control transfer acceptance was performed locally.

## Release hold and next action

Most recent parent [R240 Actions run #42285792483](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42285792483) failed; Ubuntu source-tests job `128126134171` and Windows-build job `128126134326` both recorded **0 steps**. Cause unconfirmed; inspect Actions billing/spending limits, workflow permissions, and runner allocation, then rerun **unchanged** R241 head. Obtain full repository and native Win11 x64 six-app evidence, SHA256/Defender/smokes/accessibility/premium authenticated distribution, independent QD review and explicit founder approval before any merge/publication. Four free and two premium Windows utilities remain **unreleased**; there are **no** authorized executable download URLs.
