# R260 — six-desktop-runtime CPython offline network fence (DRAFT / QD HOLD)

Issue: #73. Feature branch: `feature/labs-r260-runtime-offline-network-gate-20261107`.
Immutable stacked parent: R259 commit `29083a97b00d30780e67177a98151da407892b27`
(draft PR #1428). This is **not** production `main`; no release or merge is authorized.

## Change

- `fvs_suite/offline_network.py` installs a process-global Python audit
  hook to deny socket creation, bind/connect/send, DNS and urllib request events,
  including loopback, with a fixed private-data-free message.
- `fvs_suite/launcher.py` installs the guard **before** importing the GUI,
  the smoke engine, or opening customer inputs. All six real executable entry
  scripts call this shared launcher without alternate dispatch paths.
- Python may silently veto `sys.addaudithook` when another hook raises
  `RuntimeError`. A private audit-event sentinel confirms *our exact hook*
  is active. A failed installation/probe aborts startup. Repeated installation
  in the same interpreter is idempotent.
- No network exception is made for premium licensing, localhost, or telemetry.
  The existing offline Ed25519 entitlement and human review workflows remain
  unchanged. Local filesystem operations and `Decimal` arithmetic are unaffected.

**Scope limitation:** This constrains CPython-audited network APIs in app
processes. It is not an OS firewall or a complete defense against untrusted
native extensions, external child processes, or code that bypasses Python audit
events. Native Windows 11 x64 behavior must be separately verified before
any binary distribution or privacy guarantee. Development code importing
`fvs_suite.app` directly rather than entering through a six-app executable
launcher remains outside this exact startup guard.

## Local evidence (November 7, 2026)

Tested exact committed Git blob copies under **Linux CPython 3.13.5** in an
isolated package preserving the actual `launcher.py` and guard sources.
No network requests were allowed or attempted: tests intercept at Python audit
events before network I/O. The GUI, engine, and smoke implementation were
stubbed only for launcher dispatch tests; **actual financial engines, Tk GUI,
real packaged Windows executables, and whole repository were not exercised**.

```sh
python -W error -m unittest discover -s tests -p test_offline_network_r260.py -q
# 10/10 PASS
python -OO -W error -m unittest discover -s tests -p test_offline_network_r260.py -q
# 10/10 PASS
python -m compileall -q fvs_suite tests
# PASS
```

The ten independent test methods each run in separate child interpreters to
avoid permanent audit hooks contaminating the surrounding unittest process.
They cover all six launcher IDs, a runtime install failure, a *silent* audit
hook registration veto, idempotence, real socket construction, DNS, urllib,
eleven explicit audit events, source file/Decimal preservation, the executable
smoke switch, and version display. **20 method executions passed** (normal
and optimized, warnings-as-errors). No `assert`-dependent safety checks
inside subprocesses: optimized Python is meaningful.

Git blob identities matched locally tested source and tests:

| File | Git blob SHA-1 |
|---|---|
| `products/desktop/fvs_suite/offline_network.py` | `f5bc5d64a82aff371b8253266a1842b858d5f3b4` |
| `products/desktop/fvs_suite/launcher.py` | `c5ff50b3e6ba2b96ff68a997f4a947ac6de0a35b` |
| `products/desktop/tests/test_offline_network_r260.py` | `433144a2d9d4d46c968922d089eb9758e55a8019` |

The existing complete source-gate discovery will include the new
`test_offline_network_r260.py` when GitHub Actions can execute.
No workflow, default branch, WordPress page, price or entitlement key changed.

## Blocker, verification and next step

R259 hosted [Actions run #42384257039](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42384257039)
ended failure with **both** source-tests and windows-build jobs recording
no steps or logs; root cause unknown (billing/usage/permissions/runner are
possibilities, not confirmed diagnosis). R260 workflow execution should be
checked separately against this branch. Smallest owner action: resolve the
Actions runner scheduling restriction and rerun this **unchanged** PR head.

Then run both normal and optimized **whole-repository** source suites; run
actual Win11 x64 six-launcher normal/smoke/network-denial checks; privately
build all six executables, verify SHA-256 manifests, perform malware and
keyboard/screen-reader QA, validate premium access-controlled distribution,
and obtain independent QD review plus founder release approval.

**HARD HOLD:** All six tools remain **unreleased**. No public executable,
premium payload, unrestricted download, or production change was made.
