# Labs R311 — premium plaintext restore byte custody (DRAFT / QD HOLD)

## Scope and observed gap

Both **GrantAudit Studio Pro** and **ProcureGuard Studio Pro** call `fvs_suite.evidence_vault.restore_evidence`. At R310 the restore authenticated ciphertext, wrote three or two local files, then reparsed the report/journal. The exported `sealed-evidence-manifest.json` was **never reread or byte-compared after writing**. Same-size postwrite changes or an unexpected added file could therefore survive to a successful restored folder, even if the report digest and review-event count still matched. This is a local bundle-integrity hazard, **not proof of customer exposure or remote compromise**.

## Implemented

- `fvs_suite/vault_restore_verify.py`: independent exact-byte postcondition over **each** exclusively created restored member, with bounded 256 KiB streaming, short-read handling, regular-file/no-symlink descriptor checks, original descriptor inode/device identity, file size and stable metadata rechecks, and stable restore-directory identity.
- Exact set enforcement: reject absent, unexpected, duplicated, reordered, replaced, symlinked or corrupted plaintext members, including the manifest. Preserve unrelated added files; R309 rollback only unlinks identifiable files owned by the restore.
- Expected `OSError`/file-path diagnostics are converted to fixed-path-free `ValueError` **outside** the original handler, avoiding implicit chained exceptions. `KeyboardInterrupt` still propagates to caller rollback.
- `evidence_vault.restore_evidence` calls the verifier once **before parser validation** and again **after report/journal validation**, so neither postwrite nor parser-side mutation can be silently reported as success.
- Desktop CI's existing Linux and Windows jobs explicitly run R311 normal and `-OO` tests, as well as **R310's previously unexecuted genuine AES-GCM integration tests**, before downstream source-gate/packaging. No third-party action or token permission added.

## Reproducible local proof (2026-11-09)

Tested new helper and test file in a standalone Python package layout with real Linux temporary files, synthetic report/journal/manifest bytes, simulated replacement files/symlinks/directory swaps, injected I/O faults, and `unittest.mock`; **not a complete repository checkout**:

```sh
cd products/desktop
python -W error -m unittest discover -s tests -p 'test_vault_restore_verify_r311.py' -q
python -OO -W error -m unittest discover -s tests -p 'test_vault_restore_verify_r311.py' -q
python -m py_compile fvs_suite/vault_restore_verify.py tests/test_vault_restore_verify_r311.py
```

- **29/29 PASS** normal, **29/29 PASS** `-OO`, total **58** focused method executions; `py_compile` PASS. Includes payload corruption, same-length manifest change, path and inode replacement, arbitrary extra files, short reads, and path-private failures.
- Executed *local source* was matched to committed GitHub Git blob `c516a3cfe400d3409c9205813e70e36cf62acbd1`; executed *local test file* matches GitHub Git blob `dffd7a24969371a512905c16efafdbab0944ab58`.
- Confirmed two call-site insertions in the committed `evidence_vault.py`: once before `read_cases`, once after `read_journal`.
- Cannot claim complete-checkout crypto integration or actual Windows x64 behavior: the hosted Actions jobs have repeatedly failed before starting steps.

## Limits and release hold

Verification is a finite observation: **does not eliminate races** against a hostile same-user process changing the directory immediately after return. Windows NTFS filesystem IDs, symlink behavior, GUI, Defender and unsigned executable acceptance require genuine Windows 11 x64 evidence. The two full-system restore pathways are wired but not executed locally; the R310 integration suites remain pending runner execution. Source archive is never overwritten. No remote sync, telemetry, new monetary arithmetic or automatic compliance approval.

R311 is a new **stacked draft feature branch based on R310**, not `main`. No Windows EXE, WordPress edit, downloads, premium distribution, price/license activation, merge or production publication. Keep independent QD and founder approval gates intact.

**Highest-impact unblock:** GitHub owner inspects Actions billing/spend limits, workflow enablement, permissions and hosted runner scheduling; rerun this exact draft head and require both Linux + Windows gates green, then privately build/smoke/scan all six real x64 binaries, checksum them and review licensing/accessibility before any release.
