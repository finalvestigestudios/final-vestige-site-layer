# R244 — Ambiguous hardlink-publication failure (Issue #73)

**Release state: DRAFT; QD and founder HARD HOLD.** This change only hardens private `SHA256SUMS.txt` construction for the six named offline Windows x64 candidates. It is not an EXE build, malware inspection, Authenticode signature, entitlement or publication approval.

## Defect and limited correction

R243 records the verified staging inode **before** `os.link(stage, target)`, but sets a `published` flag only **after** the call returns. If a wrapped/ambiguous hardlink operation creates the target and then raises, R243's `finally` skips owned-target rollback because the flag is still false; a checksum manifest can remain despite a failed build. The R244 change removes this unreliable success flag. On any failed operation after the staging identity was recorded, cleanup checks the destination's **`lstat()` device and inode** against that pre-link identity and removes the link only when it still owns it. Ordinary pre-link errors leave no target. An intervening foreign regular file, symlink, or directory is not deleted.

This is **best-effort cleanup**, not a claim of complete TOCTOU immunity: there remains an external replacement race between `lstat()` and `unlink()`, and cleanup can fail due to filesystem permissions. In those cases the candidate folder must be manually quarantined and inspected rather than released. This work does not authorize a Windows release.

## Exact reproduction and verification

- Parent: R243 immutable head `3478fd4229dd619f56775adf0933a8eca44016c2`. Original source `build_inventory.py` Git blob `44af90fe06e80a7f7575391da9985060716fcb80` and `candidate_guard.py` blob `cc92c58246196f284ea12659621a347bd96e4fe9` were reconstructed locally from GitHub and checked byte-for-byte against those Git blob hashes. The two inherited test blobs were also independently checked: R243 `b06cd2249487cc1d21392f971efc57ca3237d8fb`, R242 `163a4ae329017fb57d8d0db36fd659177ade207a`.
- New fault-injection suite `test_inventory_link_ambiguity_r244.py` uses real local hardlinks and **synthetic, deliberately invalid** executable payloads. With unmodified parent R243 code, **6 of 12 tests failed** and 6 passed: after-link exceptions strand `SHA256SUMS.txt`.
- With the R244 source fix: **12/12** new tests and **31/31** inherited R242/R243 tests pass normally; the same **43/43** pass under `python -OO -W error`. **86/86 successful local test-method executions**, no skips, Python compileall pass. Linux CPython (record local version in issue comment).
- Full repository, hosted Ubuntu, native Windows 11, packaging, malware scan, UI accessibility, and gated premium-download integration remain **unverified**.

## CI and release workflow

The pre-existing desktop workflow includes a complete normal/optimized source suite prior to Windows packaging. The new `test_inventory_link_ambiguity_r244.py` follows the `test_*.py` discovery convention and will be included by that suite **once Actions runners execute**. Hosted CI is blocked at runner scheduling (e.g. R243 Actions #42309428196: Windows and Ubuntu jobs failed without steps or logs). Do not count these as test executions.

**Next highest-impact action:** owner diagnoses GitHub Actions billing/spending/permissions/runner availability, reruns R244 exact SHA, then obtains native Windows 11 x64 full-suite and actual private six-EXE smoke/checksum/Defender/accessibility evidence. Independent QD, premium access controls and founder approval still gate release. No change to Decimal calculations, user files, local-first processing, human compliance review, WordPress, production branch, or release downloads.
