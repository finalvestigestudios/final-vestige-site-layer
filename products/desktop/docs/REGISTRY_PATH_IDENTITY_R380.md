# R380 — Offline premium SQLite registry path identity (DRAFT / release HOLD)

Issue #73. Applies to operator-side issuance for **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. Four free engines, money calculations, signed entitlement format, human review, storefront, and site publication remain unchanged. Stacked on R379 draft PR #2203, NOT production.

## Demonstrated prior gap

The inherited registry preflight used Path.is_symlink and os.fstat but never bound the public registry pathname to the opened descriptor. A single-link, private, otherwise valid regular file could replace the path before or after preflight open. An OS-exposed Windows reparse attribute was not checked. SQLite itself opens the path later in a separate call; registry directory custody remains essential.

Against **exact original R377 helper Git blob** b46da03bc853cf7d7203f48261b6dd3fe27bac10, **9 of 12** new synthetic tests failed on Linux. This is a regression-detection count, not nine distinct exploits.

## Code

Updated registry_file_guard.py obtains lstat identity before opening, validates a private single-link regular file and exposed reparse attributes, opens and checks the descriptor, validates another pathname witness, and rejects missing-to-existing races, same-byte replacements, metadata discrepancies, and new reparse attributes. Fresh files are still created exclusively at mode 0600. Existing registry bytes are neither read nor rewritten by preflight. Raw descriptor closure and fixed public errors remain, with no private Python exception chains.

**Limit:** there is still an unbound interval between closing the inspection descriptor and SQLite subsequently opening the pathname; no guarantee against privileged/same-user parent-directory swaps. Windows reparse behavior is synthetic mock coverage only, not native validation.

## Local evidence (2026-11-12; Linux Python 3.13.5)

- New exact helper blob: eda4e4a29d44bcea192c0631a64009df9f2dae7c.
- New exact 12-method test blob: f2336ac2350ff00b39ca5ab76c8252bb16adc466.
- Inherited R377 14-method tests reconstructed from inspected upstream content, NOT independently byte-identical to upstream Git blob.
- Standard Python, warnings-as-errors: **26/26 PASS**.
- Optimized -OO Python, warnings-as-errors: **26/26 PASS**.
- Total: **52 passing focused executions**, 26 unique methods. Source compileall PASS.
- Prior exact helper with new tests failed **9/12**, as expected.
- Tests ran in isolated exact-helper working tree, NOT a complete exact-HEAD checkout. Real Ed25519 registry lifecycle, 22 genuine AES-GCM tests and complete six-app suite are unexecuted.

## CI and release gate

Four R380 test invocations added to .github/workflows/desktop-build.yml: Ubuntu and Windows × standard/optimized, before packaging; workflow approximately 221,773 UTF-8 bytes, below reviewed 224 KiB threshold. Hosted CI status requires separate confirmation. Previous R379 Actions run #43233828465 failed before any recorded steps on both jobs; source of infrastructure failure unconfirmed.

Next: inspect Actions check annotations, spending/billing caps and runner eligibility; restore runners and run full exact-head six-app plus Ed25519/AES-GCM suites. Then validate real Windows x64 builds, Defender, accessibility and genuinely gated premium distribution.

**HOLD:** no merge, executable publication, unrestricted premium access, WordPress production edit or bypass of QD and founder sign-off.
