# R225 — LedgerDiff optional CSV header keyboard access (draft / QD HOLD)

Tracking: [six-app Labs issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). **No production merge, EXE release, or accessibility certification.**

## Concrete change

LedgerDiff Lite already provides two configurable match-key CSV column names and two optional amount-column names. The R223 responsive form made those fields visually reachable at high DPI, but R224 supplied direct keyboard shortcuts only for mandatory inputs and two other applications' optional controls. A keyboard-only operator otherwise had to traverse the entire Ledger form to reach its four header fields.

R225 retains the four actual `ttk.Entry` widgets in visual order (left match, right match, left amount, right amount) and passes them to the shared installer. Mnemonics are:
- **Alt+L**: focus left match-key header.
- **Alt+R**: focus right match-key header (LedgerDiff only; this remains the Review shortcut on premium apps).
- **Alt+A**: focus left amount header.
- **Alt+M**: focus right amount header.

Shortcuts do **not** open files, change values, generate reports, or approve decisions. Original source selection, output, Generate, and premium human Review callbacks remain the sole execution paths. The existing zero-telemetry, offline and Decimal-safe engines are untouched. Existing `Alt+1..3`, `Ctrl+1..3`, `Alt+O`, `Ctrl+O`, `Alt+G`, `Ctrl+Enter`, Invoice `Alt+W` and procurement `Alt+P`/`Ctrl+P` remain in place.

The shared shortcut installer refuses to bind Ledger controls when the expected four widgets, exactly two required input pairs, or free-only optional-control contract is violated; it checks all widget identities before binding. It also rejects mixing Ledger header shortcuts with Invoice, ProcureGuard, or premium Review controls. The visible LedgerDiff keyboard hint explains the new shortcuts.

## Actual test evidence and limits (2026-11-05 PST)

**Executed locally:** Linux CPython **3.13.5** against `keyboard_access.py` with Git blob **`70d8e6cabb55487485456b517bbda8628128d99c`**, byte-identical to the branch version. A separate 25-method focused headless fixture test module (not the 17-method checked-in GitHub file) passed:

```bash
cd products/desktop
PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_ledger_header_shortcuts_r225.py' -q
PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_ledger_header_shortcuts_r225.py' -q
python -m compileall -q fvs_suite/keyboard_access.py tests/test_ledger_header_shortcuts_r225.py
```

**25/25 PASS** normal, **25/25 PASS** optimized, **50 test-method executions**, Python compilation PASS. Tests model widget focus, callback isolation, deterministic add-only bindings, legacy shortcuts, premium review separation, invalid counts, malformed optional fields, and widget aliasing. No customer data used.

**Important distinction:** 17 new regression methods are **committed to** `tests/test_ledger_header_shortcuts_r225.py`, but those exact checked-in tests and the complete repository suite have **not** been executed locally. The local 25-method fixture is separate, albeit using the exact committed production shortcut module. The GUI app wiring, real Tk event delivery, physical Windows keyboard/NVDA and 100/200/400% scaling, and all six native Windows x64 EXEs are **unverified**.

Both Ubuntu `source-tests` and Windows `windows-build` now explicitly invoke the checked-in 17-method R225 file in normal and `-OO` modes. Previous R224 [Actions run #42160413227](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42160413227) completed failure with both jobs showing `steps:null` (no verified test execution). [R225 Actions run #42165972815](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42165972815) on this draft PR also completed **failure**. Ubuntu `source-tests` job `127722422192` and Windows `windows-build` job `127722422470` both had `steps:null`; separate steps queries returned empty lists, and the Ubuntu log request returned HTTP 404 `BlobNotFound`. No hosted source test, Windows build, or native accessibility probe is verified. The root cause remains unconfirmed (runner/account/billing/permissions must be checked).

## Next release gates

1. Restore GitHub Actions execution; inspect account/org billing/usage limits, runner allocation, and prestart error banner. Rerun the **unchanged R225 commit** and complete all inherited source tests.
2. Verify the actual `ttk.Entry` focus and auto-scroll after Alt+L/R/A/M on Windows 11 at 100/200/400% scale with NVDA/high contrast; verify Alt+R triggers only premium Review on premium apps.
3. Privately build all six Windows x64 candidate EXEs. Check SHA256, Defender/EDR, offline startup, keyboard/scroll behavior, input/output provenance and premium entitlement enforcement.
4. Independent QD review and founder authorization before any PR merges, WordPress changes, public downloads or premium delivery. All six programs remain **unreleased**.
