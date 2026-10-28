# R17 — Windows x64 PE-image structural preflight (internal, not a release)

## Failure mode addressed

R9 only read the first 26 bytes of the NT header. A checksum-matched file
containing MZ, PE signature, AMD64 and PE32+ magic could pass even if it had no
section table, no entry point, or was flagged as a DLL. A SHA-256 checksum
proves consistency with the manifest, not that an input is an executable.

R17 adds products/desktop/pe_image_guard.py to the **existing** six-app
release_gate.verify path, before any candidate may be smoke-tested. The
verifier opens a candidate read-only (no-follow when supported), confirms a
regular file, uses bounded offset reads and checks:

- MZ/PE signatures and a bounded NT header offset.
- AMD64 COFF machine, 1–96 sections, a bounded PE32+ optional header.
- Executable-image characteristics with neither DLL nor system-image flags.
- A nonzero entry point, power-of-two alignments, sensible image/header
  extents and GUI/console (not native/driver) subsystem.
- A complete COFF section table, backed section bytes within the file, and at
  least one backed section marked executable.

All six expected filenames, SHA-256 inventory entries, before/after smoke
integrity checks, smoke timeouts and no-release-authority report flags are
**unchanged**. Earlier R9/R10 inert test fixtures were upgraded to supply
realistic header structure, *not* real runnable binaries.

## Evidence and reproducibility

Focused R17 **13 tests passed** on Linux in both ordinary Python and -OO.
These use inert 1-KiB mock images and mutate architecture, signatures, section
headers, flags, entry point, subsystem, sizes, alignments and symlinks.

Run the exact committed tests (once a trusted checkout is available):

    PYTHONPATH=products/desktop:products/desktop/tests python -m unittest discover -s products/desktop/tests -p test_pe_structure_r17.py -v
    PYTHONPATH=products/desktop:products/desktop/tests python -OO -m unittest discover -s products/desktop/tests -p test_pe_structure_r17.py -v

The complete test suite, previous R9/R10 integration tests on this branch,
real Windows x64 PyInstaller executables, malware/Authenticode validation and
clean Windows 11 smoke are still **unverified** until a usable runner or
trusted Windows workstation is available. Python test passes are not release
evidence for actual EXEs.

For candidate verification on a trusted clean Windows 11 x64 checkout:

    powershell -ExecutionPolicy Bypass -File products/desktop/scripts/verify-windows-candidate.ps1 -Build

Inspect the six binary hashes, smoke output, and generated
dist/offline-gate-*.json report. Treat the report as pre-release evidence
only; product owners must separately approve QD production publication,
signing/malware acceptance, premium entitlements and restricted delivery.
**Never upload an untested premium EXE to public web storage.**

## Limitations

Structural PE validity is not code-signing, malware clearance, an end-to-end
installer test, a trusted timestamp, or a runtime behavior guarantee. SHA-256
inventories generated from untrusted artifacts do not provide authenticity.
Symlink restrictions on platforms lacking O_NOFOLLOW also depend on the
release gate's _regular pre-check. No customer financial data is required
for these structural tests, and no data leaves the local machine.
