# Labs R310 — Premium restore filesystem error privacy (DRAFT / QD HARD HOLD)

**Scope:** both premium products — GrantAudit Studio Pro and ProcureGuard Studio Pro — share `fvs_suite/evidence_vault.py`. All four free apps, cryptographic format, reports, budget calculations, human review decisions, site/CMS and production are untouched.

## Observed defect and intervention

The R309 restoration loop used `restored.mkdir(...)` and `file.open("xb")` / `stream.write` / `os.fsync` directly. Common OS failures such as an occupied filename, access denial, or disk I/O errors could escape as `OSError` with the customer's local path embedded in `filename`, `str(error)` or traceback. The outer exception handler rolled back file contents but re-raised the original exception, retaining that identifying path. This is a private-local diagnostic exposure, **not** evidence of cloud exfiltration.

R310 adds `fvs_suite/vault_restore_writer.py` and routes the premium `restore_evidence` writing path through it:
- Exclusive 0700 directory creation and snapshot of its filesystem identity; permission/existence/identity OS errors become **fixed, path-free ValueErrors** after leaving the source exception handler.
- Per-member exclusive `xb` creation, descriptor identity snapshot **before** any decrypted byte, and byte write, flush, and fsync.
- All ordinary write/open/fsync `OSError` failures become fixed path-free diagnostics with no implicit `__context__` / `__cause__`.
- After a member is created, its descriptor identity remains in R309's rollback ledger, so failures and interrupts can remove only files still owned by this restore.
- Non-`OSError` failures and `KeyboardInterrupt` still propagate for caller rollback (no invented success or compliance approval).

## Reproducible evidence

Focused test file: `products/desktop/tests/test_vault_restore_writer_r310.py` (13 unittest cases: successful actual descriptor-custody writes, 0700 directory, occupied name, directory/symlink refusal, injected permission and fsync errors, exception-chain privacy, unlink-only-owned rollback, interruption handling, and identity failure).

Executed locally on Linux CPython **3.13** with synthetic input and actual temporary files:
- `cd products/desktop && python -m unittest discover -s tests -p 'test_vault_restore_writer_r310.py' -v`: **13/13 PASS**
- `cd products/desktop && python -O -m unittest discover -s tests -p 'test_vault_restore_writer_r310.py' -q`: **13/13 PASS**
- `python -m py_compile fvs_suite/vault_restore_writer.py tests/test_vault_restore_writer_r310.py`: PASS.
- The new helper and 13-test module Git blob IDs were matched against the locally tested files: `e3a848bcc9fd4c074b2700043b6e872b27cf4591` and `b78afd99c1af0070540334432ca866efad4b8cb2`.

The full-checkout `test_vault_restore_writer_integration_r310.py` supplies **four** integration methods, covering genuine AES-GCM archives for both premium products, synthetic fsync/path leakage and rollback, directory creation privacy, and postwrite digest mismatch cleanup. **These four are committed but have not been executed**, because native full-repository CI / dependency-backed checkout is currently blocked. Do not count these as passing tests.

## Boundaries, outstanding checks, and release hold

This change protects **expected directory and member filesystem OSError diagnostics**, not every possible exception from third-party CSV/JSON validation, nor all attacker-controlled directory races. If a new directory is created but its OS identity cannot be obtained, the helper fails closed before writing financial bytes and can leave an **empty** private directory rather than delete a possibly unowned path. On Windows, filesystem 0700 semantics differ; require actual Windows 11 x64 NTFS acceptance.

Existing draft chain remains unmerged. GitHub Actions jobs on R309 run `42661030119` failed with zero steps; underlying service, runner or billing cause remains unconfirmed. Do not claim a native Windows executable, Defender scan, artifact attestations, premium gated delivery, or release readiness.

**Next gate:** restore GitHub Actions runner availability and run the complete suite, including R301–R310 integration and focused tests, on real Ubuntu and Windows jobs. Then perform controlled Windows 11 x64 six-app build/smoke/accessibility/Defender/SHA-256 and QD review. No PR merge, CMS publish, source data upload, premium file distribution, or release without independent QD and founder approval.
