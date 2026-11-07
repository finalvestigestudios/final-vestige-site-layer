# R266 — redact uncaught Python background and cleanup diagnostics

**Issue #73 · 2026-11-07 UTC · DRAFT / QD + founder HARD HOLD**

Six applications remain **UNRELEASED**: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro. This branch is stacked solely on R265 draft PR #1476 at immutable parent `1eaf0d540b4c87f69650b383ce38ac048ba3fd3e`, not production `main`.

## Reproduced privacy exposure

R265 protected Tkinter callback and R264 protected synchronous GUI startup errors, but CPython's **default** `threading.excepthook` and `sys.unraisablehook` print uncaught thread and destructor failures to stderr. Regression methods reproduced real synthetic customer filenames in both default handlers. These exceptional paths are not protected by Tk callback interception. Even if the current GUI is predominantly synchronous, later worker threads or cleanup failures can disclose financial file locations through desktop stderr and diagnostic captures.

## Implementation

- New `fvs_suite.background_privacy` replaces both process-global hooks with fixed, path-free diagnostics. Neither formatter accesses `exc_value`, traceback, user-data arguments or unraisable object. Thread `SystemExit` stays silent as in the default CPython hook. Forged hook arguments and failed stderr writes do not fall back to the default traceback printer.
- The **shared** `fvs_suite.launcher` installs both hooks before dispatch to any of six GUI apps, `--smoke-test` or `--version`. Setup failure, including failed/silently dropped registration, is a fail-closed exit before GUI/customer input. It preserves the existing network/process audit fence, avoids diagnostic exception chaining, and does not weaken the Tk callback redaction.
- No network, telemetry, cloud processing, money parsing, entitlement issuance, evidence recalculation, automated compliance decision, or premium distribution change. This is a CPython application-level safeguard, **not** a native Windows crash handler, OS firewall, or comprehensive sandbox. Other code can replace these writable Python hooks later; full packaged-app behavior needs native verification.
- The Ubuntu source job and Windows-build job each explicitly run `test_background_privacy_r266.py` in standard and optimized (`-OO`) Python before the existing gates. No public binary or premium asset is uploaded by this change.

## Reproducible local evidence

Linux Python **3.13.5**, process-isolated stdlib regression scripts using **synthetic financial paths**. Code exercised by the test file exactly matched the following **Git blob hashes** in this branch:

| Source | Git blob SHA-1 |
| --- | --- |
| `fvs_suite/__init__.py` | `a3e3f9fdeaf0f74f10077a7299f29f505dbe991f` |
| `fvs_suite/offline_network.py` | `30039ab587cb5a0ce3be305d78d3f919385a2fbf` |
| `fvs_suite/launcher.py` | `ae8eb69bfd45b1094c771cf4a08b37cd2e09b3fc` |
| `fvs_suite/background_privacy.py` | `0ad4ba042a25c5b4a4275fda96f4903182fe4acb` |
| `tests/test_background_privacy_r266.py` | `fb3cc668314ccafff303ef05a1c5bd00d3e9a2cf` |

Commands (repo root, `PYTHONPATH=products/desktop`):
```sh
python -m unittest discover -s products/desktop/tests -p 'test_background_privacy_r266.py'
python -OO -m unittest discover -s products/desktop/tests -p 'test_background_privacy_r266.py'
python -m py_compile products/desktop/fvs_suite/background_privacy.py products/desktop/fvs_suite/launcher.py products/desktop/tests/test_background_privacy_r266.py
```
**Result:** 16/16 normal methods PASS + 16/16 optimized methods PASS = **32/32 local test-method executions**, including real CPython child-thread and destructor exceptions for all six application identifiers. Python compilation PASS. Baseline default hooks were independently observed leaking *synthetic* financial filenames. GUI and smoke interfaces were stubbed only to invoke the **actual shared launcher and background/offline modules** without a display. No real Windows executable or financial records were used.

## Remaining release blockers

At R265, [run #42413630989](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42413630989) had both Ubuntu/Windows jobs fail before any recorded steps. An R266 workflow trigger is **not** evidence that jobs executed. Owner must check Actions billing/usage restrictions, workflow policy/permissions and hosted runners, then rerun the unchanged R266 commit. Inspect job steps and logs before citing any hosted PASS.

Next highest-impact step: genuine Windows 11 x64 private build and smoke/GUI/accessibility verification of all **six** executables; independent SHA-256 and malware checks; protected entitlement and distribution verification for both premium binaries. No live download link or publication until independent QD review and founder release approval. The chain of draft PRs is **not** approved for merging.
