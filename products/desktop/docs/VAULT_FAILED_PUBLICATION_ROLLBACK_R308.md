# R308 — Preserve unrelated final names during failed premium vault publication

**Issue:** #73. **Scope:** Shared `fvs_suite.vault_publish` used by **GrantAudit Studio Pro** and **ProcureGuard Studio Pro** only. Draft feature branch stacked on R307; **do not merge or release** without independent QD and founder authorization. No live site, binaries, payment state, license state, source customer records or free-app engines modified.

## Reproduced R307 defects

The R307 publisher called `published = os.lstat(target)` just after the exclusive `os.link`/Windows `os.rename` step, then used that *first observed target identity* as the rollback authority. If a different writer replaced the newly published name **before that first lstat**, verification rejected the substitution as intended, but rollback deleted the different writer's file or symlink. It also placed the first post-link `lstat` outside its cleanup handler, so an exception/interrupt there could leave the vault's published name despite reporting failure.

These are provenance and cleanup failures in a shared premium encrypted-archive publisher, **not breaks of AES-GCM or financial arithmetic**.

## R308 change and tradeoff

- The first post-link `lstat` and final-byte verification now share a `BaseException` rollback guard. An owned file left by a post-link stat failure or interrupt is removed on a best-effort basis.
- After a failed verification, rollback first compares the observed destination identity to the **owned staged descriptor's device/inode and regular-file type**. An owned target can be removed if still owned.
- If the first observed target is *not owned*, rollback inspects the source stage via `lstat`. Only when the stage still identifies exactly that same observed object (including symlink file type) does it remove the unverified final link made to a pre-link substituted stage. If the original stage remains intact and the target identifies a foreign object, the target is preserved rather than deleting a different writer's file.
- Public API, on-disk vault format, AES-256-GCM, strict no-clobber, 120 MiB byte cap, deterministic evidence, no telemetry, offline privacy and human approval remain unchanged.

**Security boundary:** This is a safer *best-effort pathname rollback policy*, not atomic proof of who created the file under arbitrary concurrent directory mutations. A hostile directory owner can still race the final stage/target lookups or alter paths after verification. Preserving a foreign final file may leave a non-vault object at the requested name on failure; the operation returns an error rather than claiming success. Handle-based native Windows/NTFS verification is still required before any release security claim.

## Executed local evidence (synthetic Linux only)

Environment: Linux CPython **3.13.5**; temporary-directory synthetic ciphertext; all source data remained local. Exact committed Git blob IDs match locally executed source and tests.

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover \
  -s products/desktop/tests -p 'test_vault_rollback_custody_r308.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover \
  -s products/desktop/tests -p 'test_vault_rollback_custody_r308.py'
python -m py_compile products/desktop/fvs_suite/vault_publish.py \
  products/desktop/tests/test_vault_rollback_custody_r308.py
```

Results: **16/16 PASS** normal, **16/16 PASS** optimized = **32 passing focused method executions**, and compilation passed. Tests cover good multi-block and empty payloads, equal-length/different-inode/symlink post-link replacement preservation, errors and interrupts in the *first* post-link metadata check, stage-swap cleanup of links created to the substituted stage, failure/success no-clobber, redacted error context, original-source preservation, and cleanup after failed final verification.

**Predecessor negative control:** The **exact R307 source blob `74b6f87eea7ce97149e2ad70e9a942952b938acc`** was reconstructed byte-for-byte locally, and the same 16-test module produced **3 failed assertions + 3 errors** as expected (16 executed): R307 erased unrelated post-link final names and missed cleanup when first post-link `lstat` failed. The negative control is *not* a test passing on R307.

Verified blobs: implementation `371471d42421a009499ae55c837ffc4e0616df1c`; new test module `1d2da490f2302c390c7469a9e47d9bf10039e070`.

## Independent review and release blockers

- Hosted GitHub Actions Ubuntu/Windows tests currently fail **before runner execution steps**, root cause not established. Owner to inspect Actions billing/spend/policy/runner availability, then rerun unchanged commit.
- **Not verified:** inherited six-app regression and integration tests, Windows 11 x64/NTFS acceptance, executable build/install/Defender scan, keyboard/screen-reader accessibility, signed/unsigned provenance receipts, SHA-256 release manifests, and gated premium distribution.
- This branch must remain **DRAFT / HARD HOLD** pending independent QD and founder approval. Do not merge, upload public binaries, publish premium artifacts to unrestricted URLs, or change WordPress production.

**Next highest-impact action:** restore working CI for full Linux+Windows desktop tests, run these R308 cases on real NTFS, then complete six distinct private Windows x64 executable acceptance gates and independently reviewed release/protected-premium distribution.
