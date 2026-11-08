# Labs R284 — single-shot / atomic Tk keyboard registration (DRAFT / HOLD)

**Issue:** #73. **Scope:** all six Windows x64 utilities through the shared `fvs_suite.keyboard_access.install_shortcuts` helper. This feature branch is stacked on the immutable R283 head `92fdd4aa85038eecdd2097afbf84d2e5e6a6153c`, not on the production branch. No changes to financial engines, Decimal handling, compliance decisions, entitlement validation, network behavior or public distribution.

## Defect and remediation

The previous helper registered shortcuts with Tk's additive `bind(..., add="+")` on each call. Calling the helper twice for one window installed duplicate handlers, meaning one Ctrl+Enter could invoke the *existing* Generate button twice, and premium Alt+R could invoke the *existing gated* Review button twice. A failure during a sequence of bind calls also left earlier shortcuts installed, potentially causing duplicated callbacks on retry. This is a defensive correction for a reproducible reinstallation defect, **not evidence of a production financial double-posting incident**.

The helper now rejects a second install for the same root before changing bindings. During initial installation it remembers each Tk callback identifier. A failed registration rolls back just those new callback IDs in reverse order, preserving preexisting application handlers. If callback removal cannot be attested (including headless fake roots with no callback IDs), it blocks installation retries on that root. The first complete successful install uses the same existing callback actions and deterministic keyboard inventory. All business and human-review authorization remains inside the original buttons.

## Exact local verification (2026-11-08)

Linux CPython 3.13.5, Tk / Xvfb, synthetic fields and buttons for all six distinct product configurations:

```sh
PYTHONPATH=products/desktop xvfb-run -a python -W error -m unittest discover -s products/desktop/tests -p 'test_shortcut_registration_r284.py'
PYTHONPATH=products/desktop xvfb-run -a python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_shortcut_registration_r284.py'
python -m py_compile products/desktop/fvs_suite/keyboard_access.py products/desktop/tests/test_shortcut_registration_r284.py
```

- 12/12 real Tk integration methods passed in normal mode; 12/12 passed in optimized mode = **24/24 focused local test executions**.
- Six configurations proved a second installer call rejects before changing any binding. Actual Ctrl+1 and Ctrl+Enter events each invoked the existing command **exactly once**; no Review command fired accidentally.
- Six configurations injected a `tk.TclError` on the fifth registration. The first four callbacks were removed without deleting a preexisting Ctrl+1 handler, and a clean retry succeeded and dispatched Browse once.
- Negative control against the original R283 helper: **12/12 new cases failed**, demonstrating the regression detects the defect. The patched helper returns 12/12 passing per mode.
- Byte identity: tested shared helper Git blob `ecd2c6da7c997eaeb20ad67ca5262d1f07b12d79`, and new tests Git blob `b8e69f09e7000e9eccfee537415e2c6b2cfc00f1` match the proposed branch files.
- Two-mode Ubuntu/Xvfb source-tests step added to `.github/workflows/desktop-build.yml`.

**Not established:** complete inherited repository test pass, successful hosted CI, real Windows 11 x64 packaged executable behavior, Defender scan, accessible physical keyboard/screen-reader tests, secure Pro distribution, buyer validation, or a release.

## Release/QD controls and next action

DRAFT / UNMERGED; independent QD and explicit founder authorization are required before any merge/release. No public EXEs or premium asset URLs. Restore GitHub Actions runner availability and rerun the exact head. Then execute the entire regression suite and private six-executable Windows 11 x64 build, smoke/checksum/Defender, physical accessibility, and entitlement-controlled distribution acceptance. Use only synthetic test data and preserve the local-first, human-review design.
