# R105 — Native Windows GUI surface and fail-closed premium lock observation

**2026-11-01 UTC · draft, release HOLD · issue #73.** Based on R104 PR #425 at exact commit `1c138aea0b21a2801084d651c9c9794424c40cca` only, not production `main`.

## Why this matters

The R104 Windows build passed both complete source-test modes, built six PyInstaller Windows x64 portable executables, and passed the R9 offline PE/SHA-256/`--smoke-test` verification at intermediate head `9e1536e` ([Actions #41288480604](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41288480604)). That was a substantial packaging milestone, but **`--smoke-test` does not create the Tk user interface**. A binary can pass a source-engine smoke while failing to open its real GUI. Furthermore, the two premium EXEs must remain unusable without signed production authority. The R105 native test targets those separately verifiable gaps.

## Implemented

- `scripts/windows_gui_probe_r105.py`: native **Windows x64 only**, runs only after the original R9 candidate gate. Reads exact six-EXE PE/checksum proof both before and after GUI probes. Launches all six built EXEs **without command-line smoke flags**, one at a time; enumerates visible Win32 windows and process ancestry through Win32 ctypes/Toolhelp.
- Four free products must display their **actual uniquely titled main Tk window**.
- GrantAudit Studio Pro and ProcureGuard Studio Pro, with intentionally empty `TRUSTED_PUBLIC_KEYS`, must instead display `Premium preview locked` and must **not** expose their normally entitled main editor. It does not try to mint, grant, or bypass entitlement.
- A matching pre-existing window, unrelated process, or renamed/impostor title never satisfies the test. Candidate checksum/PE integrity is checked again after all observations. Each launched process tree is forcibly cleaned up; no app ever selects documents, runs Generate, opens review, or writes customer reports.
- `tests/test_native_gui_probe_r105.py`: 14 synthetic fail-closed ownership/lock-admission test cases, run with both normal and optimized Python on Linux and Windows.
- `.github/workflows/desktop-build.yml`: focused R105 tests precede the mandatory R57 source suite. Native R105 GUI observation follows the successful R9 gate **and existing evidence-only upload**, so an unavailable GUI desktop does not erase verified R9 proof; nevertheless any R105 failure marks the workflow **RED**. This test is not softened with `continue-on-error`. No executable upload is added and the R41 evidence-only artifact allowlist is unchanged.

## Scope and limitations

The runner may not provide an interactive desktop visible to Win32 window enumeration. If so R105 must **fail closed**, not report a GUI pass. The `--report` output is private, path-free and release-denying; it is not in the existing GitHub uploaded artifacts because the upload policy intentionally allows only SHA256SUMS and R9 evidence. The CI result/log gives the authoritative observation outcome.

The probe establishes observable top-level GUI availability and expected local premium lock behavior; it **does not** establish WCAG 2.2 AA, manual NVDA/screen-reader navigation, keyboard shortcuts, file-picker usability, signed premium licensing, AV/EDR clearance, code signing, long-running stability, customer adoption, or authorized download distribution. Do not mistake an empty public-key pin in development for a production licensing design.

### Private reproduction in a trusted Windows x64 checkout

```powershell
$env:PYTHONPATH = "products/desktop"
python -m unittest discover -s products/desktop/tests -p test_native_gui_probe_r105.py
python -OO -m unittest discover -s products/desktop/tests -p test_native_gui_probe_r105.py
python products/desktop/scripts/offline_source_gate.py
# AFTER trusted internal six-EXE package, inventory and R9 evidence are verified:
python products/desktop/scripts/windows_gui_probe_r105.py dist --report build/offline-gui-surface-evidence.json
```

Do not run GUI probes on the production site or publish the six EXEs. If a CI runner has no usable desktop, the **smallest unblock** is a dedicated interactive Windows 11 x64 QA VM on which the exact attested six candidates can be run in an authorized private environment, followed by the same script and independent GUI/keyboard/AT review.

## Remaining release conditions

Both Linux/Windows exact-head complete normal and optimized tests; six Windows PE/SHA/smoke and native GUI observations; actual Win11 11 x64 manual keyboard/NVDA/high-contrast/zoom checks; signed AV scans and software publisher certificate if available; offline premium entitlements and *gated* distribution; independent QD exact-commit assessment; founder approval. **All six products remain unreleased**, regardless of CI outcome.
