# R267 — Uncaught main-thread exception privacy (draft; release HOLD)

**Issue:** #73 · **Date:** 2026-11-07 UTC · **Parent:** R266 draft PR #1485, commit `44fdc52cc9b14431872372d058aec7d56747413c` · **QD and founder approval required.**

## Defect and scope

CPython's default `sys.excepthook` emits complete unhandled main-thread tracebacks, which can include confidential CSV filenames, customer paths and invoice identifiers. R264–R266 already protect handled GUI, Tk callbacks, worker threads and unraisable cleanup errors, but **exceptions raised after normal GUI dispatch returns** (or in other code executing after the shared launcher initializes) can still reach the default hook.

A synthetic `OSError("C:/private/CUSTOMER_PAYROLL_2026.csv")` reproduces the unprotected interpreter disclosure. This increment installs a third fixed-output hook alongside R266's thread and unraisable hooks, before any of six applications dispatches. **Only** `Final Vestige Labs uncaught error; private diagnostics suppressed` is written to stderr; exception type, value and traceback are never inspected or formatted. Normal uncaught failures keep a nonzero exit. `SystemExit` is handled by the interpreter and remains unchanged. Failed or silently discarded installation denies startup through the existing safe launcher error path. The security module remains pure standard-library Python and has no network, upload or telemetry features.

**Covered identifiers:** `ledger` (LedgerDiff Lite), `invoices` (Invoice Twin Scout), `spend` (SpendMap Lite), `policy` (Policy Delta Desk), `grants` (GrantAudit Studio Pro), `procurement` (ProcureGuard Studio Pro). Both premium applications stay offline, behind existing entitlement and human-review controls. No business/Decimal/evidence calculations or automatic compliance decisions changed.

## Executed local evidence

Linux **CPython 3.13.5**. Regression module `products/desktop/tests/test_main_exception_privacy_r267.py` exercises real CPython uncaught exceptions in child processes with **synthetic** paths. Full testing of the installed Windows applications was not performed. For launch-path checks, only GUI dispatch is mocked; the **real shared launcher and offline-network audit guard** are executed in the isolated local source harness. These results do not prove full repository health, GUI behavior or packaged Windows executables.

Commands (from the prepared root, `PYTHONPATH=products/desktop`):

```sh
python -W error -m unittest discover -s products/desktop/tests -p test_main_exception_privacy_r267.py -q
python -OO -W error -m unittest discover -s products/desktop/tests -p test_main_exception_privacy_r267.py -q
python -m py_compile products/desktop/fvs_suite/background_privacy.py products/desktop/tests/test_main_exception_privacy_r267.py
```

**Result:** 14/14 normal methods PASS; 14/14 optimized methods PASS (including `-OO` child interpreters); **28/28 focused test method executions PASS**; compilation PASS. Tests include every app ID, chained exceptions, KeyboardInterrupt, SystemExit, hostile payload/formatter, stderr-write failure, idempotence, preservation of R266 thread/unraisable behavior, rejected/silently discarded hook registration, safe launch rejection, version flag and no I/O during direct installation.

**Exact executed source matched Git blob SHA-1 objects:** `fvs_suite/__init__.py = a3e3f9fdeaf0f74f10077a7299f29f505dbe991f`; `background_privacy.py = dd73f396fbff91dc1405c15978180f9569ee1378`; `offline_network.py = 30039ab587cb5a0ce3be305d78d3f919385a2fbf`; `launcher.py = ae8eb69bfd45b1094c771cf4a08b37cd2e09b3fc`; `test_main_exception_privacy_r267.py = b3e95cc0a841b81ed70effcd856f716e2b1449d5`. Thus both the **real** offline guard and launcher were exercised; only the app GUI module was replaced with an in-process stub. No native Windows x64 execution or packaged binary test occurred. The R267 hosted [run #42423573021](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42423573021) also failed **before execution**: both source and Windows jobs reported failure with zero recorded steps, no runner identity or logs. The previous R266 run [#42419215770](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42419215770) reported Ubuntu and Windows jobs failed **before any steps**, without an assigned runner or logs; root cause remains unconfirmed.

## CI and safety gates

The internal `.github/workflows/desktop-build.yml` now gates R267 regression tests in normal and `-OO` modes in **both** the Ubuntu source job and the Windows build job, before executable packaging. GitHub Actions must actually assign and run both jobs before they count. The branch is stacked on R266 draft, **never production main**.

This is a **CPython hook**, not a native crash handler, Windows OS firewall or a comprehensive guarantee against all exfiltration and unexpected output. Code can replace writable interpreter hooks; unmanaged C modules and console subprocesses require separate review. Do not release based on this unit test alone.

**Release HOLD:** Six apps remain **UNRELEASED**. No site changes, production branch merge, public installer, unrestricted premium download, or invented verified binary URL. Independent QD approval and founder authorization remain mandatory.

**Highest-impact next action:** Owner confirms Actions billing/usage, workflow permissions and hosted-runner provisioning, then reruns pinned R267 CI. On true Windows 11 x64, privately package each of six app-specific EXEs, validate smoke/GUI/accessibility/Defender, SHA-256 checksums, network-denial and premium access control before QD/founder release review.
