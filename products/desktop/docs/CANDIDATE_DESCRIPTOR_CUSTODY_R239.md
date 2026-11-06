# R239 — release-candidate and SHA256SUMS descriptor custody (DRAFT; release HARD HOLD)

Date: 2026-11-06 UTC. Issue [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked only on [R238 draft PR #1287](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1287), base commit `05f836a224c0e54a66d3190f236043374e2053bb`. **Never merge directly to production; independent QD and founder approval are mandatory.**

## Why this is a real defect

`candidate_guard._inspect` opens a raw descriptor with `os.open` and previously passed it directly into `with os.fdopen(descriptor, "rb")`. When `fdopen` failed before returning a stream, no context manager existed to close the raw descriptor. Ordinary OSErrors were sanitized by the outer handler, **but still leaked the handle**; `ValueError` / `TypeError` / `UnicodeError` could expose client-provided exception strings, and `KeyboardInterrupt` / `SystemExit` escaped with an unclosed descriptor. This matters for both `sha256_candidate` (six potentially private or premium Windows EXEs) and `read_checksum_candidate` (the seven-file bundle's SHA256SUMS.txt).

## What changed

- Transfer descriptor ownership **only after** `os.fdopen` returns a valid stream.
- On *every* pre-transfer `BaseException`, attempt to close the original descriptor. Ordinary `Exception` types fail closed to the fixed `CandidateGuardError("Unable to read candidate payload safely")` with suppressed printed exception chaining. Genuine interruptions are re-raised after cleanup.
- Preserve the existing `with stream` guard for all post-transfer read/fstat failures; retain source/destination identity checks, SHA-256, all size caps, hardlink/symlink rules, non-overwriting release flow, and no telemetry or remote processing.
- Add 20 synthetic, real-FD regression methods that exercise both **candidate EXE hashing** and **checksum manifest reading**: simulated permissions/EMFILE/TypeError/ValueError/UnicodeError failures; KeyboardInterrupt/SystemExit; pre-open OSErrors; post-handoff `fstat` errors; and exact successful digest/manifest-byte handling.
- Add mandatory normal and optimized Python test steps **before packaging** on both Ubuntu source-tests and Windows-build GitHub Actions jobs. CI failure must block any internal executable artifact. This change **does not** scan, execute, sign or authorize executable distribution.

## Reproducible local evidence and scope

On Linux x86_64 CPython 3.13.5, with isolated copies of the exact affected module and exact new test source:

| Evidence | Result |
| --- | --- |
| Original R238 candidate guard Git blob | `d6d5b4660b64fc07f9a61ab848ea5114796a10a8` |
| Pre-fix control using all 20 new methods | **FAIL as expected:** 8 failures, 6 errors, 20 total |
| Patched candidate guard Git blob | `6092e69f8d09c78f874c763b625c5ff2043b9c62` |
| New regression test Git blob | `a609a35b054be2af8e0ddb6037ae18811b9deac1` |
| `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_candidate_fd_custody_r239.py'` | **20/20 PASS**, 0 skips |
| Same command with `python -OO -W error` | **20/20 PASS**, 0 skips |
| Python compileall for affected local source/tests | PASS |
| Total focused local executions | **40 PASS / 40** |
| Full inherited repository suite | **NOT run** (no complete checkout in local execution environment) |
| Native Windows 11 x64 and packaged EXEs | **NOT verified** |

No actual financial evidence, premium binaries, licenses or production website contents were accessed by the synthetic tests. The original control failures demonstrate the previous weakness; they are not passing acceptance results. Real-host `fdopen` failures are uncommon; fault injection is deliberate and tests only the failure path, not platform-specific distribution.

## CI, QD, and release custody

Prior [R238 workflow run #42267210721](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42267210721) failed with Ubuntu and Windows jobs before recorded test steps; exact runner cause **unconfirmed**. New R239 workflow status must be read from this branch's Actions run; do not claim passing hosted CI or built executables until execution evidence exists.

**Owner unblock:** inspect GitHub Actions billing/spending limits, runner provisioning and workflow permissions in repository/account settings, restore runner allocation, then rerun this exact head unchanged. Next, run complete six-engine regressions and build private Win11 AMD64 candidates, verify SHA-256, execute native smoke/accessibility/Defender checks, verify protected premium transfer/entitlement, obtain independent QD and founder sign-off. The four free and two premium apps remain **UNRELEASED**; no public download link is authorized.
