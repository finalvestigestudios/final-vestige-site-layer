# R44 — Keyboard access for all six desktop applications

**Scope:** Source-level Tkinter usability improvement, not a verified Windows
release, an assistive-technology certification, or permission to publish.
The same behavior is used by LedgerDiff Lite, Invoice Twin Scout, SpendMap
Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro.

## Keyboard controls

| Shortcut | Action |
| --- | --- |
| Alt+1 through Alt+3 | Focus the corresponding required input path (only existing fields) |
| Ctrl+1 through Ctrl+3 | Open that input's existing file picker |
| Alt+O | Focus the output directory |
| Ctrl+O | Open the output directory picker |
| Alt+G or Ctrl+Enter | Activate the existing Generate review report button |
| Alt+R | Activate the existing human exception review button, premium only |
| Tab / Shift+Tab | Native Tk keyboard focus traversal |

A visible help line lists the available input count and keyboard commands.
On opening a window the first required input receives focus. Dialogs belong
to the app window so they are less likely to appear behind it. The Tk root
and content frame expand when the window is resized.

The shortcut layer invokes existing Tk buttons; it does **not** call an
engine, load a report, select a customer file, read a license, or bypass
premium entitlement validation. A disabled widget's invoke remains disabled.
No hotkeys are installed system-wide.

## Reproducible source-only verification

From the full repository checkout:

    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_keyboard_access_r44.py -v
    PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p test_keyboard_access_r44.py -v
    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v

The R44 focused tests require no GUI display, customer records, network, or
installed license. They cover 1/2/3 input-field layouts, shortcut uniqueness,
focus, browse, generate/review command delegation, and disabled buttons.

## Manual Windows 11 x64 acceptance still required

Use actual Tk windows on a clean-machine VM for all six products.
Check keyboard navigation, high-DPI text and minimum window size,
Alt/Ctrl shortcut behavior with native file pickers, focus return after
cancelling dialogs, Narrator/NVDA labels, contrast, visible focus, and
screen-reader announcements of errors. Test both premium tools with
untrusted/no entitlement to confirm they remain locked. Record results,
screenshots without client data, and reviewer approval before release.

**Release HOLD:** These headless tests do not prove built EXEs, native GUI
accessibility, AV clearance, premium access controls, or QD approval.
