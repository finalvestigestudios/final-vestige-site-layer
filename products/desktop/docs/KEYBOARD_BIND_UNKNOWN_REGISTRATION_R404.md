# Labs R404 — Indeterminate Tk shortcut-registration hold

**Status:** DRAFT only; issue #73. Stacked on R403 draft PR #2350, never production `main`. Independent QD and founder approval remain mandatory. All six Windows x64 apps remain unreleased.

## Reproduced failure mode

`keyboard_access.install_shortcuts` uses additive, window-local Tk bindings. The prior R403 code rolled back callback IDs returned by previous `bind` calls. But `root.bind` itself can register a callback then raise **before returning its callback ID**. If the earlier returned bindings were rolled back cleanly, R403 left `_fvs_shortcuts_installed` false. A second installer call could add a second Generate/Review callback over the unknown first registration, duplicating operations or reviewer actions.

This is an adversarial/synthetic control-flow finding; no customer incident is asserted.

## Exact change

The window is conservatively marked `_fvs_shortcuts_installed=True` **before the first `root.bind`**, after all R403 preflight and alias validation succeed. Any failure or interruption, even one with apparently complete rollback of known IDs, leaves the flag set. Rollback of returned callback IDs still proceeds best-effort, preserving unrelated preexisting application handlers; it now also runs on `KeyboardInterrupt` and `SystemExit`, then re-raises the original failure. **Never automatically retry in the same Tk root** after a failed binding attempt. Dispose of the window and construct a new root to retry under operator control.

Successful keyboard sequences, focus targets, existing Generate/Review widget commands, disabled-state checks and premium entitlement/human review guards are unchanged. No financial documents, paths, money, audit journals, network or entitlement records are accessed.

## Exact-source test evidence

Local Linux CPython 3.13.5 with directly fetched R403 Git blobs and committed R404 source/test bytes:

- `keyboard_access.py` Git blob `8188c9558d877665eb6a334f932a364d57fbcdc9`.
- `test_keyboard_bind_uncertain_r404.py` Git blob `1cc2e61085292eda7fa78eb32a0114ea07632f13`.
- R403 `shortcut_targets_r403.py` unchanged Git blob `a1e41291fa32ed52d6f972c681bab11f6ffacf9e`.
- **71/71** focused unittest methods PASS in normal `python -W error` and **71/71** in `python -OO -W error`: **142/142 method executions**. This includes 19 new R404, 10 inherited R403 binding integration, 24 inherited R403 preflight, and 18 inherited R44. `compileall` passed. All five source/test Python files used for this subset matched their exact Git blob SHAs; the tests were run in a partial local reconstruction, not a complete checkout.
- Replayed the 19 new R404 methods against exact prepatch R403 `keyboard_access.py` Git blob `c1839246200003cb36e973913b60a57e45d448bb`: **15 expected failures** (including all six app-shape subtests), reproducing the weak retry contract.
- Synthetic cases include a callback already installed when `bind` raises, early/mid/last action failure, unknown callback ID, failing unbind, `KeyboardInterrupt`/`SystemExit`, six application control shapes, and premium disabled review.
- These are no-display synthetic control-flow tests, **not** six real Tk desktop GUIs, a full checkout suite, genuine Windows x64 validation, accessibility acceptance, or packaging tests.

## Release hard holds

GitHub Actions source/build workflows have previously failed before runner assignment, including R403 source [#43440015971](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43440015971) and desktop build [#43440016202](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43440016202). A check-run summary indicates annotations exist, but the available authenticated GitHub connector cannot retrieve the check-run annotation endpoint; the **cause remains unverified**. The R404 dual-OS CI job includes these 19 tests in both normal and optimized modes, but is not evidence until a runner executes.

**Next highest-impact step:** Owner inspects failed-run annotation banners and Actions billing/spending/runner eligibility, restores runner allocation; then run all R403/R404 and inherited keyboard suites on Windows and Ubuntu, full six-app Decimal/provenance/crypto regressions, six genuine Windows x64 packaged executable smoke/Defender/NVDA/high-DPI checks, and premium distribution/access-control testing. No release or website publication before independent QD/founder approval.
