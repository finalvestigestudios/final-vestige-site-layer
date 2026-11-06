# Final Vestige Labs R229 — preserve native wheel modifiers (DRAFT / QD HOLD)

Issue: #73. Base: R228 draft PR #1224, exact parent `b043f6638e5a57fa668ec73dff46f556b4b27383`. Branch: `feature/labs-r229-modifier-safe-wheel-20261106`. Never merge directly to `main`.

## Defect and change

The shared `ScrollableForm` used by all six standalone desktop utilities previously scrolled vertically in response to **Shift+Wheel**, **Ctrl+Wheel**, and **Alt+Wheel**. Those gestures should remain available to native controls / accessibility tools rather than being hijacked by the parent form. R229 adds one pure, strict native state-bit check before calculating viewport geometry or changing the Windows high-resolution wheel accumulator. Shift (0x1), Ctrl (0x4), and Mod1/Alt (0x8) are bypassed. Caps/Num Lock and unrelated mouse-button bits do not suppress ordinary vertical scrolling.

Native state is checked only after the existing viewport ownership test. Invalid non-native states fail closed with a generic exception; booleans and custom conversion-hook objects are not coerced. Legacy synthetic wheel events that omit `state` retain preexisting behavior. X11 Button-4/5 and macOS Aqua modifier gestures likewise bypass the app-level vertical handler. The previously implemented plain Win32 precision-wheel accumulator continues unchanged.

This is purely a shared UI/accessibility fix: no customer value, filename, ledger, input CSV, engine, network endpoint, entitlement key, report or compliance decision is read or changed. Four free and two gated premium apps continue sharing the same form.

## Executed local source-level verification

Linux CPython, real Tk 8.6 + Xvfb, with exactly matching Git source blob hashes:

| Checked-in source | Git blob SHA-1 |
| --- | --- |
| `fvs_suite/scroll_access.py` | `d9201bd79b7b3e2205401f8cab6b0917ae6ef7a6` |
| `fvs_suite/wheel_modifiers.py` | `7d63c855c1b9a21b8abff4901e6400a6384611ca` |
| `tests/test_wheel_modifiers_r229.py` | `49fe9e9b5d6678f97adb2439d9b4680d875fd9b8` |
| `scripts/native_wheel_modifiers_r229.py` | `e29aeaeae1c27d7f719677037c0e918f5b49bb8b` |

- `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_wheel_modifiers_r229.py`: **21/21 PASS**, 0 skips.
- Same command with `python -OO -W error`: **21/21 PASS**, 0 skips. **42 focused unittest method executions**.
- `PYTHONPATH=products/desktop xvfb-run -a python -W error products/desktop/scripts/native_wheel_modifiers_r229.py`: **PASS**.
- Same Xvfb command with `python -OO -W error`: **PASS**. Uses real nested `ttk.Entry` wheel event propagation and simulated Win32 delta behavior; modified events never scroll the viewport or alter a pending -30 delta, while a resumed plain -90 delta scrolls once.
- `python -m compileall -q products/desktop`: **PASS**.
- Tests cover all three modifier masks, combinations, lock keys, huge native mask, strict invalid types/poison conversion hooks, Win32 residual integrity, Aqua/X11 bypass, dialog isolation and legacy no-state events.

## CI and release boundaries

`.github/workflows/desktop-build.yml` now requires the exact 21-test file in **both** normal and optimized Python on Ubuntu and Windows; Ubuntu also mandates two real Tk/Xvfb runs. The historical R228 Actions run #42185069334 failed with Ubuntu and Windows `steps:null`; no runner execution evidence and no confirmed root cause. Check this new head's run before claiming CI pass.

This local Linux/Xvfb test is not native Windows/NVDA/physical touchpad or full six-application validation. All six executables remain unbuilt or unverified for release. No executable or premium download is published. Private Windows x64 PE builds, SHA256, scanning, accessibility checks at 100/200/400% scaling, independent QD review and founder authorization are still required.

**Highest-impact next step:** restore GitHub Actions runner execution, rerun the **unchanged R229 head**, complete full inherited repository suite and physical Windows accessibility acceptance, then privately package/smoke-test all six distinct Windows x64 utilities. Preserve protected premium distribution and QD/founder release hold.
