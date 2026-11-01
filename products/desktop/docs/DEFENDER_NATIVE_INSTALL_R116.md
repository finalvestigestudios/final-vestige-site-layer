# R116 — Native Defender installation-origin gate (private release verification)

**State: DRAFT / RELEASE HOLD.** No Windows executable, premium product, signing key, customer record, or private scan report is eligible for public upload. The six-app candidate suite remains unreleased; this does not modify the financial engines or entitlement locks.

## Threat and correction

The R111 offline six-executable operator scanner used process environment variables `ProgramData` and `ProgramFiles` to locate `MpCmdRun.exe`. An untrusted local process can override these variables to point the scanner preflight at a different directory. R114 removed search-path ambiguity for **PowerShell**, but the Defender scanner search roots still came from ambient environment data. Authenticode and SHA-256 custody offered other layers of protection; they did **not** make environment-selected directories authoritative.

R116 instead resolves the actual machine folders via Win32 `SHGetKnownFolderPath` with Microsoft's documented `FOLDERID_ProgramData` and `FOLDERID_ProgramFiles` GUIDs. It refuses a missing API, 32-bit/non-Windows process, suspicious or nonexistent native roots, linked/junction scanner ancestry, unexpected executable names, and executables outside the two recognized Defender layouts. The numeric latest-platform discovery and R112 scanner byte/signature custody remain in effect. A missing or corrupt native scan tool produces **HOLD**, never a permissive fallback to a user-supplied path.

## Contract and validation

- New pure Python/native-Win32 module: `scripts/trusted_defender_install_r116.py`; no added packages, network, privilege escalation or GUI changes.
- R111 `locate_defender()` now calls `install.native_roots()` and `install.require_candidate()`. It does **not** read `os.environ['ProgramFiles']` or `os.environ['ProgramData']`.
- R116 tests cover modern and legacy accepted layouts, wrong/non-version folders, absent directories, links and reparse ancestry, native-folder lookup failure, spoofed environment variables, 64-bit Windows requirements, and GUID byte layout. One Windows-specific test exercises real `SHGetKnownFolderPath` under the hosted Windows build job; this checks the API only, not real Defender scan execution.
- R111 prior scanner tests now inject a **test-only** native-root resolver. No customer files or real AV scanner are invoked.
- CI runs focused R116 tests under both Python normal and `-OO` on Linux and Windows, in addition to existing full source suites, six private Windows executable builds, SHA/PE/smokes, four free GUI and two premium locked-GUI tests.

**Limits:** Native known folders are not proof of OS trust, Microsoft signature correctness, actual antivirus detections, absence of tampering, independent malware clearance, or actual Windows 11 acceptance. Signed scanner verification, 14 active-health checks, 14 scanner-byte custody checks, 7 history/exclusion checks, and six-EXE R9 checks stay mandatory.

## Physical acceptance and privacy hold

The operator needs a trusted **Windows 11 x64 workstation**, six privately transferred checksum-pinned candidates, private R9 evidence with independently retained hash, an independently reviewed actual Defender/EDR scan and event/remediation assessment, and the 46 physically performed keyboard/NVDA/high-contrast/scaling tasks. QD must review the exact proposed SHA; founder must separately authorize release. Premium authenticated delivery and code-signing/security review remain separate unsatisfied gates.

No runnable candidates, premium editor bytes, client or financial inputs, scan history, or reviewer witness records may be committed to Git or attached to CI artifacts. No release/download links should be inferred from source or passing mocked CI tests.

Microsoft reference: `SHGetKnownFolderPath` in Windows Shell API and Known Folder IDs (`FOLDERID_ProgramData`, `FOLDERID_ProgramFiles`).
