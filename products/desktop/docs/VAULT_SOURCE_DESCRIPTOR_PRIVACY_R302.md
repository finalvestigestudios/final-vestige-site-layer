# R302 — Premium evidence-vault local source custody

**Issue #73 | draft, stacked on R301 | QD and founder HARD HOLD.** No edits to `main`, production pages, downloads or premium access controls.

## Reproducible pre-R302 defect

`evidence_vault._read_regular` used `Path.is_symlink()/is_file()/stat()` followed by `Path.open()` and an unbounded-in-time file read. A source file could be replaced between pathname checks and opening, and IO exceptions exposed the absolute client filename in the exception itself. Because the exception was not sanitized, UI/debug tooling could retain sensitive local path details. This helper is called for reports and journals during premium sealing and for encrypted archives during restoration.

## Implemented

- `fvs_suite/vault_input_snapshot.py`: verify `lstat` regular-file metadata; use `os.open` with `O_NOFOLLOW` where available and `O_NONBLOCK`, `O_BINARY` where appropriate; verify opened descriptor identity, size and timestamps before/after bounded reads; verify final pathname identity; reject growth, mutation, path replacement, oversized content, links and non-files. The source is never modified.
- Convert expected OS errors during path inspection, open, fstat, read and close to fixed-label messages after the original handler has exited. No original error chain (`__cause__` / `__context__`) or confidential pathname remains on those paths. Never swallow `KeyboardInterrupt`/`SystemExit`.
- `evidence_vault._read_regular` delegates to the shared source snapshot, retaining existing `Report`, `Journal`, and `Encrypted archive` size contracts and vault authentication, Scrypt, SHA-256, AES-GCM, human review and local-only design.

**Threat-model boundaries:** On some Windows filesystems, pathname and descriptor `st_ctime` differ; comparison excludes that field *across those two views* while still comparing each view's full signature before/after. These checks detect ordinary swaps and mutations but are not an operating-system lock, remote filesystem consistency guarantee or defense against hostile kernel/filesystem metadata forgery. Vault write destination exceptions, simultaneous external edits after snapshot return, and OS-specific native Windows acceptance remain separate review items.

## Reproducible checks

From `products/desktop` (complete checkout):

```sh
python -W error -m unittest discover -s tests -p 'test_vault_input_snapshot_r302.py'
python -OO -W error -m unittest discover -s tests -p 'test_vault_input_snapshot_r302.py'
python -W error -m unittest discover -s tests -p 'test_vault_source_integration_r302.py'
python -OO -W error -m unittest discover -s tests -p 'test_vault_source_integration_r302.py'
python -W error -m unittest discover -s tests -p 'test_evidence_vault_r8.py'
python -W error -m unittest discover -s tests -p 'test_vault_restore_privacy_integration_r301.py'
```

Run these plus the full Python suite on actual Windows x64 and Ubuntu CI. Failures must block merge. No test output, SHA-256 receipts, Defender attestation or release links are evidence until truly produced and independently reviewed.

## Release gates

QD and founder must review before merge. CI and native Windows smoke, six application launches, source preservation, accessibility, signed or clearly unsigned packaging, scan artifacts, hashes, and payment-gated premium downloads are **pending**. No binary or site change is authorized by this sprint.
