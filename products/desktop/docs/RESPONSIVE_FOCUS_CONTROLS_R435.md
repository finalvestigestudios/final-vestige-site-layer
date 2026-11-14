# R435 — narrow-viewport reflow and extended keyboard focus (DRAFT / HARD RELEASE HOLD)

Issue: [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Applies to the shared source-level Tk scrolling form used by **LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro**. No executable or download was released.

## Two concrete accessibility defects

1. `ScrollableForm._canvas_resize` previously forced `wraplength >= 100` pixels for every tracked label even when the entire canvas was narrower. At 400% scaling or small windows, a forced 100-pixel text wrap could exceed the available interior width, creating clipping. R435 uses `max(1, event.width - 72)`: at canvas width 80, the requested label wrap is now **8px**, not 100px; at width 500 it stays **428px**. Tk will still determine actual font geometry and column widths; this is a targeted clipping fix, not a WCAG certification.

2. `ScrollableForm._focus_reveal` previously handled only `ttk.Entry` and `ttk.Button`, leaving common Tab-focusable widgets without scroll-to-focus when obscured. R435 adds classic Tk `Entry`, `Button`, `Text` and themed `Combobox`, `Spinbox`, `Checkbutton`, `Radiobutton`, `Treeview`. The existing same-root and actual viewport-descendant checks remain in force; no focus event from a sibling or child dialog may move this canvas.

No changes were made to financial parsers, Decimal money logic, source hashes, evidence manifests, payment decisions, audit history, license checks, premium assets, telemetry, or site publishing. The focus handler reads only window geometry; it does not call any control's `get()` or read label text.

## Regression evidence and exact scope

New file `products/desktop/tests/test_responsive_controls_r435.py`: **18 tests**, with eight narrow widths, normal-width compatibility, zero/negative widths, multiple labels, empty label lists, private-label getter traps, eight additional focus classes, unrelated root siblings, child dialogs and private financial-value getter traps.

Locally executed on **Linux Python 3.13.5**, using a standalone projection of the affected R435 methods, synthetic widget hierarchies and the *exact committed test-file bytes* (Git blob `1205a3c86c6d8a63dfbba9b6e73b0944b0a6c6b9`):

- Standard `-W error`: **18/18 passing**.
- Optimized `-OO -W error`: **18/18 passing**.
- Source/test compilation: **passing**.
- Controlled pre-fix projection (restored 100px wrap minimum and two-class filter): regression suite failed. This does not establish a production incident.

**Limit:** This is a projection test, not a run of the entire committed `scroll_access.py` module with real Tk widgets, a full repository checkout, native Windows, screen-reader behavior or actual 400% display scaling. Do not call this 36 complete application tests.

The independent `.github/workflows/desktop-source-evidence-r385.yml` now queues the committed **real module + 18 exact tests**, in normal and optimized mode on both **Ubuntu 24.04 and windows-latest**, alongside inherited R434/R107 accessibility gates. A pass requires actual runner steps and their logs, not just workflow registration.

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_responsive_controls_r435.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_responsive_controls_r435.py
```

## Release gates and review

Retain feature-branch isolation, stacked draft PR review, independent QD validation and explicit founder approval. Before any of the six Windows x64 executables is offered: get a **real hosted CI run**, run the full six-engine, cryptography, entitlement and financial regressions, manually exercise Tab/Shift+Tab focus and 400% reflow on Windows 11 including dropdowns/tables/dialogs, build and smoke-test each executable, Defender scan, checksum/version each binary, and verify separate restricted premium distribution. No downloads, licensing bypass, payment flow, production deployment or site changes are permitted by this sprint.

The immediate infrastructure blocker is previous GitHub Actions jobs failing with **zero recorded steps/no assigned runner**. Check organization/repository Actions billing/spending eligibility, workflow permissions and runner policy; capture a logged Ubuntu/Windows run. A missing log does not establish a particular billing or policy cause.
