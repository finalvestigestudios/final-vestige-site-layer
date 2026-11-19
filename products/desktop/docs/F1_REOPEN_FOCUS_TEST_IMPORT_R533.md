# Labs R533 — F1 help reentrancy, keyboard focus and committed-test import repair

**Status:** Source change only, draft PR / QD + founder HARD HOLD. Parent is R532 draft #3056 at `72a30bcdb13fabe33cfeb89d14b648becb35efe4`. Do not merge to production or deploy downloads without independent approval.

## Verified defects at parent R532
1. The 20 committed R532 GUI regression methods in `tests/test_keyboard_access_r44.py` call bare `show_keyboard_help(...)`, but the test module imported only `install_shortcuts` and `format_keyboard_help`. That name raises `NameError` at runtime when the affected methods execute. The R532 isolated helper checks do not validate the full committed test module.
2. Reopening an already-visible F1 help window called only `lift()`. Window z-order changed, but the keyboard could remain focused on the original input; arrow keys could then edit/operate the form instead of scroll/help navigation.
3. Repeated Escape/window-manager close callbacks could destroy the same dialog more than once and attempt to restore focus repeatedly. A Tcl window-destruction race could prevent the intended focus restore.

## Source changes
- Correctly import `show_keyboard_help` into the existing inventoried R44 test module. **Nine** additional `test_r533_*` regression methods cover import identity, help-text ownership, repeated-F1 focus, legacy dialog fallback, child loss, close idempotence, Tcl destroy races and stale-window lift recovery.
- The shared Tk F1 helper remembers the read-only text widget on the help dialog; a repeated F1 raises the existing window **and** focuses its text for keyboard navigation.
- The close handler is idempotent; repeated Escape or X cannot destroy twice. Expected `tk.TclError` during window teardown is handled without losing the prior-focus restoration attempt.
- All six products use the same helper via `fvs_suite/app.py`; no Generate, Browse, reviewer, premium entitlement, ledger, money or source-file handling was changed.

## Local test evidence (limited scope)
- A standalone Linux CPython harness executed `show_keyboard_help` copied **byte-for-byte as a function** from the committed R533 branch. FNV32 fingerprint of that extracted helper: `8cc955f1` (also recomputed from GitHub branch source). Tk widgets mocked; valid static help text provided by a minimal formatter stub.
- **14/14 PASS** normal CPython, **14/14 PASS** with `python -OO`: 28 focused test executions total; 9 represent newly committed R533 scenarios, 5 are earlier R532 behavior checks.
- **Not executed:** the entire committed `test_keyboard_access_r44.py`, the 416 pinned source commands, a Windows-native Tk window, Narrator/NVDA tests, actual app EXEs, Defender scans, installation/checksum checks, premium download/entitlement validation. The local harness is *not* a substitute for those gates.
- R532 head's previously inspected three workflows all failed **before steps** (six jobs with `steps=null`), tracked in #75; request fresh exact-R533 CI and review jobs before any approval.

## QA release acceptance
1. Unblock one GitHub Actions runner (check Actions billing limits, runner availability and workflow policy; capture actual startup banner/step log).
2. On the exact R533 head, run `cd products/desktop && python -m unittest discover -s tests -p test_keyboard_access_r44.py -v`, then `python -OO -m unittest discover -s tests -p test_keyboard_access_r44.py -v`. Run all 416 pinned source commands and full CI matrix.
3. On Windows 11, launch each of the **four free** products (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and **two gated premium** products (GrantAudit Studio Pro, ProcureGuard Studio Pro). At 100%, 200% and 400% display scaling, press F1 twice (including after moving focus to the form); verify text regains keyboard focus, scroll works, and only one window exists. Check Close/Escape/X, re-open, and Narrator/NVDA; verify no Generate or premium Review runs unexpectedly.
4. Package/smoke test all six Windows x64 binaries, scan with Defender, record SHA-256 checksums and confirm premium distribution remains gated. Do not publish any binary or checkout link until signed-off QD review and explicit founder approval.

No customer data, file paths, financial records or entitlement secrets were transmitted for this change. No WordPress or production branch write.
