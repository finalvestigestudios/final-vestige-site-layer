# Data Import Doctor — Windows release acceptance checklist

**Not a completed test record.** This is the executable evidence required before a public release.
Checks must be run on a clean Windows 11 x64 system with the exact installer artifact;
record Windows build SHA, installer SHA-256, test date, and tester in the release evidence.

## Build provenance

- [ ] Python 3.12 unittest suite (original and v0.2 cases) passes on a Windows runner.
- [ ] PyInstaller build produces `DataImportDoctor.exe` and the Inno Setup installer.
- [ ] Generate and independently recompute SHA-256 checksum of the installer.
- [ ] Code-sign installer and application with a trusted, current signing identity.
- [ ] Defender/security scan passes; verify no packed executable false positives remain.
- [ ] Rebuild from exact tagged Git commit and record dependency/SBOM versions.

## Installation and operation

- [ ] Install as standard (nonadmin) user; verify Start Menu shortcut launches GUI.
- [ ] Test silent install, uninstaller, application removal, reinstall, and upgrade.
- [ ] Run a clean two-row CSV; confirm a clear structural PASS with zero errors.
- [ ] Load `examples/sample-import.csv` and `examples/sample-schema.json`.
- [ ] Confirm three records and four issues: duplicate_key=1, invalid_type=2,
      invalid_allowed_value=1. The duplicate must identify physical line 3.
- [ ] Verify a multiline quoted cell and confirm correct physical line references.
- [ ] Verify BOM CSV, semicolon separator, Unicode headers and Unicode filenames.
- [ ] Verify blank header, duplicate-case header, malformed quote and header-only
      CSV all fail closed rather than suggesting successful import.
- [ ] Verify rejection of a source file over 80 MiB and rule JSON over 1 MiB.
- [ ] Confirm GUI stays responsive during maximum-sized file analysis.
- [ ] Change the selected source after analysis but before export; export must
      refuse until reanalysis. Repeat for edited schema rules.
- [ ] Try choosing the CSV, JSON rules, existing report, and symlink as the
      export destination; all must be rejected without modifying originals.
- [ ] Verify source and rules bytes/checksums identical before/after analysis.
- [ ] Inspect JSON report: no source full path, proper status, schema/source SHA-256,
      issue counts, capped examples and clearly visible incomplete warnings.
- [ ] Run CLI source version on malformed CSV; verify exit 2. For issue CSV exit 1;
      clean CSV exit 0. Do not assume console output from `--windowed` EXE.
- [ ] With network access denied, verify full GUI and report workflow still works.

## Commercial release gate

- [ ] Run a realistic external beta on customer CSV samples using synthetic
      or redacted records; verify results with a human reviewer.
- [ ] Confirm purchase-free distribution, no accounts, no unexpected telemetry.
- [ ] Publish genuine screen captures, version, limitations and support contact.
- [ ] Verify final download URL, Content-Type, file size, SHA-256, Windows Defender
      reputation, and signed installer on the public finalvestige.com page.

**At present:** Local Python engine + CLI tests passed; GitHub hosted runners
have failed before job steps began, and clean Windows installation/signing
have not been verified. This checklist is intentionally unfilled.
