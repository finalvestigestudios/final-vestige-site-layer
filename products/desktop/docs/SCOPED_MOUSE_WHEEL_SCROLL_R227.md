# R227 — Six-app scoped wheel scrolling for narrow/high-DPI forms

**2026-11-06 UTC · Issue #73 · DRAFT / QD + founder release HOLD.** This change is stacked on R226 draft PR #1212, exact starting SHA `98147658136c79e7efd6113ad0eedadeee08ab78`, not production `main`.

## Problem and implemented behavior

The R107 shared `ScrollableForm` previously exposed a visible scrollbar and focus-driven viewport reveal, but **no mouse-wheel bindings**. Users of the six standalone Windows desktop forms, especially those using high DPI and long vertically stacked field sets, could use the scrollbar or Tab but not roll a wheel over a nested input. R227 adds a narrow, shared UI-only capability to `fvs_suite/scroll_access.py`:

- Root-local `<MouseWheel>`, `<Button-4>` and `<Button-5>` bindings; **never `bind_all`**. Only events whose actual widget is a descendant of this exact viewport can move it. Events from dialogs/other top-levels are ignored.
- Deterministic, integer-only wheel scaling: 3 Tk units per notch, capped at 12 units per event. Direction maps Windows/macOS deltas and X11 buttons 4/5, including nonzero high-resolution deltas. Zero delta and non-scrollable forms leave other handlers intact.
- The handler never calls `.get()`, reads file paths, accesses financial values, emits telemetry, or triggers Browse, Generate, license, or human-review callbacks. Existing keyboard shortcuts, focus reveal, and premium entitlement gate are unchanged.

## Committed evidence and reproduction

- `fvs_suite/scroll_access.py` blob **06082badbbc31afc6bea19d25305d38a1caeb8b7**.
- `tests/test_wheel_access_r227.py` blob **11ba4ba84393c4ceca584c2644ec4fca9efc3267**, 12 cases covering both platform wheel types, huge/zero/invalid/bool deltas, input-read rejection, root/modal isolation, inherited visible form, and optimized-mode assertions.
- `scripts/native_wheel_smoke_r227.py` blob **c96bcbce2b5238bc7113d2b1fba05bbd3813cd17**. Real Tk event delivery through a nested `ttk.Entry`: `<MouseWheel>` and X11 `<Button-5>` both move an overflowing canvas; a separate Toplevel's wheel does not move the parent.
- Workflow `.github/workflows/desktop-build.yml`: mandatory 12-test normal + `-OO` gates on **both** Ubuntu and Windows source/build lanes; on Ubuntu, two additional real-Tk Xvfb smoke invocations. None of this uploads an executable.

**Actually executed on Linux CPython 3.13.5 / Tk 8.6 with synthetic widgets:**
```sh
cd products/desktop
PYTHONPATH=. PYTHONWARNINGS=error python -m unittest discover -s tests -p test_wheel_access_r227.py -v
PYTHONPATH=. PYTHONWARNINGS=error python -OO -m unittest discover -s tests -p test_wheel_access_r227.py -v
xvfb-run -a env PYTHONPATH=. PYTHONWARNINGS=error python tests/native_wheel_smoke_r227.py
xvfb-run -a env PYTHONPATH=. PYTHONWARNINGS=error python -OO tests/native_wheel_smoke_r227.py
```
**12/12 PASS normal; 12/12 PASS optimized; 24/24 unittest method executions, zero skips. Real Tk smoke PASS in both modes.** `compileall` PASS. The source and both committed test artifacts were independently compared against locally executed Git blob SHA identities. This is an isolated *three-file* reconstruction, not an intact checkout's inherited integration suite or Windows x64 hardware observation.

## Non-waivable QD/release gates

Do not claim accessibility certification, Windows 11 100/200/400% wheel and precision touchpad behavior, packaged EXE support, screen-reader parity, native keyboard/NVDA, stable Windows CI, financial-engine full regression, malware/Defender scanning, or paid license/distribution approval from these Linux results. All six products remain unreleased; the two premium applications remain entitlement-gated. Keep source review and physical Windows acceptance independent. No `main` merge, WordPress release, public executable or unrestricted premium file.

**Next highest impact:** restore the Actions runner allocation currently failing before any steps; rerun this exact draft head, execute the inherited six-engine suite plus native Windows 11 tests at 100/200/400% and mouse-wheel/precision-touchpad checks, then privately build/checksum/scan/smoke-test all six Windows x64 images and obtain QD + founder signoff.
