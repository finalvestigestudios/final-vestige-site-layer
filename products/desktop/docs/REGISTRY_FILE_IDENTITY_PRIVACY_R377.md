# R377 — premium SQLite registry identity and diagnostic privacy (draft / HOLD)

## What changed

Applies only to the operator-controlled offline issuance registry for **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. Neither the four free utilities, the site's QD workflow, nor customer entitlement validation is changed.

The inherited R376 _check_file() accepted a registry path that was a **hardlink** to another operator-owned, mode-0600 regular file (st_nlink greater than 1). Opening SQLite through that alias could then operate on the other file. It also used exception chaining on os.open failures, retaining sensitive OS paths in __cause__ and __context__, and os.fdopen failure could strand a raw descriptor.

R377 delegates inspection to registry_file_guard.verify_registry_file, which:

- Preserves O_RDWR, O_CREAT | O_EXCL, mode 0600, O_NOFOLLOW where supported, and the existing non-symlink/regular-file/POSIX-ownership rules.
- Requires exactly **one hardlink** (st_nlink == 1) before SQLite is opened.
- Inspects via os.fstat on the raw descriptor and retires that descriptor in a finally block, without an unnecessary fdopen wrapper.
- Defers translated OSError failures until outside the handler; the resulting RegistryError has no private __cause__/__context__. Treats unsuccessful close as a fail-closed error.
- Never opens or edits customer financial exports, changes entitlement signing, retries an issuance, publishes binaries, or bypasses human issuance review.

**Limits:** This is a pre-open pathname check; sqlite3.connect(str(path)) opens the DB separately. A privileged or same-user attacker able to modify the protected directory could still race/swap the path. Enforce a trusted operator-owned parent directory, leave SQLite registry files outside Git worktrees, and do not treat this patch as an OS-level file-handle binding or protection against a compromised operator account. On Windows, O_NOFOLLOW is not universally available; Windows junction/reparse-point race hardening still needs native acceptance.

## Measured local evidence (2026-11-12, Linux Python 3.13.5)

- Reconstructed **original R376 _check_file** accepted a synthetic hardlinked 0600 file with st_nlink=2 (reproduced defect).
- Exact helper Git blob b46da03bc853cf7d7203f48261b6dd3fe27bac10 and exact 14-test Git blob 3eb5d8d87dd5fd6878afbb0c23c9e98f948a68d3 executed locally:
  - python -W error -m unittest -q test_registry_file_guard_r377.py — **14/14 PASS**
  - python -OO -W error -m unittest -q test_registry_file_guard_r377.py — **14/14 PASS**
  - python -m compileall -q registry_file_guard.py test_registry_file_guard_r377.py — **PASS**
- 28 total focused test executions: creation/mode, immutable existing bytes, nonregular/symlink/hardlink rejection, group-readable rejection, deterministic private path redaction including chained faults, metadata failure + descriptor cleanup, close failure, repeated inspection, both premium registry aliases, and no file-content reads.
- These local tests executed the **exact committed helper and test module**, not a complete repository checkout running the revised license_registry.py integration. The four original free tools were not exercised.
- Four CI invocations (Linux/Windows, normal/optimized) were added to the existing internal desktop-build workflow before packaging.

## Release gates and owner unblock

The R376 parent GitHub Actions run [#43205453362](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43205453362) failed for both source-tests and windows-build, each with no recorded steps; failed-check annotations are not retrievable through this GitHub connector. This is not evidence of failing application tests or a functioning Windows build. The root cause is not verified.

**Smallest owner action:** inspect GitHub Actions failed-check annotations and account Actions billing/spending limits/hosted-runner eligibility, then rerun the exact R377 draft head.

**Next acceptance:** run the complete inherited six-app repository tests (including the 22 genuine AES-GCM cases), real Windows 11 x64 build and executable smoke, Defender, keyboard/accessibility, premium entitlement + restricted distribution checks, then independent QD/founder approval.

**Release HOLD:** No merge to production, no site publication, no new executables or unrestricted premium links. Human review remains required.
