# R532 — scrollable, bounded F1 help for all six Windows utilities

**Date:** 2026-11-18. **Issue:** #73. **Base:** R531 draft PR #3051 SHA `44c9f7872c97973f4a01f7806dca6afe50de7c39`. **Status:** draft, source-only, QD/founder HOLD.

## Defect and implemented change

R530 introduced F1 discovery and R531 formatted shortcut lines, but Tk `messagebox.showinfo` has no scrolling/resizing. At 400% display scaling a long legend may be clipped. R532 replaces that unscrollable modal with a bounded, resizable Tk Toplevel containing a read-only, keyboard-focusable Text widget and vertical scrollbar. Users can scroll with keyboard or mouse, close with Escape or the explicit Close button, and return to the prior focused control.

This shared path applies to LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro.

- Validates the statically authored shortcut legend *before* creating a window; no financial fields, filenames, license tokens, paths or customer records are read.
- Restricts each root to one existing help window; repeated F1 raises it. A destroyed window can be replaced.
- Uses screen-bounded geometry (maximum 760x480, margin 64 horizontal/96 vertical) and a scrollable read-only Text with keyboard focus. No global key registration or global modal grab.
- Escape, Close button and window-manager X dismiss help and restore previous widget focus if alive; failures during construction clear/destroy the partial window.
- Generate/Browse and gated premium Review stay on their original widget commands. Financial Decimal arithmetic, local-first privacy, human review, audit trail and entitlement logic are unchanged.

## Changed files

1. `products/desktop/fvs_suite/keyboard_access.py`: new `show_keyboard_help` function.
2. `products/desktop/fvs_suite/app.py`: F1 uses the new shared function for six launchers.
3. `products/desktop/tests/test_keyboard_access_r44.py`: 20 headless constructor-mocked regression methods for scrolling, read-only focus, single window, cleanup, geometry, Escape/Close, redaction and invalid input.
4. This document. Existing 416-command source inventory and test filenames unchanged.

## Test evidence and unverified gates

Local Linux CPython 3.13.5 isolated extract of the new helper with mocked Tk constructors passed **20/20 standard Python** and **20/20 optimized `-OO`**, 40 focused executions. These tests were run on a standalone exact implementation of the new helper, *not* by executing the committed test module or native Windows Tk. They are not accessibility certification. The entire committed R44 test module, 416-command source matrix and native Windows binary tests remain outstanding.

Reproducible commands at the R532 branch head:

```sh
cd products/desktop
python -m unittest discover -s tests -p 'test_keyboard_access_r44.py' -v
python -OO -m unittest discover -s tests -p 'test_keyboard_access_r44.py' -v
cd ../..
python -B -W error products/desktop/scripts/source_evidence_runner_r509.py
```

Native Windows 11 validation: each of six EXEs at 100%, 200%, 400% scaling; F1, repeated F1, scroll keys/mouse/scrollbar, resize, Escape, Close, X, focus restore, high contrast and Narrator/NVDA behavior. Confirm all instructions accessible and no Generate/Browse or premium Review bypass. Then full packaging, fresh VM smoke, Defender, SHA-256 and premium-entitlement/download checks.

GitHub Actions runner-start failures tracked in #75. An administrator must restore one job with real step logs before calling hosted tests passed. All changes remain a **draft feature branch**. QD independent review and explicit founder approval are prerequisites for merge or WordPress publication; catalog page 1612 remains draft. Never publish untested EXEs or unrestricted premium binaries.
