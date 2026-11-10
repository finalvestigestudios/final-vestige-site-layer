# R338 — post-link release-report custody for six Windows x64 utilities

**2026-11-10 · DRAFT / QD + founder HARD HOLD**. Scoped only to six-app verification JSON for LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, ProcureGuard Studio Pro. Based exclusively on R337 draft PR #1943 (parent 5e9877f52d38671d2f3a402a141f58564045b798). Production main unchanged.

## Reproduced defect

R337 read back the temporary staging bytes but accepted publication without checking the final hardlink target after os.link. Reconstructed *exact* predecessor report_evidence.py blob 5b68694c5c40daa1ee7070f060b6f540c40b7533. Fault-injected separate copy, same-length corrupted copy and link no-op: predecessor ACCEPTED all three; R338 REJECTED all three.

## Working change

New report_link_witness_r338.py requires ordinary files, same dev/inode for staging and published paths, expected size, opened-descriptor identity, exact final JSON bytes, and post-read identity stability. Uses O_NOFOLLOW if supported; rejects symlink paths. Closes reader descriptors on failure. report_evidence.publish_report now demands that witness before success and preserves both disputed paths on failed witness without attempting an unsafe deletion. Successful publications still use exclusive hardlink, preserve no-overwrite semantics, and remove their ordinary staging path. Exceptions are privacy-redacted. The publisher does not change financial math, local-first input processing, review decisions, or premium gating.

## Local verified execution

Linux CPython 3.13.5, real temporary filesystem, synthetic JSON, no real executables or personal financial files. Both modes:

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_report_link_*_r338.py'
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_report_link_*_r338.py'

18 witness tests + 8 publisher integration tests = **26/26 standard PASS, 26/26 optimized PASS, 52/52 executions, zero skips**. Python compilation PASS. Tests cover accepted hardlink, identical-but-independent copy, bad bytes, short/extra bytes, in-place mutation, swapped source, symlinks, missing target, descriptor fault/closure, redaction, no overwrite, suspicious-stage preservation. Source and tests matched their actual Git blobs:

- report_evidence.py: 09babcfa5acc40b86f98eec3a191adca34244d2b
- report_link_witness_r338.py: 12054deb1fa231ccd2911d1d3bfe6b5d720d4757
- test_report_link_witness_r338.py: 72e95aebf299a2dd1537312b6e2bea34adf94961
- test_report_link_integration_r338.py: 248af174cec88efee7b553d5fc3e7a6ac6711415

Hosted Ubuntu and Windows workflows now request both new modules in normal and -OO modes; actual CI results must be checked independently.

## Residual risks and release holds

The witness establishes momentary byte and inode consistency, not an immutable signature. A same-user actor may mutate after verification; pathname-based cleanup of the ordinary *successful* staging file retains a theoretical check-to-unlink race (not eliminated here). If a post-link witness fails, candidate destination and private staging JSON may persist for human inspection; never treat a leftover file as a valid report or auto-distribute it. Native Win11 filesystem/ACL semantics and six-EXE integration are UNTESTED. Reports are not QD approval, signing, malware scan, compliance judgment or premium entitlement proof. No binaries published and no production changes.

R337 hosted CI run #42892105338 completed failure on 2026-11-10, with both source-tests and windows-build jobs lacking recorded steps/logs; cause unconfirmed. Owner must inspect Actions billing/spending/runner/workflow eligibility, run full standard and optimized regression including 22 genuine AES-GCM tests and legacy R38/R337 report tests, then native Windows 11 x64 smoke/Defender/checksum/accessibility/entitlement acceptance. Independent QD and founder approval required before merge or release.
