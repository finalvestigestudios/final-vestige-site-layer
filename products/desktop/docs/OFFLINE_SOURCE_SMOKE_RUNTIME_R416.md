# R416 — One global deadline for twelve offline six-app source smokes

**Status:** Internal source-only engineering evidence. DRAFT, hard release HOLD. Tracked by [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73), stacked on R415 draft #2416. This does not modify production `main`.

## Defect and finite execution contract

R415 imposed a 90-second timeout **per subprocess** for each of six launchers in both normal and optimized Python. Twelve independently timed out processes could consume up to 1,080 seconds, plus repeated inventory scans, in a 20-minute source-evidence CI job. A caller also could override timeout with `None` and remove child time limits.

R416 enforces an **integer-only** 1–120-second per-child timeout and a **shared 300-second monotonic budget** covering preflight and all twelve subprocesses. Before each child, the remaining global budget caps `subprocess.run(timeout=...)`; expired budget stops further children without claiming any successful receipt. A late return after the total deadline likewise fails closed. Rejections use constant diagnostics without customer filenames, financial data, credentials, child output, or exception chains. The runner continues to invoke Python `-I -B -W error`, never uses a shell, passes a restricted environment, discards stdin/stdout/stderr at OS level, validates SHA-256 source continuity before and after each subprocess, and always sets `release_authorized=false` on normal receipts.

**Scope limitation:** This is a subprocess scheduling budget, not a strict 300-second wall clock for blocked filesystem metadata calls or a hardened OS process sandbox. No new network access, data telemetry, financial rule, premium entitlement, binary, site content, or download link.

## Evidence

- New committed `products/desktop/tests/test_source_smoke_runtime_r416.py`: **12 regression methods**, including 12 real synthetic source launchers, invalid/bool/float/None timeouts, preflight expiration, first and twelfth child overruns, shrinking remaining-time cap, private timeout output, DEVNULL/no-shell custody, and no-release receipts.
- Both `python -W error` and `python -OO -W error` required by the Windows/Ubuntu source-evidence workflow.
- An **independent Linux extraction of the modified scheduler logic** passed **9/9 standard and 9/9 optimized** synthetic methods (18/18). **This was not execution of the exact committed runner or exact 12 committed methods; full repository integration is UNVERIFIED.** Do not count these model results as six-engine financial or packaged-binary evidence.
- The source workflow and Windows packaging workflow previously failed before runner steps on the R415 exact HEAD. Reinspect exact R416 workflow runs when created; a failed-before-run job is neither a test pass nor proof of test failure.

For a trusted checkout on both Ubuntu and Windows:

```sh
# from repository root; PowerShell equivalent: $env:PYTHONPATH='products/desktop'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_source_smoke_runtime_r416.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_source_smoke_runtime_r416.py
python -I products/desktop/offline_source_smoke_r408.py
```

## Release HOLD and next highest-impact action

Owner: resolve GitHub Actions runner/billing/eligibility issue and run exact-commit complete checkout on Windows and Ubuntu (R408–R416 plus all financial, Decimal, provenance, AES-GCM, Ed25519 and premium review suites). Then build actual Windows x64 PE executables, smoke them natively, run Defender and NVDA/high-DPI observations, hash the exact artifacts, and verify premium unauthorized-download denial. Keep private premium executables off unrestricted URLs. Independent QD and explicit founder approval are still required before merge, website publication, access-control promotion or release. **All six applications remain unreleased.**
