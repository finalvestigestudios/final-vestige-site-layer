# Final Vestige Labs R279 — mandatory native Defender candidate acceptance

**2026-11-08 · Private engineering evidence · DRAFT · QD/founder HARD HOLD**

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
Stacked only on [R278 draft #1566](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1566), not production `main`.

## Defect and scope

R269–R278 private Windows builder verified six PE32+ candidates, SHA-256,
source receipt, real executable smoke, and R9 attestation, but did **not**
invoke the existing R111 native Microsoft Defender scanner before printing
its private successful-candidate message. R111 also failed to bootstrap
its Git-owned sibling imports when invoked using the build pipeline's
isolated Python `-I`. Its custom file scan had previously left Defender
remediation enabled; a zero status alone does not prove no threat was
detected, since remediation may produce a zero exit.

R279 connects the existing native scanner to the private build acceptance
path and makes Defender custom scanning non-remediating. No application
calculation, customer data, licensing key, or release authorization changes.

## Exact private gate order

1. Run and retain normal/optimized full source-suite evidence and verify
   six named source smokes and source-to-build binding.
2. Capture and verify source/toolchain manifests; build all **six**
   standalone Windows x64 one-file applications via PyInstaller.
3. Inventory SHA-256 and PE architecture; execute actual `--smoke-test`
   on each Windows executable; retain bounded R9 Windows evidence.
4. Independently attest the original R9 evidence under its SHA-256 pin;
   recheck source/build and toolchain manifests.
5. **New mandatory step:** run
   `python -I products/desktop/scripts/defender_candidate_scan_r111.py`
   privately, passing the pinned R9 SHA-256 and a distinct *unpublished*
   Defender report path. This child rejects non-Windows 11 workstations,
   untrusted scanner locations/signatures, inactive/passive/unhealthy
   Defender, stale signatures, unexpected exclusions/history,
   modified artifacts and nonzero scan status.
6. All six custom file scans use
   `MpCmdRun.exe -Scan -ScanType 3 -File <exe> -DisableRemediation`.
   The external command is argument-vector based, with no shell,
   suppressed output, fixed timeouts, and no private paths in public logs.
7. Require a real, bounded, regular, unlinked Defender evidence file.
   SHA-256 pin it; repeat build and toolchain checks; rehash **both**
   R9 and Defender receipts and source-test receipt before accepting
   *private candidate readiness*. An absent report, failed scanner,
   or changed receipt rejects the candidate.

**Total child stages:** 43 (prior 40 plus Defender scan and two postscan
source/tool checks). This stage count is an *orchestration plan*, not a
native executable or antivirus test result. Only an owner-run trusted
Windows 11 x64 workstation can supply real scan evidence.

## Microsoft syntax and limitations

Microsoft documents `-DisableRemediation` for custom file scans. Without
it, success can follow remediation. With it, detections may not appear in
the same history/event-log channels as ordinary scans, so a **nonzero**
custom-scan result is essential to the rejection policy. The scanner still
observes exclusions/history/health before/after scans; none of those
observations certifies malware freedom.

Reference: [Microsoft Defender command-line arguments](https://learn.microsoft.com/en-us/defender-endpoint/command-line-arguments-microsoft-defender-antivirus).

## Regression coverage

- New `tests/test_native_defender_bridge_r279.py`: eight synthetic
  integration contracts for six-build/scan ordering, immutable R9 pin,
  nonzero scan denial, absent Defender receipt denial, report mutation
  and deletion denials, release hold text, and an actual isolated
  `python -I .../defender_candidate_scan_r111.py --help` subprocess.
- Adapted R269/R270/R271 fake-runner tests to produce **synthetic** Defender
  evidence and assert 43 subprocess stages, not 40.
- Fixed the R271 old synthetic fixture's invalid app-to-engine IDs and
  missing source commit field; this aligns it to the existing strict
  smoke-receipt contract.
- Adapted R111 scanner argv tests to require `-DisableRemediation`.
- Wired R279 focused checks and `-I` import preflight to both Ubuntu
  source and Windows CI jobs, normal and optimized Python modes.

**Do not mistake passing synthetic tests for an actual AV scan.**
Hosted GitHub Actions has repeatedly failed before runner allocation;
the real native gate, complete test suite and native builds are **NOT
verified** until successfully executed and independently reviewed.

## No-release gates / owner next action

An owner must restore Actions runner allocation or run the private candidate
pipeline locally on a trusted Windows 11 x64 computer with preinstalled
trusted tools, a separate access-controlled workspace and active Microsoft
Defender. Review the six actual EXE SHA-256 outputs, R9 attestations, Defender
reports, keyboard/screen-reader/high-DPI acceptance, premium entitlement and
download protections, then independent QD and founder authorization.
**No production merge, public EXE, public premium link, download URL,
malware clearance claim, or automated compliance approval is authorized.**
