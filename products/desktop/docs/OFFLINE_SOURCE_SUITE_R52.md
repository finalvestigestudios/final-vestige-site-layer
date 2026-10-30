# R52: runner-independent complete desktop source-suite gate

**Release state: development only.** This tool is for engineers operating a trusted source checkout. It neither produces nor approves Windows executables; it cannot authorize premium distribution, code signing, malware clearance, or QD/WordPress publication.

## Why

The R51 GitHub Actions run (`41000421385`) reported both Ubuntu and Windows jobs failed with no recorded execution steps; job logs were unavailable. Rather than treating hosted CI failure as an application regression or a pass, R52 supplies a no-cloud, operator-run path for **complete** local source regression evidence. The existing R9 Windows script now invokes this gate before attempting packaging.

R42/R43's six-source-smoke inventory covers application engines, helpers, and launchers, but not the Python regression *tests themselves*. R52 fingerprints every Python test file and helper, including nested modules, and checks content and private metadata snapshots before tests, after **each** test pass, and after all six synthetic engine smokes.

## Offline usage

From a trusted, complete checkout with Python 3.12+, Tk and `cryptography==46.0.4` installed:

```powershell
python products/desktop/scripts/offline_source_gate.py
```

This invokes **all desktop unittest-discovery tests** twice (normal and `-OO`), then runs all six synthetic engine smokes. Both test passes must exit zero. Test stdout and stderr are sent to the null device; customer filenames or exception text are not collected in the evidence. On failure, run `python -m unittest discover -s products/desktop/tests -v` directly in the trusted checkout (with `PYTHONPATH=products/desktop`), then address the failing tests. The script reports only a fixed redacted rejection message.

For an **exclusive, non-overwriting JSON** evidence report, first create a separate local folder *outside the repository checkout*, then run:

```powershell
python products/desktop/scripts/offline_source_gate.py --report C:\fvs-private-evidence\r52-source-suite.json
```

The report contains file-relative SHA-256 inventories and six synthetic smoke results; it has explicit `released: false`, `qd_approved: false`, `windows_executables_verified: false`, `premium_download_authorized: false`. Private inode/mtime metadata is used for comparisons but omitted from the report. The optional `GITHUB_SHA` field is an environment hint, **not a cryptographic checkout identity**. Archive the precise commit and independent checksum with the report.

## Test evidence and threat model

Focused regression tests: `python -m unittest discover -s products/desktop/tests -p test_offline_source_gate_r52.py -v`; repeat with `python -OO` to check optimized behavior. These tests verify fail-closed behavior for nonzero/timeout test runs, changed/added/deleted/swapped test modules, source changes during regression and smoke phases, extra launchers, and symlinks.

The gate intentionally does **not** hash generated `__pycache__`, site content, or every non-Python fixture. It cannot prevent privileged filesystem attacks, certify trust in the checkout or runner, or replace the independent native Windows x64 packaged-EXE verification. The test executor is deterministic in command/inputs, but successful evidence does not imply time-independent application behavior or signed provenance.

## Remaining release gates

On a trusted Windows 11 x64 machine, run `products/desktop/scripts/verify-windows-candidate.ps1 -Build` to build and smoke each of the six actual portable Windows binaries. Validate clean-machine GUI accessibility, premium entitlements, malware/SmartScreen, checksums and download access controls. Obtain independent QD approval before any merges/releases or WordPress changes. Keep financial data offline and all grant/procurement findings subject to human review.
