# Labs R251 — Six-app report completion custody (2026-11-07 UTC)

**Status: DRAFT; independent QD and founder authorization are HARD HOLDS.**
Base: R250 draft PR #1364 at `681f85365728085b2cd331babc5e8a5f3731a4df`. No production branch update, executable publication, customer licensing change or website change.

## Reviewed defect

The common Tk `app.run.execute()` callback handled only `ValueError/OSError/UnicodeError` when an engine generated a report. Unexpected errors such as `RuntimeError` escaped through Tk's exception handler, potentially printing customer paths/records; a malformed result (including `None`, empty list, string or nonexistent path) could appear to succeed or trigger uncaught property/index errors. The GUI selected `outputs[0]` for human exception review without verifying the claimed output had been created. A generation operation may already have written a destination when a subsequent check fails.

## Implementation

- `fvs_suite/report_completion.py` introduces `confirm_report_files`, used by **all six desktop Generate actions**. It accepts an exact `list/tuple` inventory of 1–16 distinct native `Path` instances. Each destination is checked using a non-following filesystem `stat`; symlinks, directories, empty and missing files, duplicate paths, malformed result collections and Path subclasses are rejected.
- `app.py` runs that check **inside** the engine exception handler and **before** publishing success or binding a premium review target. Unexpected ordinary exceptions get an existing fixed-text privacy-safe diagnostic; failed generation keeps automatic report selection revoked and instructs operators to **inspect the output folder before retrying**. No output is deleted, silently retried or interpreted as a compliance approval. Free apps do not retain an irrelevant premium review target.
- Existing offline entitlement validation occurs *before* invoking either premium engine. All original financial calculations, CSV source provenance, persisted evidence, native OS permissions and user files remain unchanged.
- Non-following `stat` establishes only an immediate GUI result-shape/file-presence check. It is **not** content verification, release authenticity, a durable filesystem lock, or an elimination of stat-to-use races.

## Evidence

Test artifact: `tests/test_report_completion_r251.py` — **20 methods** (14 pure output/file tests plus 6 displayless GUI callback tests). Locally executed on **Linux CPython 3.13.5**, normal `-W error` **20/20 PASS**, optimized `-OO -W error` **20/20 PASS**, 0 skips = **40/40 local test-method executions**. `compileall` PASS.

**Reproduction limitation:** local pure verifier and test files were byte-exact (Git blob SHA verified), but local GUI callback was reconstructed from the reviewed source; the full updated `app.py` was **not** executed in its complete repository environment. The committed GUI tests compile the actual nested callback from `app.py` when hosted source tests run. Not a full-repository regression, Tk/NVDA test, Windows native run or executable release verification.

## Required independent QD

1. Restore GitHub Actions job execution; R250 run #42345048358 produced two failed jobs with `steps=null`, root cause not established. Inspect billing/usage budget, allowed workflows, permissions and hosted runners.
2. Run unchanged R251 commit's full normal and `-OO -W error` source/provenance suite on Ubuntu **and** Windows; examine all 20 committed tests and six-app smoke results.
3. On native Windows 11 x64, exercise all six GUI Generate flows: successful report, an engine exception after a partial destination write, unexpected engine exception containing a private pathname, bogus report return, expired premium entitlement, and screen reader/keyboard behavior.
4. Privately build and malware-scan six distinct x64 EXEs; verify signed/unsigned status and SHA-256, traceable deterministic report results, accessibility and protected premium distribution. **Do not publish or expose premium binaries without approved access controls.**
5. Obtain independent QD signoff and founder release approval before merging to production or advertising downloads.

**Next highest-impact action:** restore CI runners and run the complete unchanged source and Windows executable matrix; stop accumulating unverified draft stacks until a native QD gate is available.
