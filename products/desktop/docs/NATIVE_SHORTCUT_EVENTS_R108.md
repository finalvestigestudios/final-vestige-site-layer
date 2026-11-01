# R108 — Windows Tk accelerator dispatch and cancellation safety

**November 1, 2026 · Issue #73 · DRAFT / RELEASE HOLD.** Stacked on R107 [PR #434](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/434) at commit `6e7071a159384a023c1edce5d5cdc34d294fec7c`. No production, WordPress, payment, licensing, or download changes.

## Narrow missing acceptance gate

R106 verified that shortcut handlers are registered and that controls participate in native Tk Tab traversal. R107 verified viewport/focus behavior with simulated Tk scaling. Neither proved that a dispatched shortcut *actually invokes* the intended callback, or that a cancelled file picker leaves the input empty and the report generator blocked. This sprint exercises actual Tcl/Tk event dispatch for **the four free source interfaces**, rather than solely inspecting binding metadata.

## Implementation and exact scope

- `scripts/native_shortcut_events_r108.py` creates the real source-owned Tk interface for each of LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, and Policy Delta Desk on a native Windows x64 runner. It sends **Tk-synthetic** Alt+1/2, Ctrl+1/2, Alt+O, Ctrl+O, Alt+G, and Ctrl+Enter key events through the registered root handlers. It verifies **six input focus events**, **six cancelled input dialogs**, **four output-focus and four cancelled output dialogs**, and **eight blocked report attempts** (two per free app). It checks that cancelled paths remain unchanged, no financial engine runs, and no unexpected dialogs open. The CI summary is a fixed string; no paths, field contents, or customer information enter logs.
- The application engine is replaced with a deny-only stub; both file choosers return empty strings; warning dialogs are counted without appearing. This is a **no-customer-data source-Tk probe**, not a test of loading real financial data or actual Windows file picker accessibility. Neither premium application or premium editor is started.
- `tests/test_native_shortcut_events_r108.py` adds **20 synthetic fail-closed unit test methods** covering exact product inventory, events, cancels, missing/extra events, booleans masquerading as integers, invalid premium scope, accidental engine calls, unexpected dialogs and suppressed private diagnostic output.
- `.github/workflows/desktop-build.yml` runs R108 regressions in normal Python and `-OO` on both Linux and Windows, then runs the native Tk event gate **after R9 six-executable PE/SHA/smoke, R105 premium lock, R106 focus and R107 scaled GUI tests**. The existing two evidence-only `upload-artifact` selections remain unchanged. The new gate is release-blocking if a native event is not delivered.

## Reproduction

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_native_shortcut_events_r108.py' -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_native_shortcut_events_r108.py' -v
# Native Windows x64 with a usable Tk desktop, only:
PYTHONPATH=products/desktop python products/desktop/scripts/native_shortcut_events_r108.py
```

Local isolated synthetic tests: **20/20 passed in normal Python and 20/20 in optimized `-OO`** before submission. This tests the source-owned verifier, NOT Windows event delivery. The final exact PR-head GitHub Actions result must be observed separately; never infer a pass from committed code.

## Non-waivable remaining gates

Tk `event_generate` is **not physical hardware keyboard delivery** to the actual packaged EXEs. Source Tk inspections are **not NVDA/JAWS/UIA, WCAG 2.2 AA, Windows 11-specific high-contrast/DPI tests, EDR/AV review, installer code signing, SmartScreen clearance, audited premium license issuance, authenticated premium download controls, manual usability acceptance, QD or founder authorization**. Keep all six EXEs internal until separately approved. This artifact cannot declare a paid entitlement or automatically authorize distribution.