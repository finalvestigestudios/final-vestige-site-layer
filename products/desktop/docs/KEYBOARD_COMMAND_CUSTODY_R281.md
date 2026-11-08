# Final Vestige Labs R281 — six-app keyboard action custody and inherited test repair

**2026-11-08 · issue #73 · DRAFT / independent QD + founder HARD HOLD · no release**

Base: R280 draft PR #1578 at `f1169cbcdfc9511dd6e33f173f22f9660fab3f07`. This branch must target only the R280 feature branch, **never production main**.

## Confirmed defect and practical risk

The shared `install_shortcuts` helper ensured input, output and optional controls were distinct, but **excluded Generate and premium Review buttons from its identity check**. A mistakenly aliased command button could therefore be invoked by a *focus/Browse* shortcut (or map Generate and gated Review to the same underlying button). That would turn a navigation key into an unexpected report/review action. This is a configuration safety defect, not evidence of an existing production bypass or a live malicious exploit.

The inherited `test_keyboard_access_r44.py` also retained four obsolete shortcut-count assertions from before R226's numeric-keypad bindings. The actual required inventory is now 10 / 16 / 22 bindings for one / two / three ordinary inputs, not 6 / 8 / 10. Those assertions would fail on a working current implementation when full CI resumes.

## Source changes

- `fvs_suite/keyboard_access.py`: **pre-bind** validation now requires a callable `invoke` for Generate and optional Review and distinct object identities across those buttons, all source entry/Browse widgets, output controls and optional Ledger/Invoice/Procurement controls. Invalid configurations raise a privacy-safe `ValueError` before any keybinding is installed; no existing widget command, premium entitlement check, callback handler, native Tab order or root-local shortcut is replaced.
- `tests/test_shortcut_command_custody_r281.py`: ten new headless `unittest` methods exercise all six product shapes, exhaustive action/button alias combinations, missing/bad actions, disabled Generate and Review controls, keyboard-only Browse separation and exact current binding inventories including Num Lock keypad variants.
- `tests/test_keyboard_access_r44.py`: correct four stale legacy count assertions to 10 / 16 / 22. Nothing is removed from that test suite.

## Local verification scope (synthetic/headless, not native Windows)

The exact committed Git blobs of the R281 helper and new test module were evaluated in a local Python 3.13.5 Linux subset containing those two files and a package `__init__.py`. Git blob IDs:

- `keyboard_access.py`: `26d9e3d2fb22aed6ca3e80e764ac2d2684ee2765`
- `test_shortcut_command_custody_r281.py`: `7c161987934b2c8f2379ba9197eea783ed7d0277`

Both commands passed (10/10 each, **20 focused method executions**):

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_shortcut_command_custody_r281.py' -q
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_shortcut_command_custody_r281.py' -q
```

The commands above describe the repository-relative equivalents; the actual runs used the same relative package/test hierarchy within a minimal local `/mnt/data/r281` checkout, not a complete clone. `compileall` of the locally tested module and test passed. The inherited R44 file was updated **but not executed** locally; its four revised counts are directly covered by the R281 inventory tests.

**Not verified:** complete inherited repository suite, real Tk / Windows GUI, native keyboard and screen-reader behavior, Windows x64 PE/Defender, license/payment access controls, signed installers or hosted CI. No customer finance data was used.

## CI / QD / next step

The most recent inspected R280 Windows/Ubuntu [Actions run #42478231163](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42478231163) finished failure **before recorded steps**; neither job had an assigned runner. Cause remains unconfirmed. Restoring runner availability (owner checks Actions billing/spend, workflow permissions and runner allocation) is the smallest unblock. R281 adds a normal `test_*.py` file discoverable by the existing complete desktop unittest suite; its direct focused execution is recorded above, but hosted acceptance is **not** claimed.

**Next highest-impact step:** run full source suite and R279/R280 native pipeline under a trusted CI/Win11 x64 environment, then six genuine EXE builds/sha256/smokes/Defender no-remediation, native accessibility and gated premium delivery verification. Preserve independent QD + founder review.

**Release HOLD:** no production merge, executable publication, public premium artifact/URL, financial compliance decision or release approval.
