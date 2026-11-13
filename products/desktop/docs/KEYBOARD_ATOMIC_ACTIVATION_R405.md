# Labs R405 — Atomic activation of six-app keyboard shortcuts

**Status:** Draft only, issue #73. Stacked on R404 draft #2357, not production `main`. Independent QD review and founder approval remain hard release holds.

## Reproduced defect (synthetic, not a customer incident)

R404 correctly refused another `install_shortcuts` call after an uncertain Tk registration and best-effort rolled back known callback IDs. But a Tk `root.bind` can install a handler and then raise before returning its ID. That unknown callback is **still executable** after the helper fails, even when retry is forbidden. In particular, if the final Generate or premium Review shortcut is registered before the error, pressing it could invoke its *existing* button command on an incomplete window. The button's own entitlement/human-review checks were not bypassed; the risk is unexpected execution while keyboard installation failed.

## R405 implementation

In `fvs_suite/keyboard_access.py`, each new Tk shortcut handler closes over a local `activated=False` flag. Before successful installation, handlers return Tk `"break"` **without invoking any focus, Browse, Generate or Review operation**. Only after the entire set of `root.bind(..., add="+")` calls returns successfully does the function change `activated=True`. On any registration error, interruption, missing ID or best-effort rollback failure, the flag stays false permanently. Existing pre-registration capability checks, R404 same-root retry hard hold, native widget commands, and unrelated pre-existing bindings are retained.

A failed registration may leave an inert shortcut that consumes its keystroke. The operator must close/recreate the window; no automatic retry is permitted. A successful registration retains the ordinary keyboard behavior and disabled-state/entitlement checks.

## Local test evidence on Git-verified files

- Changed installer blob: `e32e4b816f1083942bcdbaccd29950664effc4f0`.
- New 20-method regression file: `0b56ff373964b59a1fa3018b116d70fa5a2ef8ab`.
- Unchanged, original source dependency `shortcut_targets_r403.py`: `a1e41291fa32ed52d6f972c681bab11f6ffacf9e`.
- Two inherited tests from Git-verified files: `test_keyboard_access_r44.py` (18 methods; blob `508962b11eb0ec9b9daecc0c99c4634a430b4ba7`), `test_keyboard_binding_integration_r403.py` (10 methods; blob `f6a029034beb60662848cc22ee64589897b9f55b`).
- **48/48** methods passed in normal CPython and **48/48** in optimized `-OO -W error` execution: **96/96 focused method executions**. Source compilation also passed. All five source/test files in this focused subset were byte-for-byte checked against their Git blob identifiers. Linux isolated reconstruction only; **not** a full repository integration run or genuine Windows GUI execution.
- Before the patch, these new R405 tests produced **23 failing unittest assertions/subtests**, including the final premium Review shortcut and the six app-shaped failure permutations.
- Coverage includes free and premium launchers; partial first/mid/last registrations, forgotten callback IDs, failed unbind, reentrant calls while binding, `KeyboardInterrupt` and `SystemExit`, native disabled review, successful post-activation Generate/Review, and unrelated existing bindings.

## Remaining release gates

Hosted Windows and Ubuntu workflows are configured to run the new regression file in both standard and optimized mode, but previous R404 runs failed before runner steps: [source #43450269981](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43450269981), [build #43450269957](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43450269957). No observed CI test success can be claimed; precise Actions infrastructure cause remains unconfirmed.

**Next highest-impact step:** Owner inspects failed-run annotations and billing/spending/runner eligibility; restores GitHub Actions runner assignment; then execute full R403/R404/R405 and all six app financial/cryptographic integration suites on Windows + Ubuntu. Follow with six actual Windows x64 executable smoke tests, Defender/AV checks, keyboard + NVDA/high-DPI acceptance, and premium-only protected distribution verification.

No release, merger, public EXE, premium link, customer-data upload, WordPress publication, or QD bypass authorized.
