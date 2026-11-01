# R117 — Offline sealed handoff to a physical Windows 11 reviewer

**DRAFT / RELEASE HOLD.** This optional tool packages the six already-built Windows x64 candidates and their R9 smoke-test evidence into a single **encrypted** transfer envelope. It does not release executables, license either premium app, attest independent QA, authorize a sale, upload an artifact, or change the production site.

Source: `products/desktop/scripts/sealed_candidate_handoff_r117.py` — Python 3.12+ with the already pinned `cryptography==46.0.4`. This is **operator-only**, subject to QD/founder authorization before any actual premium-candidate transfer.

## Preconditions

1. The operator privately possesses the actual, matching six PE32+ AMD64 executables (LedgerDiffLite.exe, InvoiceTwinScout.exe, SpendMapLite.exe, PolicyDeltaDesk.exe, GrantAuditStudioPro.exe, ProcureGuardStudioPro.exe), their exact `SHA256SUMS.txt`, and an R9 native-Windows smoke report with `status=windows_smoke_passed`. Checksums alone cannot reconstruct or provide candidate EXE bytes. Existing GitHub Actions deliberately retain only source and checksum reports; **R117 does not change CI artifact uploads**.
2. The exact lowercase SHA-256 of the original R9 report is independently established and communicated securely to both endpoints; never trust a digest supplied only inside the encrypted envelope.
3. Use access-controlled private local folders. On POSIX the tool rejects group/world-accessible key files and destination parents; on Windows the human operator **must verify NTFS ACLs and BitLocker/EFS protections** because the tool cannot certify them. Keep private keys away from the sealed transfer transport.
4. QD must approve access to premium candidate bytes and the exact transfer workflow before any actual transfer. The sealed archive contains premium executables; encryption alone is not commercial entitlement.

## Operator commands (examples; substitute trusted paths)

Create a fresh random **32-byte binary** key under a private path; key bytes are never printed:

```powershell
python products/desktop/scripts/sealed_candidate_handoff_r117.py keygen --key-file C:\PRIVATE\key.raw
```

Seal the six EXEs, checksum inventory and R9 report after the source-owned R9/PE/hash attestation:

```powershell
python products/desktop/scripts/sealed_candidate_handoff_r117.py seal --dist C:\PRIVATE\candidates --r9-report C:\PRIVATE\r9-smoke.json --expected-r9-sha256 <64-character-sha256> --key-file C:\PRIVATE\key.raw --bundle C:\PRIVATE\six-exe-review.sealed
```

Transfer **only the encrypted envelope** through an approved private channel, then deliver the 32-byte key through a distinct trusted/authorized channel (not a workflow flag, log, GitHub artifact, website, or public URL). Independently communicate/verify the R9 SHA-256 at the reviewer endpoint. On physical Windows 11:

```powershell
python products/desktop/scripts/sealed_candidate_handoff_r117.py unseal --bundle C:\PRIVATE\six-exe-review.sealed --key-file C:\REVIEWER-PRIVATE\key.raw --expected-r9-sha256 <independently-checked-sha256> --output C:\REVIEWER-PRIVATE\intake-r117
```

After successful intake, `intake-r117/exes/` contains the six private candidates and checksum list; `intake-r117/evidence/r9-report.json` contains the smoke report. The tool re-checks all R9/PE/hash custody before the intake directory is exposed. Existing destination paths are never intentionally overwritten.

## Technical gates

- Fixed order and exact eight fixed archive entry names; no user-provided paths, wildcard extraction, tar/ZIP traversal or external data.
- Streaming AES-256-GCM with a fresh independent 96-bit nonce per file, 16-byte authentication tag, raw metadata header plus record index as additional authenticated data. Raw random 256-bit key; no guessable passwords. Original source digests are rechecked during encryption.
- Maximum six 512-MiB candidates; checksum list <= 8 KiB, source evidence <= 256 KiB, metadata <= 8 KiB. Ordinary single-linked input file checks, rejection of modified files and symlinks, strict metadata schema/uniqueness, fail-closed bad key/tampering/truncation, and exclusive encrypted-file publication.
- Intake decrypts only into a private staging directory; verifies per-file tags, SHA-256, exact EOF and original source-owned R9 candidate consistency before renaming staging into the requested private destination. On failure it deletes staging. Never makes compliance decisions or runs the EXEs.
- All tool statuses have `release_authorized: false`; the archive is not a signature and cannot prove source authenticity against a malicious party holding its key.

## Limits and mandatory separate release gates

Passing synthetic unit tests does **not** demonstrate secure handling of actual Windows executable bytes, independently reviewed Windows ACLs or endpoint compromise resistance. Authenticated encryption cannot mitigate an insider who has the key or guarantee that Windows Defender cleared the applications. R118's follow-on Windows CI check now creates an **ephemeral key, bundle and private decrypted intake on the same hosted runner**, then deletes all three within that run. **None is uploaded or transferred to a physical reviewer**; it is not independent evidence custody or Win11 acceptance. The key must never travel alongside the encrypted archive. Windows rename and filesystem permission expectations need QD review on a real NTFS system.

The physical Windows 11 reviewer still needs actual Defender/EDR/detection-history review, R109–R110's 46 physical keyboard/NVDA/contrast/scaling acceptance checks, SmartScreen/code signing, genuine premium entitlement and authenticated checkout/download protections, independent QD exact-SHA review, and founder approval. **All six programs remain unreleased.**

## Test evidence

`python -m unittest discover -s products/desktop/tests -p 'test_sealed_candidate_handoff_r117.py'` and the same command with `-OO` exercise 32 synthetic security regressions: AES-GCM six-file round-trip, separate output integrity, wrong keys, tampering, truncated/extra bytes, nonce uniqueness, duplicate/bogus metadata, no-clobber behavior, symlink and key permissions, pin mismatch and reject non-smoked R9 claims. The R9 verification is deliberately stubbed for synthetic fake-PE data; real six-PE native build tests remain separate CI/reviewer requirements.
