# R55 — six-app Windows packaging input custody (pre-release)

**Source-only guard; never a release authorization.** This sprint closes a practical gap between the R52–R54 source regression suite and R9/R40 Windows packaging: previously the Python source tree could change after the test pass or between individual PyInstaller builds, yielding a six-EXE candidate assembled from mixed inputs.

## What is pinned

`scripts/build_input_guard.py` captures the R43 bounded, descriptor-checked SHA-256 inventory and filesystem metadata for every desktop Python source, nested package module, test-independent runtime script and each of the **exact six launchers**. It additionally fingerprints both packaging-control files: `scripts/verify-windows-candidate.ps1` and `.github/workflows/desktop-build.yml`, rejecting symlinked ancestors.

The versioned manifest contains only repository-relative file paths, SHA-256 digests and local source-file metadata. It contains no input CSV data, financial records, customer paths, credentials or raw test output. The manifest says `released=false`, `qd_approved=false`, `windows_executables_verified=false`, and `premium_download_authorized=false`.

Capture compares two snapshots, creates a **new** private manifest outside the checkout using exclusive atomic publication, and verifies the source once more after publication. Subsequent checks reject observed file content changes, additions/deletions, metadata-only rewrites, inode swaps, unsafe links, altered build controls and unsafe/oversized/duplicate-key manifest files. A check re-enumerates the full source scope, so neither a seventh launcher nor a new Python module is silently ignored.

## Operator procedure on trusted Windows 11 x64

Use a clean, fully fetched feature-branch checkout, Python 3.12+, locally reviewed dependencies and an already created private evidence folder outside the checkout. The normal candidate driver performs the source gate, captures input custody and checks it **before and after each of six PyInstaller invocations**, after checksum inventory generation, and before/after the executable smoke/attestation gate:

```powershell
$env:PYTHONPATH = "products/desktop"
.\products\desktop\scripts\verify-windows-candidate.ps1 -Build
```

For a manual source-only check, provide a **new** manifest path that does not exist:

```powershell
python products/desktop/scripts/build_input_guard.py capture C:\fvs-private-evidence\r55-new-inputs.json
python products/desktop/scripts/build_input_guard.py check C:\fvs-private-evidence\r55-new-inputs.json
```

Both commands fail closed with a fixed privacy-safe error and a nonzero exit. Do **not** delete source files, remove a potentially suspicious custody file, or override a failed check to continue a release. Inspect source diffs, rerun both full test modes, create a new candidate and preserve previous evidence for QD review.

The internal Windows CI job also captures once before packaging, checks on both sides of each binary build and rechecks around the release candidate smoke/attestation gate. It uploads checksum and report **evidence only**, not free or premium executables. GitHub Actions runner failures before step execution are **not test results**.

## Local regression scope and evidence limits

```powershell
$env:PYTHONPATH = "products/desktop"
python -m unittest discover -s products/desktop/tests -p test_build_input_guard_r55.py -v
python -OO -m unittest discover -s products/desktop/tests -p test_build_input_guard_r55.py -v
```

The new tests use synthetic file trees only and cover stable success, altered controls, added/missing source, same-byte swaps, metadata-only changes, unsafe filesystem links, manifest replay/collision, tampering, privacy-safe errors and mid-capture mutation.

This is a **process-local detection guard**, not a signed/attested build, a complete reproducible-build protocol, a check of the PyInstaller/toolchain wheel provenance, a guarantee against privileged filesystem manipulation or a lock that prevents source changes between checks. Non-Python project fixtures outside the explicit build controls are not inventoried here. Source verification does not establish that native Windows GUIs work, that a packaged binary is malware-free or code-signed, that premium downloads are restricted, or that QD has approved release. These gates remain independently required by issue #73.

**All six executables remain unreleased; no public or unrestricted premium download is authorized.**
