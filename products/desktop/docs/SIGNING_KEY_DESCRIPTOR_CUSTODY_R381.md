# Labs R381 — Offline signing-key descriptor custody (DRAFT / release HOLD)

Issue #73. Scope: operator-only encrypted Ed25519 PEM for **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. The four free desktop apps, premium license format and authorizations, financial engines, WordPress site, and production branch are unchanged. This draft is stacked on R380 draft PR #2212.

## What was unsafe and what changed

The inherited issuer did an initial symlink check and used os.open/fstat to read its private encrypted PEM, but did **not** reject hardlink aliases or bind the opened descriptor to the original path across the read. The old exception path used explicit exception chaining for OS and cryptography failures. This could retain confidential operator paths inside __cause__ / __context__, even when the outer displayed message was generic.

The new issuer-only signing_key_guard.read_signing_key enforces:
- Lstat before open; regular, single-link, bounded <=16 KiB, non-reparse, POSIX owner-only and same effective owner;
- O_RDONLY/O_NOFOLLOW (where available), O_NONBLOCK and no create/write flags; one FD, bounded read and unconditional close;
- Descriptor/path identity witnesses before and after reading; reject path swaps, in-place length/time metadata changes, special files, hardlinks, symlinks and exposed reparse attributes;
- Private OS errors translated **after exiting** their handlers, without retained sensitive Python exception chains;
- PEM decrypt failures also translated outside the cryptography exception handler in license_issuer.py;
- Still refuse key files within Git worktrees; still require manually authorized, separately protected registry issuance. The key module is NEVER bundled in customer EXEs.

## Executed focused proof (2026-11-12; Linux Python 3.13.5)

The following commands ran with the exact SHA-verified committed helper and regression source in an isolated local directory (not a complete HEAD checkout):

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_signing_key_guard_r381.py'
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_signing_key_guard_r381.py'

- **19/19 PASS** standard, **19/19 PASS** -OO, **38 passing focused executions**; compileall PASS.
- Exact Git blob hashes: helper 08cc2df2d8dcafd3ef4eb62311bb5baedb6d57a8; tests a79e7e51e771f5f200fafa59ed6d6611683bfe36.
- Coverage: real synthetic encrypted PKCS#8 Ed25519 sign/verify; private regular reads; missing/oversize/invalid limits; symlinks, hardlinks, directory, FIFO, POSIX permission; file swapping before/after open, in-place growth, Windows reparse-metadata emulation, private OS canaries in open/fstat/read/lstat/close, FD closure.
- Windows-specific race coverage avoids unsafe unlink of an open file and instead injects metadata mismatches. **Native Windows execution not yet verified.**
- 4 CI test invocations added: Ubuntu/Windows x standard/-OO, before build. Desktop workflow now 222,713 characters, below the existing reviewed 224 KiB size limit.

## Material limitations and next gate

This is best-effort file/path custody, not a defense against a privileged attacker with control of parent directories or a metadata-preserving rewrite. Windows ACL custody and reparse semantics require native verification. Current local tests execute the **exact new helper and tests**, plus one real cryptographic roundtrip; they do not establish full integrated license_issuer.py execution or six-app release readiness. Full R12/R13/R16 Ed25519 integration, all 22 genuine AES-GCM cases, native Windows x64 candidate builds, Defender/EDR scans, accessibility observations, and premium fulfillment gate checks remain required.

Hosted GitHub Actions on R380 prior run #43244879256 failed before steps for both Ubuntu and Windows jobs; exact infrastructure cause unconfirmed. Smallest owner unblock: inspect the failed-check annotations and Actions billing/spending/runner eligibility, then run this draft commit's workflow.

**Approval HOLD:** no merge, release, site publication, executable upload, key distribution, unrestricted premium URL or QD bypass. Independent QD review and founder approval remain required.
