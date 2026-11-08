# Labs R283 — actual six-app native keypad dispatch (DRAFT / HOLD)

**Scope:** Issue #73; isolated branch `feature/labs-r283-native-keypad-dispatch-20261108`, stacked on R282 at `1a3fe90cc15e4f5064bc5abceec3367ee09d00fc`. Not a release or production approval.

## Gap and delivered artifact

The R282 Xvfb script counted 105 registered Tk bindings and exercised a subset of them. The number of registered callbacks is **not** the number of actual dispatched events, particularly on numeric keypads where X11/Tk converts `KP_1/KP_2/KP_3` into navigation keysyms with Num Lock off.

`products/desktop/scripts/native_six_app_keypad_events_r283.py` now synthesizes **72 actual Tk KeyPress events** against real `ttk.Entry` and `ttk.Button` widgets across LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro. Each required input receives six events: top-row Alt+digit and Ctrl+digit, keypad Alt/Ctrl with Num Lock ON, and keypad Alt/Ctrl with Num Lock OFF. The checker independently asserts the target entry got focus or **only** that input's existing Browse button invoked. Unexpected Generate, Review, output and policy actions fail. All controls are synthetic, with zero customer file reads, network activity or actual financial/compliance approval operations.

X11 modifier states are explicit: `Mod1=0x08`, `Control=0x04`, `Mod2 (Num Lock)=0x10`. This forces Tk to exercise *both* keypad keysym binding paths rather than merely inspecting registrations. The R283 CI gate runs after R282 on Ubuntu Xvfb in normal and optimized Python modes and blocks source-tests on any failed event.

## Reproduced local evidence (2026-11-08 UTC)

Test host: **Linux CPython 3.13.5 with system Xvfb and Tk**. Exact pre-R283 `keyboard_access.py` verified to Git blob `26d9e3d2fb22aed6ca3e80e764ac2d2684ee2765`; R283 script verified to Git blob `c50c3f7248ec88fdf40715b1905d2b15adcc8049`. Commands (from repository root):

```sh
PYTHONPATH=products/desktop xvfb-run -a python -W error products/desktop/scripts/native_six_app_keypad_events_r283.py
PYTHONPATH=products/desktop xvfb-run -a python -OO -W error products/desktop/scripts/native_six_app_keypad_events_r283.py
python -m py_compile products/desktop/scripts/native_six_app_keypad_events_r283.py
```

Results: **72/72 events PASS normal + 72/72 events PASS -OO = 144 actual native synthetic KeyPress dispatch checks**; compilation PASS. Six configurations in each mode. The output reports 72 events in each invocation, **not 105 event executions**. A deliberate local, *uncommitted* negative control redirected the keypad Ctrl+Browse callback to Generate; the script **failed exit 1** with `LedgerDiffLite: KP_1 invoked wrong Browse/Generate/Review`. Restoring the exact source blob restored both passing runs. The mutation was not committed.

## Boundaries / QD hard hold

This is an **Xvfb/Tk event-dispatch integration test**, not a trusted Windows 11 x64 build, physical keypad test, screen-reader acceptance, premium-license verification or six-app complete-regression result. A synthetic GUI proves shortcut routing, not that the six installed launchers have identical real-world keyboard behavior. No customer input, money logic, audit provenance, entitlement or review command changed. No binaries or downloads may be published.

**Next highest-impact work:** restore GitHub Actions runner assignment; run the complete inherited tests and this CI gate against the *exact R283 head*, then privately build and smoke/checksum/Defender-test each of the six actual Windows 11 x64 applications and perform physical keyboard/screen-reader and premium-access-control acceptance. Independent QD and founder authorization remain required before any production or distribution change.
