# R282 — repair inherited keyboard CI failures; exercise six native Tk variants

**Status:** Draft only. Issue #73. Independent QD and founder approval remain mandatory. No Windows binary, public download, premium asset, or production change.

## Failure found and repaired

R226 introduced two keypad keysyms for each source field (four new keybinding sequences per field) while two older CI checks remained frozen to pre-R226 counts:

1. `tests/test_optional_shortcuts_r224.py::test_one_input_no_optional_shortcuts` expected exactly six sequences; the current helper correctly emits **ten** with `KP_1/KP_End` aliases. The old six-item expectation was reproduced locally as one **failing** test. R282 updates the expected exact ordered tuple.
2. `scripts/native_ledger_headers_r225.py` rejected any LedgerDiff configuration with more than **12** bindings, even though the current two-source LedgerDiff helper emits **20**. R282 updates this guard without loosening the no-callback condition.

No application engine or entitlement workflow was modified.

## Native GUI evidence added

`scripts/native_shortcut_actions_r282.py` drives **real tkinter/ttk widgets and native Tk event delivery** under Xvfb for all six variants, with expected per-app binding inventories:

| App | Expected native bindings |
| --- | ---: |
| LedgerDiff Lite | 20 |
| Invoice Twin Scout | 11 |
| SpendMap Lite | 10 |
| Policy Delta Desk | 16 |
| GrantAudit Studio Pro | 23 |
| ProcureGuard Studio Pro | 25 |
| **Total** | **105** |

For each variant the test rejects aliased Generate/Browse buttons before any binding, checks input and output focus, confirms Browse invokes the existing widget command, verifies blocked generation when validation denies it or the button is disabled, and verifies successful synthetic generation only via the enabled button. It also checks LedgerDiff Alt+R header focus, Invoice Twin near-match focus, ProcureGuard policy focus/Browse, and both premium review buttons' denied, disabled, and allowed paths. These are **synthetic application gate commands**, not real entitlement approval or compliance decisions.

A new two-mode Ubuntu/Xvfb job step runs the native script on PRs, and the corrected inherited R225 native check remains part of its existing CI gate. No changes to hosted release actions or Windows artifact exposure.

## Executed evidence (Linux Python 3.13.5, Xvfb, 2026-11-08)

- Previously stale R224 six-key expectation: **1/1 reproduced failure** against the exact committed R281 helper.
- New R282 native Tk script: **PASS normal; PASS `-OO`**; each mode validates all six configurations and 105 registered sequences (2 complete suite passes; **not** 210 independent test methods).
- Corrected R225 native Tk script: **PASS normal; PASS `-OO`**; four actual Tk header-focus event deliveries and zero action callbacks per mode.
- Verified local test sources byte-exact to Git blobs: shared helper `26d9e3d2fb22aed6ca3e80e764ac2d2684ee2765`, R282 native script `de267c4f2481d36cd81f432dd07952596042220a`, corrected R225 native script `13d4bb37354d2a9978fb2086d7b32d2b2606f97f`.
- **Not yet executed:** entire inherited R224/R44 and repository test suite, hosted Ubuntu/Windows jobs for R282, a real Windows GUI accessibility audit, native Windows builds, Defender scans, and protected premium delivery. The CI infrastructure failure observed through R281 remains under investigation.

## Reproduction

```sh
PYTHONPATH=products/desktop xvfb-run -a python -W error products/desktop/scripts/native_shortcut_actions_r282.py
PYTHONPATH=products/desktop xvfb-run -a python -OO -W error products/desktop/scripts/native_shortcut_actions_r282.py
PYTHONPATH=products/desktop xvfb-run -a python -W error products/desktop/scripts/native_ledger_headers_r225.py
PYTHONPATH=products/desktop xvfb-run -a python -OO -W error products/desktop/scripts/native_ledger_headers_r225.py
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_optional_shortcuts_r224.py'
```

## Next highest-impact gate

Restore GitHub Actions runner allocation and execute the full inherited test suite on this exact immutable branch/commit. Inspect failed jobs, repair any additional stale post-R226 assertions, then run the private trusted Windows 11 x64 six-EXE build/smoke/SHA-256/Defender pipeline. Physical keyboard, screen reader, and premium license/access verification remain required; **QD+founder HARD HOLD**.
