# Labs R226 — numeric keypad access for all six input forms

**2026-11-05 PT / 2026-11-06 UTC · DRAFT ONLY · independent QD/founder HARD HOLD**

## Acceptance improvement

Before R226, the six-app keyboard installer only recognized the main-row digit
keysyms for source focus and Browse. A user relying on the numeric keypad could
not use the documented Alt+1..3 / Ctrl+1..3 input shortcuts. In Tk, physical
keypad presses can arrive as `KP_1`, `KP_2`, `KP_3` with Num Lock on,
or `KP_End`, `KP_Down`, `KP_Next` with Num Lock off.

R226 binds **both keypad keysym variants**, for each existing source index:

- **Alt + keypad 1/2/3:** focus the corresponding source-entry field.
- **Ctrl + keypad 1/2/3:** invoke that source's existing Browse button.
- Only existing input indices are bound (one to three per product).
- The regular keyboard shortcuts, output and Generate controls, LedgerDiff
  header mappings, invoice review window, and gated premium exception-review
  control are unchanged.
- No shortcut accesses source values, bypasses an entitlement, mutates an
  original CSV, or makes a compliance determination.

The visible GUI keyboard instructions now mention numeric keypad 1..3.
The input count remains constrained to the app's existing source inventory.

## Source and test artifacts

- `products/desktop/fvs_suite/keyboard_access.py`: native plus keypad bindings.
- `products/desktop/fvs_suite/app.py`: discoverability in all six forms.
- `products/desktop/tests/test_numeric_keypad_shortcuts_r226.py`:
  11 focused, synthetic-widget regression methods, including both modifier
  modes, Num Lock representations, all one/two/three-source layouts, no
  extra bindings, no default Generate/Review effects, no input value reads,
  deterministic binding order, and legacy optional-control behavior.
- `products/desktop/scripts/native_keypad_shortcuts_r226.py`:
  actual Tk 8.6 / Xvfb keysym dispatch on synthetic `ttk.Entry` and
  `ttk.Button` widgets, checking three focus transitions, three synthetic
  Browse callbacks, and zero Generate or output actions per run.
- `.github/workflows/desktop-build.yml`: source regression in both Ubuntu
  and Windows jobs, both normal and `python -OO`; real Tk smoke in Linux/Xvfb.
  The existing Windows full-source, build, private artifact, and QD gates
  stay in their established order.

## Actually executed local evidence — scoped

Linux x86_64 CPython **3.13.5**, Tk **8.6**, Xvfb.
Executed files are exact Git blobs when recorded against the branch head.

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover \
  -s products/desktop/tests -p 'test_numeric_keypad_shortcuts_r226.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover \
  -s products/desktop/tests -p 'test_numeric_keypad_shortcuts_r226.py'
PYTHONPATH=products/desktop xvfb-run -a python -W error \
  products/desktop/scripts/native_keypad_shortcuts_r226.py
PYTHONPATH=products/desktop xvfb-run -a python -OO -W error \
  products/desktop/scripts/native_keypad_shortcuts_r226.py
```

Results: **11/11 PASS normal**, **11/11 PASS optimized**;
**22/22 focused unittest method executions**. Two separate real-Tk runs
both PASS: **six native focus events, six synthetic picker invocations,
zero Generate/output actions**. Zero financial data fixtures; all tests
use fake widgets or synthetic controls.

These results validate the keyboard installer and test runner, **not** the
actual six forms in their installed Windows packaging, their screen-reader
announcements, Windows keymaps or end-to-end financial engines.
Physical keyboard Num Lock on/off must be witnessed on Windows 11.

## Required independent Windows / QD acceptance

1. Restore hosted GitHub Actions runners; rerun this **unchanged commit**.
2. Execute the entire inherited normal/optimized source suite and all six
   source smoke tests, rather than only R226.
3. On actual Windows 11 x64, use both Num Lock states with a **physical**
   numeric keypad for each configured source of all six apps; test Alt focus,
   Ctrl Browse, Tab order, Esc cancellation, and 100%/200%/400% scaling.
4. For both Pro apps, reject missing/invalid entitlement **before** file
   selection. Reverify entitlement immediately before Generate or human
   Review. Confirm key combinations cannot authorize approvals.
5. Privately build, hash, malware-scan, and smoke-test all six exact EXEs.
   A successful CI run does not authorize release. Do not expose premium
   binaries via public links. Only independent QD review and founder
   authorization may advance publication.

## Blocker and next highest-impact step

Hosted Ubuntu and Windows jobs in preceding R225 Actions run
`42166397227` reported completed/failure with null step data. Cause
unconfirmed; no Windows executable or hosted test may be counted.
Smallest owner action: inspect GitHub Actions account/repository billing,
usage, runner provisioning, and workflow prestart notices; restore runner
allocation and rerun R226 on the immutable head.

**No public downloads, production WordPress changes, entitlement bypass,
customer information, or QD/founder approval introduced in R226.**
