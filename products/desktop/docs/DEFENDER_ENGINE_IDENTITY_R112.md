# Labs R112 — installed Defender engine identity hardening (DRAFT / HOLD)

Issue #73; builds **only** on R111 draft #450. This is source/testing work, not a production merge, executable publication, or commercial license authorization.

## Specific defect addressed

R111 correctly checked all six packaged Windows x64 EXEs before and after each custom Microsoft Defender command, and checked the **signer** of its scanner during first/final health checks. However it did not pin the **scanner executable's own bytes and file identity** across the six scans. A Defender Platform update or intervening file swap could leave an R111 evidence report whose six commands had not all used the same reviewed scanner image. The R111 discovery code also sorted installed Platform directories **lexicographically**, which may prefer `4.18.9` over `4.18.10`.

R112 adds `scripts/defender_engine_custody_r112.py` and integrates it into the existing private operator scanner. The installed engine is read through a single file descriptor, SHA-256 hashed within a 128-MiB cap, and checked for regular-file type, one link, file size, path-to-descriptor identity and stable per-view ctime/mtime metadata. Windows **path-versus-descriptor ctime differs legitimately**; only that cross-view ctime comparison is relaxed. Complete same-view before/after checks remain mandatory. A changed SHA-256 **or** file identity now blocks the private scan.

R112 also:

- Selects installed Platform engines by strictly parsed numeric version instead of string order. Unrecognized or linked version folders are ignored. A legacy Microsoft Defender installation remains an explicit fallback when no suitable installed Platform image is present.
- Checks the exact observed scanner identity **after signed health preflight, before and after each of six scan commands, and after final health preflight**: 14 rechecks in a complete run.
- Requires a trusted Authenticode-valid signature with a **Microsoft Corporation CN** rather than an arbitrary signer whose name merely includes the word “Microsoft.” A signature or scanner mismatch stops the operation without a report.
- Emits `scanner_sha256` and a nonauthorizing scanner-custody label in the **private** R111 report. It emits no scanner pathname, local user information, customer file names, financial data or premium editor.
- Leaves six-candidate SHA-256/PE/R9 smoke checks, no-overwrite report publishing, and `release_authorized=false`, `independent_malware_clearance=false` and `premium_distribution_authorized=false` unchanged.

## Tests and CI

`test_defender_engine_custody_r112.py` supplies **19 independent synthetic unit tests** for metadata/byte changes, same-size mutation, inode replacement, deletion, hardlinks, symlinks, size limits, per-view Windows ctime parity, version ordering and malformed versions. Five further R111 integration tests check strict signed publisher identity, exception privacy and fail-closed mid-scan tamper. R111 now contains 31 test methods instead of 26.

Both source CI jobs enforce the R111 + R112 regressions normally and with Python `-OO` **before** the complete source gate and six Windows executable packaging step. Full six-binary source/R9/native GUI/keyboard/scale gates remain mandatory. No new artifacts are uploaded; the existing evidence-only allowlist remains in place.

Local self-contained verification (tests do not call actual Defender):

```powershell
python -m unittest discover -s products/desktop/tests -p 'test_defender_engine_custody_r112.py'
python -OO -m unittest discover -s products/desktop/tests -p 'test_defender_engine_custody_r112.py'
python -m unittest discover -s products/desktop/tests -p 'test_defender_candidate_scan_r111.py'
python -OO -m unittest discover -s products/desktop/tests -p 'test_defender_candidate_scan_r111.py'
```

On a **trusted, physically operated Windows 11 x64 workstation**, follow the existing R111 runbook `docs/OFFLINE_DEFENDER_SCAN_R111.md`, retaining the six private EXEs, exact pinned R9 report, R111 private scan report and independent reviewer records **outside GitHub**.

## Honest limitations and next highest-impact step

These checks observe file integrity at multiple points; they cannot create an atomic guarantee that a privileged adversary never swapped a scanner between the final fingerprint and process execution. A trusted host with protected Defender directories is required. A Defender engine update during review rightly forces a complete rerun. Microsoft-signed scanner **does not certify** absence of malware in the six products.

**Defender exit 0 can mean a threat was remediated**, not just “clean.” R112 does not reconcile Defender detection/remediation history or claim independent AV/EDR clearance. All 46 hands-on Windows 11 keyboard/NVDA/high-contrast/real scaling checks, actual Defender scanning on the pinned private candidate set, signing/SmartScreen review, authenticated paid-entitlement distribution, exact-head independent QD review and founder authorization remain outstanding.

**All six desktop apps stay UNRELEASED.** Do not merge draft branches to production, publish free or premium EXEs, upload private scan/witness records, or alter WordPress without separate QD/founder approval.
