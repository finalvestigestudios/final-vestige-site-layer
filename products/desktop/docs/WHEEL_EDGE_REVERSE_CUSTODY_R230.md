# R230 — Precision-wheel boundary and reversal custody (DRAFT / HARD HOLD)

**Scope:** shared `ScrollableForm` used by LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro. The last two remain premium/entitlement-gated. No change to finance/Decimal engines, report provenance, review approval, offline privacy, or website publishing.

## Reproduced failure and correction

At the top or bottom of a scrollable form, a wheel event pointing *outward* was still routed to `canvas.yview_scroll()` and returned `"break"` despite no remaining scroll distance. On Win32, sub-notch movement could also build up the signed `_wheel_remainder`, delaying the user's first precision-touchpad gesture when reversing direction. The complete tests against an R229-style local copy **failed 8 of 23 cases** (not a hosted CI result).

R230 adds `wheel_edge_guard.wheel_points_outward()` to decide native vertical direction from strictly typed event metadata and finite Tk yview geometry. When the wheel points beyond the top/bottom, the shared form returns without scrolling, clears any stale Win32 fraction, and leaves normal reverse scrolling available immediately. When the full form fits without vertical scrolling, Win32 residual state is cleared. The existing nested-dialog and Shift/Ctrl/Alt routing is checked *before* boundary processing, so modified/out-of-scope events cannot clear residual state. X11 Button-4/5, macOS-style deltas, and Win32 partial deltas are covered.

No customer data, entry values, paths, money, records, telemetry, or network calls are inspected by this guard. No compliance decision is automated.

## Immutable source/test custody

- `fvs_suite/wheel_edge_guard.py`: Git blob `4e3af8322f26289312824c931c4f0dc5991be200`
- `fvs_suite/scroll_access.py`: Git blob `35da5fc2345b4c22c5b04e445aed74f909e4c574`
- `tests/test_wheel_edge_guard_r230.py`: Git blob `f2b324f757bbcbcc1ed3d92775218cd6d82368a9`
- `scripts/native_wheel_edge_r230.py`: Git blob `0802e554b22108811f32ecca5a8fb21b0d6457b6`

All four locally executed Python files were compared to their exact Git blob SHA-1 values after upload, including complete content lengths. Synthetic-only Linux x86_64 CPython 3.13.5 / Tk 8.6 / Xvfb acceptance:

1. `PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_wheel_edge_guard_r230.py'`: **23/23 PASS**.
2. `PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_wheel_edge_guard_r230.py'`: **23/23 PASS**.
3. `PYTHONPATH=. xvfb-run -a python -W error scripts/native_wheel_edge_r230.py`: **PASS**.
4. `PYTHONPATH=. xvfb-run -a python -OO -W error scripts/native_wheel_edge_r230.py`: **PASS**.

The native Tk script dispatches actual nested-entry wheel events under Xvfb. It **simulates Win32 delta semantics** on Linux; this is *not* a physical Windows 11 touchpad test. New workflow gates require 23 methods in normal and optimized Python on both Ubuntu and Windows, with two real Tk/Xvfb smoke executions on Ubuntu. Existing inherited R227–R229 coverage remains mandatory.

## Quality and release holds

This is an engineering increment only, on a feature branch stacked on draft R229, not `main`. Hosted GitHub Actions has repeatedly failed before either OS job acquired executable steps (R229 run 42192383298 had `steps:null`). Restore hosted runners and require fresh Windows + Ubuntu step evidence, full inherited six-application source suite, physical Windows 11 wheel/touchpad/NVDA + 100%/200%/400% scaling acceptance, privately built/checksummed/scanned/smoked PE x64 candidates, controlled premium delivery, independent QD review, and founder approval before any release. No executables or download links may be published based on this sprint.
