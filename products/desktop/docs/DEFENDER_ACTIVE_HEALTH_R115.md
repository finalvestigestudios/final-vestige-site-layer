# R115 — Active Microsoft Defender continuity gate (private Win11 x64 only)

**State:** engineering preflight only; **release HOLD**. Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Draft stacked on R114, not production `main`. None of the six Windows executables is approved for distribution.

## Observed weakness and correction

The R111 preflight checked that Microsoft Defender reported service, antivirus, real-time protection and fresh signatures **only before and after** six independent scanner invocations. The service could become passive or lose behavior/on-access/IOAV protection between those two observations without triggering the previous status gate.

R115 requires Microsoft Defender's `Get-MpComputerStatus -ErrorAction Stop` to report `AMRunningMode = Normal` (not passive, EDR block, or unknown), plus explicit `AMServiceEnabled`, `AntivirusEnabled`, `RealTimeProtectionEnabled`, `BehaviorMonitorEnabled`, `IoavProtectionEnabled`, and `OnAccessProtectionEnabled` true. Existing valid Microsoft Corporation scanner Authenticode signature and antivirus signature freshness (age ≤3 days) remain mandatory.

The R111 operator workflow now evaluates **14 active-health checkpoints**: initial, immediately before each of six candidates, after each of six candidates (following R113 history observation), and final. Any failed, unavailable, ambiguous or timed-out checkpoint aborts without a completion report. Existing seven history/exclusion observations and 14 scanner-byte identity checkpoints are preserved. Report counts describe checks **attempted and completed on a successful run only**; they do not assert continuous protection between observation instants.

## Tests and executable impact

`tests/test_defender_active_health_r115.py` exercises twelve fail-closed synthetic contracts: static required provider fields, signed-scanner/signature freshness, exact six-app ordered checkpoint chronology, early and late health failure stops, history-before-posthealth failure, timeout error redaction and non-release report flags. Existing R111 integration test now requires fourteen health calls. Mandatory normal and optimized `-OO` jobs on Linux and Windows are source-level tests **with mocked provider/Win11 behavior**, not real Microsoft Defender results.

The code does not import financial records, contact a server, modify Defender settings, use customer data, change premium licensing, or upload any binaries. R111/R115 are to be run **privately** against exact R9 SHA-pinned six EXEs on a trusted, independently reviewed physical Win11 workstation. Neither a zero scanner exit nor fourteen clean snapshots proves malware absence; detections/remediation require separate human review. Preserve all reviewer evidence locally.

## Human / commercial release blockers

All 46 physical Win11 keyboard, NVDA, high-contrast and scaling acceptance checks are still NOT_RUN. Independent AV/EDR clearance, code-signing/SmartScreen, authenticated premium issuance/distribution, QD exact-head review and founder authorization are still required. **No public EXE artifacts, unsigned download links or premium access exceptions.**

Official provider fields: [Microsoft PowerShell Get-MpComputerStatus](https://learn.microsoft.com/powershell/module/defender/get-mpcomputerstatus). Microsoft explains normal versus passive running modes in [Microsoft Defender Antivirus on Windows](https://learn.microsoft.com/defender-endpoint/microsoft-defender-antivirus-windows).
