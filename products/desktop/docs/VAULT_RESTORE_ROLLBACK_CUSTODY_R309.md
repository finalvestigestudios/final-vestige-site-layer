# Labs R309 — Identity-bound rollback of decrypted premium evidence (DRAFT / QD HARD HOLD)

**Scope:** GrantAudit Studio Pro and ProcureGuard Studio Pro share `fvs_suite/evidence_vault.py`. No other app engine, premium licensing, site content, production branch, AES-GCM archive format, Decimal arithmetic, deterministic audit fields, or review decisions are changed.

## Defect / fix

Prior to R309, `restore_evidence()` used a bare list of created plaintext paths and, on any ordinary exception, called `file.unlink(missing_ok=True)` on every path. When another local process replaced one with an unrelated file or symlink before rollback, restore cleanup could **delete that unrelated pathname**. It also skipped cleanup after `KeyboardInterrupt`, leaving our newly created plaintext files in the 0700 restore folder.

R309 captures file identity via `os.fstat()` **immediately after each exclusive `xb` create and before writing decrypted bytes**. The unique private restore directory is also captured via `lstat()`. On failure *or interruption*, rollback checks current directory identity and the regular-file device/inode of each created output; it unlinks only detectably owned names and removes the directory **only if empty and still owned**. Files with missing/zero identity fail closed; unrelated replacements and symlinks remain untouched. Expected cleanup I/O errors never mask the original restore failure.

**Threat boundary:** This remains best-effort, path-based rollback; it is not a security claim against a malicious actor continuously racing the final `lstat` and `unlink`. On filesystems without stable nonzero file IDs cleanup may preserve a private folder, which must be handled by an operator. A privileged same-user/directory adversary is out of scope pending Windows NTFS reparse-point and ACL validation. No restored plaintext, passphrase, path, or source customer data is added to logs.

## Evidence actually executed (2026-11-09, isolated Linux CPython 3.13.5)

The **new helper and focused tests**, exactly matching committed Git blobs, were run with actual temporary directories and synthetic bytes:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_restore_rollback_r309.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_restore_rollback_r309.py'
python -m py_compile products/desktop/fvs_suite/vault_restore_cleanup.py products/desktop/tests/test_vault_restore_rollback_r309.py
```

- **19/19 PASS** under normal Python with warnings as errors, **19/19 PASS** optimized (38 passing focused executions). Both test runs performed on Linux; no Windows claims.
- Real-file regression cases cover three-owned-file rollback, unrelated regular and symlink replacements, equal-byte/different-inode collision, replaced or linked restore directory, missing files, actual same-inode edits, failed unlink/rmdir/stat, and invalid file/directory identities.
- Two stand-alone negative-control simulations of the exact predecessor unconditional `unlink` loop reproduced deletion of replaced regular and symlink names. These are simulations, not full pre-R309 end-to-end restore execution.
- Committed helper Git blob: `1053fcfac625e697639284ee86b807a4efed7c8d`.
- Committed regression Git blob: `77bc0bfc028dc06c69997824fedb4b63393a44c4`.
- Full inherited `evidence_vault` integration, Windows 11 x64 NTFS, hosted Ubuntu/Windows CI, encrypted end-to-end restore, Defender/EDR, and all executable packaging remain **UNVERIFIED**.

## Review / release gates

This PR is stacked on R308, not production. Preserve independent QD + founder approval. Do **not** merge, publish the site, expose either premium file, or claim executables are released based on synthetic Linux tests.

**Highest-impact next step:** Restore scheduled GitHub Actions runners (check billing/spend controls, workflow permissions, runner availability), run the complete Python and actual AES-GCM seal/restore integration suite on the exact branch head, then perform actual Windows 11 x64 NTFS restore interruption and rename/reparse/ACL acceptance. Afterwards complete six real EXE builds, smoke tests, SHA-256/Defender/accessibility evidence and gated premium distribution.
