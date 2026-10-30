# R56 — Python / packaging-toolchain change detection (pre-release)

**Scope:** source/build environment safety for all six Windows x64 candidates, not a release or QD approval.

## Concrete gap addressed

R55 pins the six launchers, desktop Python runtime code and two build-control files. It did **not** pin the Python executable, installed PyInstaller files, hooks or critical libraries used to construct the six binaries. A packaging toolchain changed after source tests or between the first and sixth build could produce a mixed candidate while R55 source inputs remained unchanged. Also `python -m PyInstaller` searches the checkout working directory for imports, permitting an untracked repository-root `PyInstaller.py` to shadow the installed package.

R56 adds `scripts/toolchain_guard.py` and changes **both** the Windows offline driver and Windows CI to use `python -I -m PyInstaller` for every build. `-I` prevents the working directory and `PYTHONPATH` from being searched for the PyInstaller package; `--paths products/desktop` still includes app code during PyInstaller analysis.

## Inputs pinned and checks

The guard computes bounded SHA-256 content and local file identity for the actual Python interpreter plus files enumerated by Python distribution metadata. **Required:** `pyinstaller`, `pyinstaller-hooks-contrib`, `altgraph`, `cryptography`. **Also tracked when present:** `cffi`, `packaging`, `pefile`, `pywin32-ctypes`. Missing required packages, missing inventories, untrusted packages inside the checkout, symlinks, hardlink aliases, file swaps, in-place edits, added/removed installed files listed in the package metadata, changed versions, or excessive file sizes fail closed. The manifest includes per-distribution file counts, bytes and a digest of file names/content/identity, **not** absolute paths or customer data. Installer-generated scripts with `..` path components are deliberately excluded because `python -I -m PyInstaller` does not invoke them.

Capture produces a new, private, non-overwriting JSON manifest **outside** the checkout. It takes three snapshots, including one following atomic publication. `check` reads that manifest with descriptor-verified bounded I/O and strict JSON duplicate-key detection, then recalculates the complete toolchain snapshot. The machine-local manifest is **not signed** and should not be transported to another machine as a supply-chain attestation.

The Windows build driver and CI verify R55 source custody **and** R56 toolchain custody before/after each of the six PyInstaller invocations, after SHA256SUMS inventory creation, and around the executable verification gate.

## Trusted Windows x64 procedure

On a reviewed clean checkout, using a fresh trusted Python environment with PyInstaller and dependencies installed, run:

```powershell
$env:PYTHONPATH = "products/desktop"
python -m unittest discover -s products/desktop/tests -p test_toolchain_guard_r56.py -v
python -OO -m unittest discover -s products/desktop/tests -p test_toolchain_guard_r56.py -v
.\products\desktop\scripts\verify-windows-candidate.ps1 -Build
```

Or capture/check separately, with the new private target outside the checkout:

```powershell
python products/desktop/scripts/toolchain_guard.py capture C:\fvs-private-evidence\toolchain-NEW.json
python products/desktop/scripts/toolchain_guard.py check C:\fvs-private-evidence\toolchain-NEW.json
```

A failed check blocks packaging/candidate acceptance. Do not delete or overwrite prior evidence, silently reinstall dependencies mid-build, bypass checks, or publish partially built EXEs. Investigate and rebuild from a new clean environment. Environments using hardlinked installed dependencies may be rejected intentionally; use a clean, independent installation rather than relaxing the check.

## Evidence and limitations

R56 synthetic tests cover tampering, installation drift, interpreter changes, links, malformed/unsafe manifests, missing dependencies, and isolated `-I` module resolution. Local Linux Python 3.13.5: **23/23 PASS** normally and **23/23 PASS** under `-OO`; compilation successful. Tests ran using synthetic fake installed distributions and the unchanged R38 atomic report writer. This was **not** a full-repository regression, an actual PyInstaller build, or a Windows executable smoke.

This is **change detection, not dependency origin verification**: it cannot detect an already-compromised baseline, all dynamically located files, unrelated tools, unsigned PyPI packages, OS DLL substitutions, or privileged hostile actions between checks. The PyInstaller version is still permitted to vary **between clean runs** under the existing CI semver range. Independently lock and attest wheels, check Windows GUI keyboard usability, scan actual binaries, verify SHA-256 and premium access, then request QD approval before release.

**No executables are uploaded or published. All six remain unreleased, including both gated premium applications.**
