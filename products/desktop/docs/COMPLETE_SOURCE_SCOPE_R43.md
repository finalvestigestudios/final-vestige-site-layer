# R43 — Complete repository-owned Python source scope for six-app smoke evidence

**Status: pre-release, source-only.** This hardening applies to all four free and both premium desktop apps. It does not validate Windows executables, premium entitlement, malware clearance, signing or Final Vestige QD release approval.

## Reproduced defect

The R42 verifier inventoried only top-level Python engine modules and six named launcher files. A successful six-engine source smoke could omit edits to nested modules, top-level imported desktop helpers, and operator scripts. It also silently ignored unexpected Python launchers. An attacker or concurrent process that replaced a Python file with identical bytes could evade the SHA-only pre/post comparison. The new R43 tests reproduced those omissions before the fix.

## New behavior

1. Recursively inventory all Python files under products/desktop/fvs_suite, plus top-level desktop Python helpers, scripts/*.py, and exactly the six approved launcher Python files. Unexpected seventh launchers are rejected.
2. Reject detected symlinked directory ancestors, nested package symlinks, non-regular files and hardlinks. Maintain 16 MiB/file, 256 Python file and 256 traversed directory bounds. Scripts directory remains optional for isolated legacy test fixtures; a symlinked scripts directory is always rejected.
3. Compute the full deterministic SHA-256 inventory before and after all six synthetic smoke routines. Also compare a PRIVATE file-stat identity snapshot (device/inode/mode/nlink/size/mtime/ctime) to detect observed same-byte swaps and touches. The extra metadata never enters the JSON manifest.
4. Keep schema fvs-source-smoke-v1 and explicit released=false, qd_approved=false. Continue R38 no-clobber report publication outside checkout. No financial engine, privacy, licensing, QD, production or artifact upload change.

## Reproduced and executed tests

Linux x86_64 / Python 3.13.5 / PYTHONWARNINGS=error. Tested byte-exact R43 Python and test files plus reconstructed prior R42 and R21 tests and R38 report publisher:

- PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v : **56 passed** (26 new R43, 22 R42, eight R21).
- PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -v : **56 passed**.
- python -m compileall -q products/desktop : **PASS**.

New regressions cover nested modules, top-level helpers, scripts, added seventh launcher, symlinked ancestors and nested directories, hardlinks, unicode paths, source inventory bounds, metadata-only edits and same-content inode replacement.

**Limitations:** focused reconstructed source subset, not the full repository; actual six-engine integration and Windows x64 binaries have not been run. This verification cannot prove historical source authenticity against a privileged adversary, nor does it replace signed builds, malware scans, customer entitlement checks or QD approval.

## CI and release blockers

As of 2026-10-29, [R42 Actions run #40935959856](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/40935959856) failed before any recorded steps on both Ubuntu and Windows. Check R43 CI separately. Smallest unblock: inspect GitHub Actions billing/runners/permissions/storage or run the full checkout tests and private Windows build with products/desktop/scripts/verify-windows-candidate.ps1 -Build on a trusted Windows 11 x64 workstation. Keep all six EXEs unreleased until real smoke, AV/security scan, checksums, controlled premium fulfillment and independent QD review.
