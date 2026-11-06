# Labs R224 — keyboard access for optional desktop fields (draft / QD HOLD)

**Scope:** Issue #73, six Windows x64 utilities. Based only on R223, not `main`.
**Disposition:** source-only enhancement; NOT a release approval, keyboard/screen-reader certification, or a tested Windows executable.

## Problem and implementation

R223 stacked the invoice-day setting and optional ProcureGuard policy controls into responsive rows, but the existing shortcut installer only provided direct access to mandatory inputs, output, Generate and premium Review. Keyboard users needed to Tab through the entire form to find the optional setting.

- **Invoice Twin Scout:** `Alt+W` focuses the existing **Near-match days (0–365)** Entry. It does not generate a report or change the day value.
- **ProcureGuard Studio Pro:** `Alt+P` focuses its optional local JSON policy Entry; `Ctrl+P` invokes the existing JSON file picker. Neither loads an entitlement nor performs a procurement decision.
- All six apps retain `Alt+1..3` and `Ctrl+1..3` for required source inputs/pickers, `Alt+O`/`Ctrl+O` for output, `Alt+G`/`Ctrl+Enter` for the existing Generate button, and premium-only `Alt+R` for the existing human exception-review button.
- The shortcuts still use window-scoped `root.bind(..., add="+")`, preserving Tab traversal, native Tk controls, and R223 focus-scroll bindings. The on-screen keyboard hint now names both optional workflows.
- The shared installer rejects impossible combinations of optional controls, malformed policy pairs and widget aliasing before binding anything; no customer data, filenames, policy contents or financial amounts are read.

**Security:** shortcuts call the same `focus_set()` or `invoke()` methods as user interaction. Existing premium entitlement checks on app startup, Generate, and Review remain in place; no bypass or automated approval is introduced.

## Focused reproducible test evidence

On Linux CPython 3.13.5 with a local exact source/test working copy:

```bash
cd products/desktop
PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_optional_shortcuts_r224.py' -q
PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_optional_shortcuts_r224.py' -q
python -m compileall -q fvs_suite/keyboard_access.py tests/test_optional_shortcuts_r224.py
```

- **16/16 methods passed** normal and **16/16 passed** `-OO`: 32 focused executions.
- Source/test blobs were checked against the exact GitHub commit after upload.
- Headless tests use fake focusable widgets to verify bindings and behavior, immediate non-execution, optional-control separation, legacy shortcuts, privacy-free failure and preservation of premium-only Review. This is **not a native GUI integration test**.

## Outstanding acceptance / gates

1. Restore GitHub Actions runners. R223 Ubuntu and Windows jobs failed with zero reported execution steps; no hosted test, full repository regression or Windows artifact acceptance is claimed for R224.
2. On a real Windows 11 x64 build at 100/200/400% display scale, test all six apps: keyboard focus sequence, shortcut handling, Ctrl+P file picker cancel, default and changed invoice window, high-contrast and NVDA announcements. Re-run the full native accessibility observer matrix and the 46-check independent review.
3. Privately build, checksum, scan and smoke-test six candidate EXEs. Retain premium offline entitlement and access-controlled distribution; never expose premium binary URLs.
4. Independent QD review and explicit founder approval must precede merging to `main`, site publication or any download.

**No live site edit, real financial data, payment/compliance decision, publicly distributed executable, or unrestricted premium file.**
