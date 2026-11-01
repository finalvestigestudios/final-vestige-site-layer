# R113 — Defender history and exclusion observation for private Windows 11 acceptance

**Status: engineering source gate only. Release HOLD.** This component does not itself perform a real Windows 11 scan, certify malware clearance, review payment entitlement, or authorize any software download.

## What changed

R111 already cryptographically binds all six Windows AMD64 EXEs to the independent R9 smoke report, performs six synchronous Microsoft Defender custom-file commands, and labels a zero exit **remediation-ambiguous**. R112 adds signed scanner identity and repeated SHA-256 custody. R113 adds a **fail-closed, privacy-minimal observation of Defender history and configured exclusions**:

- Before the first candidate scan, and immediately after each of the six custom-file scans, invoke a fixed, non-interpolated, local Windows PowerShell command (seven total observations).
- Query Microsoft's `Get-MpThreatDetection` (individual active/past detection records), `Get-MpThreat` (threat history), and `Get-MpPreference` (explicit path, extension, process and IP exclusions). Require all three reported counts to equal zero at every checkpoint.
- Fail closed if an observer command is missing, errors, times out, returns nonzero, returns any nonzero count, outputs extra or malformed data, or encounters an unsupported environment. A partially scanned suite cannot produce a success report.
- All detected object details stay inside the local PowerShell process. Only a short fixed ASCII count line is parsed in memory. **No threat names, user names, local paths, customer CSV records, individual exclusion strings, or security-event dumps enter the JSON report or CI logs.**
- A completed private R111 report records `defender_environment_observations=7` and `defender_environment_status=zero_local_history_and_explicit_exclusions_observed_not_malware_clearance`, with `release_authorized=false`, `premium_distribution_authorized=false`, and `independent_malware_clearance=false` unchanged.

This supplements, **not replaces**, inspection of Windows Security Protection History, quarantine/remediation, Microsoft Defender Operational events, and other AV/EDR findings by an independent human reviewer. Empty local history is **not evidence of complete event retention, protection coverage, no threat remediation, or software safety**. Exclusion metadata may be incomplete relative to OS-managed automatic exclusions. A reviewer must not clear old threat records, remove quarantine, change Defender preferences, or disable protection to force these checks to pass. Use a separately provisioned trusted workstation or stop and escalate.

## Private operator procedure

1. Independently retain all six nonpublic, unmodified Windows x64 candidate EXEs, `dist/SHA256SUMS.txt`, the R9 Windows native-smoke report, and its SHA-256 outside the repository. Confirm a trusted physical Windows 11 x64 workstation, elevated reviewer permissions, current active genuine Microsoft Defender, and signed stable scanner engine as required in [R111](OFFLINE_DEFENDER_SCAN_R111.md) and [R112](DEFENDER_ENGINE_IDENTITY_R112.md).
2. On that workstation, use the **existing R111 private scanner CLI** with its exact externally pinned R9 report hash and a private output path; R113 runs as part of that CLI automatically. No uploads or network activity are performed by the R113 observer. The Defender installation itself may have cloud or sample-submission features unless separately controlled by the organization.
3. A nonzero local history or configured exclusion causes **HOLD** before or between scans. Do not make changes to the workstation to obtain an artificial PASS. Review detection/remediation and protection configuration independently. The R113 result is not a release signoff.
4. After any actual scan, retain observations locally and privately. The reviewer separately examines Windows Security history, Defender operational event logs and remediation records; documents any detections and evidence gaps without including private paths in GitHub; and performs the 46 bound Win11 physical keyboard/NVDA/high-contrast/scaling checks.
5. Separate remaining gates: independent malware/EDR clearance, signature/SmartScreen policy, premium account/license authorization plus restricted delivery verification, independent QD exact-commit approval, and founder authorization. Do not merge to production, publish binaries, or mark the six applications released.

## Reproduce *synthetic* policy tests

```sh
python -m unittest discover -s products/desktop/tests -p 'test_defender_environment_r113.py'
python -OO -m unittest discover -s products/desktop/tests -p 'test_defender_environment_r113.py'
python -m unittest discover -s products/desktop/tests -p 'test_defender_candidate_scan_r111.py'
python -OO -m unittest discover -s products/desktop/tests -p 'test_defender_candidate_scan_r111.py'
```

CI executes these on Linux and Windows in normal and optimized modes before packaging. Simulated output verifies fail-closed contracts and privacy, **not** a real threat-history observation. Windows GitHub Actions runners are not accepted as physical Win11 evidence, and no R113 result, scanner record or EXE is uploaded as an artifact.

## Primary cmdlet documentation

- Microsoft Defender PowerShell module: https://learn.microsoft.com/powershell/module/defender/
- Get-MpThreatDetection: https://learn.microsoft.com/powershell/module/defender/get-mpthreatdetection
- Get-MpThreat: https://learn.microsoft.com/powershell/module/defender/get-mpthreat
- Get-MpPreference: https://learn.microsoft.com/powershell/module/defender/get-mppreference

All six applications remain **UNRELEASED**. A clean-looking CLI observation does not make the installed product safe or authorize a release.
