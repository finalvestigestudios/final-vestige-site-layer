# R269 — Private Windows 11 x64 six-application candidate runner (DRAFT / QD HOLD)

Issue [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This is a local fallback for the repeated GitHub Actions **pre-runner failures**. It does not remove the CI blocker, certify executables, approve compliance decisions, or authorize publishing any app.

## Owner-operated path — no public distribution

On a trusted **Windows 11 x64** workstation, check out this draft feature branch in a clean local clone. Use a **64-bit Python** environment with preinstalled trusted PyInstaller and cryptography dependencies (the internal workflow expects Python 3.12, cryptography 46.0.4 and PyInstaller 6.12–6.x; see the repository's exact CI configuration). Perform dependency provisioning separately, with audited package sources. The runner itself performs **no package installations or network downloads**.

Create a distinct local directory **outside the source checkout**, restrict its Windows ACL to the operator only, and ensure adequate private free space. From the repository root:

~~~powershell
py -3.12 -I products/desktop/scripts/offline_windows_candidate_r269.py --workspace "C:\FVS_Private_Candidates"
~~~

The given workspace must already exist. The runner rejects symlink workspaces, checkouts, directories inside the checkout, and ancestors of the checkout. It creates a unique new **fvs-r269-private-*** directory for each attempt. Do not sync or share that directory: it can contain the **two unreleased premium binaries**.

## Actual gate sequence

1. Execute the repository's existing **full normal/optimized Python source-test suite and all six source-engine smokes** (not equivalent to Windows binaries).
2. Snapshot installed Python / PyInstaller / crypto dependencies and source files using existing source and toolchain custody guards.
3. Build the six distinct one-file, windowed Windows x64 EXEs, individually checking both custody manifests **before and after each build**.
4. Generate the private, six-name **SHA256SUMS.txt** inventory, with no unexpected files.
5. Run the existing **native Windows x64 PE gate and six real executable --smoke-test** operations, writing the offline evidence report outside the candidate directory.
6. Independently recheck the report against candidate bytes, using its same-run SHA-256 as a consistency pin; rerun both input custody checks.

On any nonzero child exit, timeout, missing report, unsupported platform, or failed verification, the run fails closed. Subprocess output is suppressed rather than spilling financial filenames or private build paths into logs. A failed attempt's newly created directory is removed best-effort. If Windows prevents cleanup, the operator must manually secure and remove any remnants. A successful run retains only **local private evidence** for review. No upload, artifact API call, web link, deployment, or release label occurs.

## Verified engineering evidence (2026-11-08 UTC)

- New source: `products/desktop/scripts/offline_windows_candidate_r269.py`.
- New regression tests: `products/desktop/tests/test_offline_windows_candidate_r269.py`.
- **18/18 normal + 18/18 optimized = 36 passing local test executions** under Linux CPython 3.13.5, with `-W error`; `compileall` PASS.
- **Plan simulations only**: regressions validate six identities, ordered 40 child invocations, pre/post custody, fail-stop semantics, private workspace constraints, no shell/log output, cleanup behavior, and no publication.
- Real Windows toolchain, PyInstaller builds, native PE inspection, Defender scan, real Tk keyboard/screen reader tests, signing and gated premium distribution **were not executed by this sprint**. The tests do not represent proof that any six EXEs exist.
- The two executed local files' Git blob identities were compared with committed GitHub files (no local code divergence).

## Required independent QD / founder controls

Even a full private green run is **NOT a release**. Owner must independently verify actual Windows 11 GUI usability and keyboard/screen-reader operation, current Defender/malware scan, source and dependency provenance, signed or clearly unsigned Windows distribution, protected premium payment/entitlement flow, public URL/link validation, checksum fingerprints saved independently, and independent QD + founder approval.

**Smallest CI unblock:** Have an authorized owner inspect GitHub Actions billing/usage limits, Actions permission settings, and hosted-runner provisioning. Jobs for [R268 run #42427627508](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42427627508) failed with zero recorded steps on 2026-11-07. Restore runner execution and rerun the exact unchanged head before any QD release decision.
