# FileProof 0.2 — local integrity and authenticated manifests

**Development preview. Not yet a publicly tested or signed Windows release.**

FileProof helps people check whether files have changed or disappeared from a
folder. It records each readable regular file's relative path, byte length and
SHA-256 digest in a JSON manifest. During verification, it checks those files
again and reports changed, missing, unreadable, added and unstable files,
untracked symlinks/junctions, and directory scan errors.

## Which program should I run?

- **FileProof.exe** is the graphical Windows desktop program.
- **FileProofCLI.exe** is the console companion for scripts and administrators.
  They use the same offline engine. The console build is separate because a
  Windows GUI executable built with PyInstaller --windowed has no usable
  console output.
- Neither application requires a user account, Internet access or data uploads.
- Windows x64 is the intended installer target. Installer smoke tests and
  code-signing are prerequisites for publication.

## First use (graphical)

1. Choose the source folder, then **Create manifest**.
2. Save the JSON manifest, ideally *outside the source folder*.
3. Select **Yes** to protect it using a unique passphrase of 12+ characters.
   Re-enter the exact passphrase for confirmation.
4. Store the passphrase in a safe location separate from the manifest. There is
   **no passphrase recovery or reset**.
5. Later, select the same source folder, choose **Verify manifest**, and provide
   the passphrase if prompted. Review every non-OK result and scan error.

An authenticated manifest displays **AUTHENTICATED** only after its passphrase
MAC verifies. An unprotected legacy/plain manifest is explicitly labeled
**UNAUTHENTICATED**, even if every recorded file matches its checksum.

## Using FileProofCLI.exe

The option accepts a *file containing the passphrase*, not the passphrase
itself. This avoids putting secrets in process command lines or shell history.
Store that file securely, outside the folder being inspected. Example
(PowerShell):

    .\FileProofCLI.exe create C:\Records C:\Proof\records.json --passphrase-file C:\Private\fileproof-secret.txt
    .\FileProofCLI.exe verify C:\Records C:\Proof\records.json --passphrase-file C:\Private\fileproof-secret.txt

Without --passphrase-file, the tool creates or verifies an unsigned manifest:

    .\FileProofCLI.exe create C:\Records C:\Proof\legacy.json
    .\FileProofCLI.exe verify C:\Records C:\Proof\legacy.json

**Exit codes:** 0 = completed and clean; 1 = verification differences or scan
errors; 2 = invalid input, authentication failure, incomplete initial snapshot,
or an I/O error. The tool never rewrites source files. Creating a manifest
refuses to overwrite an existing destination, including if another process
creates it during publication.

Verification with --passphrase-file rejects an unauthenticated manifest,
including one whose authentication metadata was removed. A protected manifest
also requires a passphrase, even when all underlying files appear unchanged.

## What the protection does and does not do

- **Signed/verified files?** No. The optional protection uses
  PBKDF2-HMAC-SHA256 (600,000 iterations, per-manifest random salt) and a
  keyed SHA-256 MAC covering the manifest JSON properties. This establishes
  consistency with the supplied passphrase, **not** the author's identity.
- **Windows code signing?** No. A passphrase-authenticated manifest is not
  a publisher-signed Windows installer. Windows installer signing remains
  a separate release requirement.
- **Encryption?** No. JSON manifests reveal paths, sizes and hashes. Do not
  put sensitive file names into a publicly shared manifest.
- **A backup?** No. It detects changes but cannot restore damaged files.
- **Prevent all attacks?** No. An adversary able to replace an unsigned
  manifest can rewrite its hashes. An adversary with the passphrase can forge
  authenticated manifests. An adversary can delete/replay older *valid*
  manifests; secure copies and separate dated records remain necessary.
  For strong verification, explicitly supply the secret file: an unsigned
  manifest cannot prove that authenticated metadata was never stripped.
- **Short passwords?** Minimum 12 characters is enforced at creation, but
  use a strong, unique, preferably randomly generated passphrase; length
  alone does not prevent dictionary guessing.
- **Filesystems:** Manifest publication requires hard-link support in the
  destination folder to guarantee atomic no-overwrite. If unsupported (some
  network drives or removable filesystems), saving fails safely. Choose a
  destination on a local NTFS disk.
- **Scope:** v0.2 does not audit empty folders, registry state, permissions,
  alternate data streams, hard-link counts, or source-file ownership.
  Files altered and restored between checks can pass. Checks do not make
  hostile input safe to open.

## Development and manual release tests

Run all FileProof Python unit tests using Python 3.11+:

    python -m unittest discover -s desktop-software/fileproof -p "test_*.py" -v

On Windows, build **both** executables with PyInstaller, then compile
desktop-software/fileproof/installer.iss with Inno Setup 6. CI must install the
generated EXE to a temporary directory and run:

    python desktop-software/fileproof/smoke_installed.py "C:\path\to\FileProofCLI.exe"

The smoke suite creates a fictional test directory, authenticates a manifest,
verifies it, tests incorrect/missing passphrases, detects a modified file,
detects altered or stripped authentication data, and checks unsigned handling.
It then verifies the application's uninstaller removes both EXEs. GUI
first-launch, accessibility, upgrade, AV scanning, installer signing, and
uninstall on an actual supported Windows system remain manual release gates.

**Status: source implementation and development tests, not production-ready.**
