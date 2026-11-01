# R114 — Native System32 PowerShell custody for private Defender reviews

**DRAFT / RELEASE HOLD.** Six Windows x64 apps remain unreleased. This change prevents command-name/PATH hijacking in the *private reviewer tools*; it does not scan a real executable or authorize distribution.

## Specific weakness and correction

R111's Defender signature/health check and R113's local detection-history/exclusion observer previously invoked the bare process name `powershell.exe`. On Windows, process search behavior can be influenced by the working directory and search paths. A forged local `powershell.exe` could therefore run in place of the intended Windows PowerShell interpreter, returning false health/history observations.

R114 uses **Win32 `GetSystemDirectoryW` via ctypes**, not `PATH`, `SystemRoot` or `windir`, to obtain the native system directory on an actual 64-bit Windows process. It requires an absolute path ending in `System32`, appends the fixed `WindowsPowerShell/v1.0/powershell.exe` suffix, rejects symlinks and junctions on the System32-to-binary path, checks for a regular file with PE's `MZ` header, and fails closed if any requirement is missing. Both existing Defender PowerShell commands use this full absolute path with `shell=False`; no caller inputs are interpreted as shell commands.

**Trust limit:** Path provenance and `MZ` are not proof of a valid Microsoft publisher signature or of workstation integrity. Windows ACLs, native system APIs, and the protected OS installation remain outside the synthetic test's proof. An actual physical Windows 11 reviewer and an independent AV/EDR security evaluation remain necessary. This check does not harden against an OS-level attacker who can replace protected system files or impersonate Defender cmdlets. No protection setting, threat record, or PowerShell profile is modified.

## Code and regression scope

- `scripts/trusted_powershell_r114.py`: stdlib-only native resolver and strict fail-closed path guard. No network, subprocess execution, telemetry, or customer-data access in this module.
- `scripts/defender_candidate_scan_r111.py`: native interpreter resolution before any R111 signed-scanner health command; a resolution failure invokes no command.
- `scripts/defender_environment_r113.py`: native interpreter resolution before any R113 history/exclusion command; a resolution failure invokes no command.
- `tests/test_trusted_powershell_r114.py`: **15** synthetic standalone cases including PATH/`SystemRoot` tampering, missing/malformed/nonregular PE, symlink parent and binary, relative/wrong directory, native OS and architecture, and error redaction.
- Updated prior R111/R113 suites: two further failure-before-launch regressions and assertions that launched commands use the absolute interpreter. Test mocks supply a fixed synthetic path; only the new standalone contract exercises path checks, and no test claims a real security scan.
- `.github/workflows/desktop-build.yml`: mandatory normal and optimized `-OO` R114 regressions on Linux and Windows before existing full source suites and Windows packaging.

## Developer verification

```sh
python -m unittest discover -s products/desktop/tests -p 'test_trusted_powershell_r114.py'
python -OO -m unittest discover -s products/desktop/tests -p 'test_trusted_powershell_r114.py'
python -m unittest discover -s products/desktop/tests -p 'test_defender_candidate_scan_r111.py'
python -m unittest discover -s products/desktop/tests -p 'test_defender_environment_r113.py'
```

Hosted CI must additionally demonstrate the complete normal/`-OO` source gates, all six internal Windows EXE builds and R9 native smoke/integrity, four free native GUIs, two locked premium surfaces, R106/R107/R108 accessibility/cancellation preflights. A green hosted Windows Server run is **not** Windows 11 physical-review evidence.

**Distribution remains forbidden:** no executable uploads, no public download links, no entitlement unlock or payment activation, no site or production change. All **46 physical Win11/NVDA/contrast/scaling checks**, actual checksum-pinned Defender scan and independent event/remediation review, code-signing policy, authenticated premium distribution, QD exact-head review, and founder approval remain pending.
