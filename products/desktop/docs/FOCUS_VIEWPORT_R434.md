# R434 — six-app focus visibility at high DPI (DRAFT / HARD HOLD)

Issue: [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This is source-only accessibility engineering; **no application is released**.

## Defects and repair

The shared Tk `ScrollableForm` is used by all six app forms. A focusable control taller than the available viewport cannot have both edges visible. Before R434, the visibility algorithm kept trying to bring the bottom edge into view; it could move the control's **beginning out of view** even though that beginning was already visible. R434 instead prioritizes the top of an oversized focused control and leaves it alone once its beginning is visible.

A second problem was root-local `<FocusIn>` delivery. The event could originate in a focusable widget owned by the same root but **outside** this form's scroll canvas. R434 requires the target to descend from the actual viewport before scrolling; unrelated root-owned controls and child dialogs cannot drive form navigation.

Short normal Entry/Button controls, native Tab order, button commands, report processing and premium entitlement/review decisions are unchanged. No customer content, paths or network are read.

## Measured regression evidence

New test source: `products/desktop/tests/test_focus_viewport_r434.py` (11 methods):
- Oversized offscreen control reveals start rather than end.
- Oversized control with visible start does not jump.
- Partially obscured start is revealed.
- Short visible and offscreen controls, non-scrollable content remain compatible.
- A root-owned sibling cannot scroll the form; nested entry can.
- Child dialogs, non-Entry/Button events and private-value getters are not inspected.

Red/green reproduction in an **isolated Linux Python projection of the touched production methods** (not a complete checkout):
- Pre-fix: 3/11 tests **failed** (oversized offscreen, oversized visible start, unrelated root sibling).
- Post-fix: the 11 R434 methods **plus 15 inherited R107 scroll-math expectations** passed under each mode: **26/26 standard + 26/26 `-OO -W error` = 52 projected executions**. Source compilation passed. (The inherited projections were copied from the R107 scroll-math class, not the full R107 native-scale test module.)
- Actual committed GitHub production module and committed test are **not yet executed together**: the local projection contains only the touched methods and stub imports. Hosted Ubuntu/Windows CI remains required for Git-blob-matched evidence.

Required full-checkout commands, both operating systems:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_focus_viewport_r434.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_focus_viewport_r434.py
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_scroll_access_r107.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_scroll_access_r107.py
```

These tests are now queued in `.github/workflows/desktop-source-evidence-r385.yml` for Ubuntu and Windows. CI can only certify these once a runner actually starts and produces logs.

## Release/verification boundary

Source tests do **not** certify WCAG, screen readers, Windows 11 400% reflow, physical keyboard use, installers, SHA-256 candidate provenance, Defender, premium download authorization or customer availability. Perform physical keyboard/Tab/focus and scroll checks on the six real Windows x64 executables before any release. Retain original CSV inputs, deterministic SHA-256 audit artifacts, Decimal-safe accounting, no-default-telemetry and human review for compliance decisions. Keep the draft stacked on R433, with independent QD and explicit founder authorization mandatory before any merge, site publication or release.

**Immediate blocker:** previous exact R433 Ubuntu/Windows Actions jobs had no recorded runner or test steps. Check repository Actions settings, runner availability and billing/spending restrictions; obtain one logged workflow execution. Do not infer a cause from an empty job log.
