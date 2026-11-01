# R107 — Scaled Tk viewport, keyboard visibility and local-first reflow

**November 1, 2026 · DRAFT / RELEASE HOLD · Issue #73.** This PR is stacked on R106 PR #432, exact parent `f8e5198f7f6ec43cc4d642c99062fc9071a69e52`. Neither production `main`, WordPress nor hosted downloads are changed.

## Defect addressed

R105 confirmed the **actual Windows EXEs open** and premium lock, and R106 confirmed the four free source Tk UIs expose deterministic Tab traversal and shortcuts. Neither proved that a focused control remains visible when a user increases system text/DPI scaling. All six application forms previously used a fixed-size, non-scrollable `ttk.Frame` with long labels and fixed 690/700-pixel wrapping; controls below a small/scaled viewport could be inaccessible visually even when Tk Tab focus reached them.

## Implemented

- `fvs_suite/scroll_access.py`: lightweight root-local scroll container with vertical `Canvas` + `ttk.Scrollbar`. Both are `takefocus=0` so the existing native Entry/Browse/Generate Tab sequence and shortcuts remain unchanged. It dynamically wraps text labels to viewport width, uses the current system window background (no hard-coded Canvas theme), and reveals focused Entry/Button controls by scrolling only when outside view. Geometry calculation has a pure deterministic function and rejects invalid numeric values even under `python -OO`. It never reads textbox contents or visits customer files.
- `fvs_suite/app.py`: all six app forms use this container, including premium **only after the existing signed-entitlement gate**. The source's one idle-focus callback, all financial actions, offline verification, exception workflow, and human-review disclaimers stay intact. A premium-only hard-coded warning foreground was replaced by bold system-color text to avoid defeating Windows high contrast; entitlement selection and review authorization are not changed.
- `tests/test_scroll_access_r107.py`: synthetic local test suite covers deterministic fractions, clipping above/below, invalid geometry, bounded scroll targets, four-product inventory, two scale modes, every gate signal, and denial of premium/unknown products. Runs on Linux and Windows without a GUI in **both** normal and optimized Python.
- `scripts/native_scale_probe_r107.py`: native Windows x64 smoke of the actual source Tk UI at simulated **200% and 400% Tk text scaling**, at the supported 600x390 window minimum. Checks one scroll viewport and associated scrollbar, required widgets, scroll travel when necessary, native focus revealing obscured fields, dynamically sized hint text, non-focusable scroll controls, and system background. For each of four free apps at two scales, file picker and financial processing actions are replaced by deny-only functions. Premium editors and customer data never opened. Fixed safe CI diagnostics only.
- `.github/workflows/desktop-build.yml`: adds a mandatory normal/`-OO` focused source gate on Linux and Windows plus native Windows Tk scaled-view probe AFTER the existing R9 binary-custody, R105 six-EXE GUI/premium lock, and R106 keyboard checks. Neither upload-artifact selector changes nor any executable uploads are added.

## Verification commands

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_scroll_access_r107.py' -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_scroll_access_r107.py' -v
PYTHONPATH=products/desktop python products/desktop/scripts/offline_source_gate.py
# Only native Windows x64 CI desktop:
PYTHONPATH=products/desktop python products/desktop/scripts/native_scale_probe_r107.py
```

**Proof rule:** proposed tests do not count as passing until executed and recorded at exact PR head. A native CI failure closes the gate; do not weaken the probe to obtain a green check. No release claim from isolated widgets or scaled Tk emulation.

## Remaining mandatory founder/QD gates

This is **not** Windows 11 physical 200/400% monitor scaling, actual packaged-EXE hardware keyboard use, Microsoft UIA/NVDA/JAWS, Windows high-contrast theme selection, non-English fonts, native file-picker testing, accessibility certification, malware/EDR and signing review, customer-safe reports, premium authenticated distribution, independent QD exact-SHA approval, or founder production/publication authorization. Repeat manual tests in a trusted Windows 11 x64 environment and record OS build, PE checksum, scale and exact GUI behavior; do not expose client data in evidence. All **six products remain unreleased**, and the two premium interfaces remain gated. No production edits, license-key issuance, marketing claims or public binaries.
