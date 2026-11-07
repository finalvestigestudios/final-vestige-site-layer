# R268 — Tk callback privacy-hook installation custody (DRAFT / HARD HOLD)

**Issue:** #73 · **Date:** 2026-11-07 UTC · **Base:** R267 draft PR #1492, commit `b52526e018d397d496f23f51ee9d2e1bad317c2e`. Changes are isolated from production `main`.

## Reproduced failure

R265's per-window Tk exception handler previously assigned `root.report_callback_exception` without checking it was actually installed. A root wrapper or future Tk customization could silently discard assignment and leave Tk's original handler active. The next failing invoice, payroll, grant, procurement or policy callback could then print private financial paths and traceback data.

The R268 change reads back the installed handler by **object identity** before any GUI callback starts. A denied assignment, silent drop, exception on readback or alternate handler now triggers a fixed `RuntimeError`, raised **outside** its catch block to avoid retaining a sensitive exception chain. Existing launcher's synchronous privacy boundary converts failed initialization to a fixed nonzero exit. Genuine callbacks still invalidate stale premium review selections before showing the same accessible text dialog. `KeyboardInterrupt` and `SystemExit` semantics are unchanged.

## Test evidence (source only)

- Before patch, isolated original-installation behavior: **4 failures + 1 error** in the new 12-method suite (assignment rejected, dropped, getter failed, inconsistent identity, interrupted getter).
- After patch, Linux local CPython using exact committed test/source Git blobs: **12/12 normal** with `-W error`, **12/12 `-OO -W error`**, **24 method executions passed**; `compileall` passed.
- Tested module SHA: `c9a106cdadeda9ee27fe2dea7e16e458fde85dc8`. Test SHA: `3680184f5cdebe926f41bd3271856471e9e22869`. Tests use Tkinter's real `CallWrapper` but a headless root double; no live GUI or actual Windows binary was exercised.
- Ubuntu **and** Windows job definitions now run the R268 suite in normal and optimized Python; those hosted tests have **not** executed successfully. Do not infer Windows success from Linux source tests.

## Scope, safety and QD hold

All six applications share the modified `install_callback_privacy` call in `fvs_suite.app.run`. No money parser, Decimal math, source report, evidence fingerprint, premium entitlement, HTML catalog, branch `main`, or WordPress publication changed. No financial source data, network, or premium binary was used. The Python safeguard is **not** an operating-system isolation guarantee, and it does not certify native Windows Tk behavior.

**Release remains HARD HOLD** until genuine Windows 11 x64 executable builds, source regressions, functional smoke, keyboard/screen-reader acceptance, malware/Defender evidence, SHA-256, protected premium delivery, independent QD and founder approval.

## Blocker and next highest-impact step

The prior R267 Actions run [#42423692490](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42423692490) showed source-tests/windows-build failure without executed steps/logs. Owner should verify GitHub Actions billing/limits, runner provisioning and permissions, then rerun the unchanged R268 commit on both runners. Once execution works, perform complete inherited regression and real Windows 11 x64 six-executable smoke/keyboard/network/EDR acceptance; capture provenance before authorizing any distribution.
