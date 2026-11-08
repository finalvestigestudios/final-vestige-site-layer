# Labs R271 — Private Windows evidence double-pin

**Status: DRAFT only; GitHub issue #73. Independent QD + founder release/merge HARD HOLD.**

## Defect and scope

The R270 offline Windows candidate runner checked `offline-candidate-evidence.json` with `lstat()` and then read it via `Path.read_bytes()`. A path swapped to a symlink between those calls could be followed by the read. More importantly, the parent took **no final report hash check** after the independent report-attestation child and subsequent source/toolchain checks. A swapped, deleted, or modified report after the attestation step could leave the private candidate reported successful, despite retained binary evidence no longer matching the data attested by the child. This was reproduced against the exact R270 script using synthetic report mutation: three specific regression cases failed to reject report replacement/unlink/symlink after attestation.

R271 adds a bounded (1–65,536 bytes), descriptor-based `_private_windows_report_sha256()` helper, requiring a native regular file with exactly one link. It compares path/descriptor identities before reading and checks unchanged descriptor and path identities afterward. `O_NOFOLLOW` is used when supported. This preserves Windows-specific path-vs-descriptor mode/ctime differences while enforcing within-view identity consistency. The parent computes the report hash after the six-EXE release-gate command and requires the **same report SHA-256** again after independent attestation and the final source/toolchain checks. A missing/replaced/linked/altered report fails closed with a fixed diagnostic; no private file content is printed.

The existing `report_attestation.py` is still responsible for parsing and validating Windows report content and binary custody. This patch does not claim cryptographic signing, protection against hostile privileged filesystem actors, post-exit tamper protection, malware clearance, or actual Windows verification. It adds no network calls, downloads, publication, automatic compliance decisions, or changes to financial engines. All six distinct application targets remain in the 40-stage private plan, with premium EXEs restricted to the operator-controlled private workspace.

## Measured local evidence (2026-11-08 UTC)

- Reconstructed the precise R270 source Git blob `de8eccb9bb50d73ac713260dc9f3cb8fb4ec1872` before patching. The original inherited R269 and R270 regression files were also reconstructed **byte-identically** to their Git blobs: `efe3658fb9a7167e070e8f86c44e3fa186239af6` and `e21c663f502bf28e53355f41dc56279f29fc373b`.
- New R271 regression module: **17 methods**, covering regular/empty/oversize/missing/linked evidence, stable SHA-256, descriptor/path replacement, in-read mutation, fixed diagnostics, unchanged 40-stage/six-build plan and attestation-time replace/unlink/link failures. All synthetic/fake process outputs; no customer data.
- **Before code fix:** new suite 3 failures / 13 errors (the missing-helper errors are expected for the new API). Three direct post-attestation mutation cases specifically exhibited the previously permitted success.
- **After code fix:** R269+R270 inherited **34/34** normal and **34/34** `-OO` tests passed; new R271 **17/17** normal and **17/17** `-OO` passed. **Total 51/51 normal and 51/51 optimized = 102/102 successful focused test executions**, no skips on the Linux test machine. Python `py_compile`/`compileall` passed. Linux CPython 3.13.5; no native Windows execution.
- Test commands from the recreated source/test workspace:

  ```sh
  python -W error -m unittest discover -s products/desktop/tests -p 'test_offline_windows_candidate_r*.py'
  python -W error -m unittest discover -s products/desktop/tests -p 'test_offline_windows_report_custody_r271.py'
  python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_offline_windows_candidate_r*.py'
  python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_offline_windows_report_custody_r271.py'
  python -m compileall -q products/desktop/scripts/offline_windows_candidate_r269.py products/desktop/tests/test_offline_windows_report_custody_r271.py
  ```

These are **focused local regression tests**: the 40 build/attestation subprocesses were faked, and the full repository test suite was not executed. No Windows PE, actual six executable build, Defender scan, physical GUI/accessibility pass, or premium gated distribution was verified.

## Independent acceptance / next step

1. Restore GitHub Actions runner availability (prior R270 run #42436690172, 2026-11-08 UTC: both jobs failed before recording steps). Rerun this unchanged draft head on Ubuntu and Windows with complete suites.
2. On a trusted Windows 11 x64 workstation, execute the existing R269 private candidate plan with preinstalled audited dependencies; retain the offline source-suite receipt, checksum inventory, PE/executable smoke results and attestation report, and verify that R271 report bytes remain pinned.
3. Private Defender/EDR scan, keyboard/screen reader and high-scaling tests, entitlements/payment & secure premium delivery; independent QD and founder review before merging or publishing. **No binaries, premium links or production site changes are permitted in this draft.**
