# Labs R264 — synchronous GUI launch diagnostic privacy

**Issue #73 · DRAFT ONLY · independent QD and founder release HARD HOLD**

This change is stacked on R263 draft PR #1460 at immutable parent
`e8d37a6a24222f648ae99a9e27aa32c734d8909e`.
It does not target production `main` and does not authorize a build,
a release, website deployment, public download, or premium redistribution.

## Reproduced source defect

Prior to R264, the shared `fvs_suite.launcher.launch` caught private-data
exceptions during security initialization (R263) and smoke testing (R262),
but the normal GUI path imported `fvs_suite.app` and called `run(app_id)`
without a privacy boundary. An import-time error or synchronous GUI entry
exception with private ledger paths would be printed by Python with a full
traceback, including chained cause/context. Each of the six app IDs uses this
same shared launcher.

## Code change

- Capture ordinary `Exception` from synchronous GUI module import and
  `run(app_id)`; exit nonzero with a fixed message, with no raw exception
  string, traceback, original financial path, or retained exception chain.
- Raise `SystemExit` **outside** the exception handler so `__cause__` and
  `__context__` are empty. A normal GUI event loop returning `None`
  remains successful. Do not swallow `KeyboardInterrupt` or `SystemExit`.
- Existing security bootstrap priority, Python-audit offline guard, smoke
  exit behavior, version output, and unsupported argument rejection remain
  unchanged. No engine, Decimal, entitlement, review, or site change.
- **Scope limitation:** this guards synchronous import/entrypoint exceptions
  only. Tkinter's internal callback error handlers, background threads,
  native modules and a genuine packaged Windows executable need separate
  inspection. This is not an OS sandbox or proof of zero data disclosure.

## Reproducible isolated verification

Local Linux CPython 3.13.5 with synthetic private paths; no real customer files,
no native Windows runtime. Created R264's regression suite *before* patching
the R263 launcher: **12 failures across 16 test methods** (real private paths
in stderr for GUI/import cases). After patch:

```sh
cd products/desktop
python -W error -m unittest discover -s tests -p 'test_launcher_gui_privacy_r264.py' -v
python -OO -W error -m unittest discover -s tests -p 'test_launcher_gui_privacy_r264.py' -q
python -m compileall -q fvs_suite tests
```

Results: **16/16 PASS normal + 16/16 PASS -OO = 32/32 method executions**, 
plus compileall PASS. Tests cover all six app IDs, private OSError, UnicodeError,
caused/context exceptions, import-time errors, no retained exception context,
successful dispatch, normal None-return, interrupts, offline socket/process
fence, bootstrap priority, smoke, version and unsupported arguments.

Executed source identities checked with `git hash-object` against committed
GitHub blobs:

- `fvs_suite/launcher.py`: `5c2f9f0e8275d2cb0c4ba933f55995d8b3dc6751`
- `fvs_suite/offline_network.py`: `30039ab587cb5a0ce3be305d78d3f919385a2fbf`
- `fvs_suite/__init__.py`: `a3e3f9fdeaf0f74f10077a7299f29f505dbe991f`
- `tests/test_launcher_gui_privacy_r264.py`: `5c61ab4dfb5ddcdcadcb33d978bab912f5e6ef39`

These are **focused, isolated local source regressions**, not the complete
repository suite or executable acceptance. The source tests deliberately
inject GUI module stubs rather than opening real graphical windows.

## Held gates / next highest-impact action

Hosted GitHub Actions R263 run
[`42404634222`](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42404634222)
reported source-tests and windows-build failures with no executed step or
retrievable runner logs; the cause is **not confirmed**. Owner should check
Actions billing/usage limits and hosted-runner provisioning, restore execution,
and rerun CI on an unchanged commit. Once operational, run all repository tests
and six **real Windows 11 x64** privately built binaries, test launcher
fault handling, scan/checksum/sign as applicable, complete accessibility
QA and verify protected premium distribution.

No executable was released, and no site or production file was modified.
