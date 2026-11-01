# R111 — offline Microsoft Defender candidate scan (DRAFT / RELEASE HOLD)

**2026-11-01 · Issue #73 · Stacked on R110 draft PR #443, not production.**

## Why

R110 verifies hashes and the identity of *future* physical Win11 accessibility witnesses, but does not execute an anti-malware scan. R111 adds an executable **operator-only, offline, fail-closed** scan command for the exact six Windows AMD64 candidates. The R111 CI regression step tests scanner policy only: it **never runs Microsoft Defender on GitHub's Windows Server runner and does not certify AV clearance**.

## Execution on a trusted Windows 11 x64 workstation

Build all six portable EXEs privately and retain the same `dist/SHA256SUMS.txt` and R9 `build/offline-candidate-evidence.json` produced by `release_gate.py dist --smoke --report ...`. Verify the actual R9 report with `report_attestation.py`; independently record its exact SHA-256 **before** starting review. Do not move files between the R9 check and the scan.

In a trusted PowerShell session from the checkout root:

```powershell
$env:PYTHONPATH = 'products/desktop'
$pin = (Get-FileHash -Algorithm SHA256 -LiteralPath 'build/offline-candidate-evidence.json').Hash.ToLowerInvariant()
python products/desktop/scripts/defender_candidate_scan_r111.py dist build/offline-candidate-evidence.json --expected-r9-sha256 $pin --report "$env:USERPROFILE\Desktop\fvs-private-defender-r111.json"
if ($LASTEXITCODE -ne 0) { throw 'R111 AV scan or candidate custody failed: RELEASE HOLD' }
```

The example computes the report's current SHA-256; for independent *historical* authenticity the reviewer must compare it with a separately retained trusted hash. Do not store real customer files anywhere in the scan folder. Protect the R111 report locally and keep it **out of GitHub, Actions artifacts, WordPress, and any public URL**.

The scanner requires (1) an actual Windows 11 x64 **workstation**, not Windows Server/Windows 10/Linux, (2) a current active local Microsoft Defender Antivirus instance, signature age <=3 days, real-time and AV service enabled, (3) a signed local `MpCmdRun.exe` from known Defender install paths, and (4) a verifiable R9 report with **six native Windows smoke-passed EXEs**, six exact binaries and unchanged checksum inventory.

For each of six canonical EXE names, the tool performs complete candidate/manifest rehashes **before and after** synchronous Defender custom-file scanning, rejecting nonzero exit codes (including detected threats), missing scanners, scan timeouts, quarantines and any modified candidate bytes. It repeats Defender health verification at the end. Commands use argument arrays rather than a shell; tool output, file paths, OS errors and scanning diagnostics are suppressed to protect local financial privacy. Only a completed all-six scan emits a no-clobber JSON report outside `dist` with app names, hashes, report identity and status; it contains **no customer data, local paths or licensed editor**.

## Verification and limits

Run the new synthetic suite without Defender (neither mode constitutes an AV scan):

```powershell
python -m unittest discover -s products/desktop/tests -p 'test_defender_candidate_scan_r111.py'
python -OO -m unittest discover -s products/desktop/tests -p 'test_defender_candidate_scan_r111.py'
```

The **25 R111 adversarial/synthetic tests** exercise OS provenance, inactive or missing scanner refusal, command safety, failure/timeout handling, checksum drift, independence of R9 pinning, exactly-six processing and release flags. Both normal and `-OO` modes are mandatory in both existing source CI jobs. The `ci_artifact_policy.py` two-bundle upload allowlist remains unchanged; no executables, customer inputs or private AV records may be uploaded.

A **zero exit from Defender is NOT proof of no malware**, a multi-engine AV/EDR clearance, an independent signature, a completed Windows 11 accessibility review or a publishing decision. Definitions and behavior depend on the trusted review machine. A compromised workstation or an adversary who can replace both candidate and its independently retained digests defeats this custody model. The R9 report's original `malware_scan_verified=false` intentionally stays unchanged; this is a *separate* operator evidence lane. Native execution of this scanner is **pending**, not inferred from passing synthetic CI tests.

## Remaining release gates

Physical 46-check Win11 keyboard/NVDA/high-contrast/scaling review, real R111 offline scan and independent AV/EDR decision, publisher signing/SmartScreen review, real paid licensing and authenticated premium download controls, independent QD review of the **exact final head**, and founder approval. Do not merge to production or distribute any free/premium EXE. All six applications are **UNRELEASED**.
