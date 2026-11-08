# Final Vestige Labs R280 — strict private Defender receipt binding

**2026-11-08 · Issue #73 · DRAFT / QD + founder HARD HOLD · no production merge**

Base: immutable R279 `986df324f26463e043b29310274181aef45f1652` / draft PR #1574. This branch never targets production `main` directly.

## Confirmed acceptance weakness

R279 added a mandatory native Windows Defender scan and pinned its report's bytes, but the private candidate runner checked only the existence, size, file identity and SHA-256 stability of `defender-candidate-evidence.json`. A synthetic, incomplete or contradictory JSON body could survive those gates when a child runner returned zero. The report was not independently checked against the prior six-executable R9 attestation. This is an evidence-consistency weakness; **it is not evidence that an actual Defender scan was bypassed or that malware was distributed**.

## R280 implementation

- New `scripts/defender_receipt_contract_r280.py`: strict integer-only JSON decoder; duplicate-key and nonstandard numeric rejection; exact 17-field R111 report schema; canonical provider/platform/status and Defender health/environment checkpoint strings and counts; literal false release, malware-clearance and premium-authority flags.
- The six ordered EXE entries, hashes and custom-scan status must exactly match the **independently attested, SHA-256-pinned R9 report**. The R9 report hash and checksum inventory digest must match the Defender receipt. Reject unknown fields, private paths, missing/duplicated apps and forged success/certification claims.
- The real, non-injectable `offline_windows_candidate_r269.py` CLI now reads the pinned R9 bytes and validates the Defender JSON **inside the already existing descriptor-custody read** before recording the Defender SHA-256. Its final same-run report hashes, source binding and toolchain gates remain mandatory. Synthetic plan-runner injections are intentionally not treated as authentic candidate acceptance.
- New `tests/test_defender_receipt_contract_r280.py`: 13 test methods with dozens of negative subcases spanning R9 identity, six hashes, statuses, extra data, JSON ambiguities, timestamps, checkpoints and flags.
- Ubuntu and Windows desktop-build workflows include normal and optimized Python targeted tests. All child logs and customer financial data remain private; no app engine, money calculations or compliance decision behavior changed.

## Local test evidence and scope

The **exact committed Git blobs** of the new helper and test file were tested on **Linux Python 3.13.5** from a minimal local checkout with a small shim implementing the same strict R273 JSON decoder policy (the full R273 repository file was not present locally). Git blob SHAs:

- Helper: `c076ffee53bfb2aadd96394382310152fa828f74`
- Tests: `53261b5e6b98b4c2d206aaa27712c1b170906ccc`

Commands:

```text
python -W error -m unittest discover -s products/desktop/tests -p 'test_defender_receipt_contract_r280.py' -q
    13 tests PASS
python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_defender_receipt_contract_r280.py' -q
    13 tests PASS
python -m compileall -q [new helper and tests]
    PASS
```

**26 method executions passed.** These exercise only the focused JSON/receipt semantics using synthetic R9 and Defender records. They **do not** establish full-repository compatibility, integrated private-runner acceptance, a genuine Defender scan, live EXE smoke testing, QD approval, or entitlement protection. The R273 dependency used locally was a minimal policy-equivalent shim, not its full byte-identical committed file. The runner and workflow changes have not been executed end to end.

## Hard release gates and next action

Hosted Actions previously failed before assigning runners on R279 run #42474898340 (Ubuntu and Windows jobs, no steps). Investigate GitHub Actions billing/spending caps and runner availability; rerun the unchanged R280 head on both OSes. Then run the private candidate pipeline on a trusted Windows 11 x64 workstation with actual six standalone EXEs and pinned R9/Defender reports. Continue with accessibility, Defender verification, premium access controls, independent QD review and founder approval.

**Do not merge to production, publish binaries, invent download links, label the applications released, or expose GrantAudit/ProcureGuard premium files.**
