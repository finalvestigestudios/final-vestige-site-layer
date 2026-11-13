# R390 — Windows release-candidate reparse-point custody

**Scope:** Six-app internal Windows x64 candidate verification. DRAFT stacked on R389; independent QD and founder release hold remains. No binaries are published.

## Defect and fix

The prior candidate reader rejected non-regular files, hardlinks, symlinks, oversize payloads and changed SHA-256 inventories but did not inspect the Windows FILE_ATTRIBUTE_REPARSE_POINT flag. A non-symlink reparse-point file or junction could masquerade as an ordinary source or staging directory and redirect an inspection. This is a potential file-identity gap, not an observed exploit.

R390 introduces a small Windows-attribute predicate and integrates it into the shared candidate reader. On Windows it rejects reparse or missing/invalid attributes at five custody boundaries: directory lstat, candidate path lstat, opened descriptor fstat, post-read descriptor fstat and post-read path lstat. Valid native files retain existing SHA-256, inode/timestamp, hardlink, size, fixed-membership and no-overwrite protections. POSIX behavior remains unchanged. Errors are generic and do not include private paths.

Python 3.13 documents st_file_attributes on Windows os.stat_result, including fstat and lstat. This conservative guard may reject unusual Windows filesystem views; native testing is required.

## Measured local evidence

On Linux Python 3.13.5, 28 new unittest methods passed in ordinary and optimized (-OO) execution: **56/56 focused executions PASS**. Tests cover reparse flags and combinations, malformed/missing attributes, adversarial attribute access, actual regular-file SHA-256 and path/descriptor/root rejection using synthetic Windows attributes. Source compilation passed. The local baseline candidate_guard.py matched repository Git blob a7d8fe2c37282fd3b88c8ff0b9443ee473255ed5 before edits; each of the three committed Python files matches the file actually tested.

The independent Ubuntu/Windows source workflow now runs these 28 tests under both Python modes. This workflow is **not** a native EXE release gate. The exact R389 predecessor source and build workflows failed before runner execution, and R390 hosted status remains separately verifiable.

## Mandatory remaining acceptance

- Real native Windows x64 attributes and actual junction / file reparse fixtures, plus full six-app integration.
- Native PE smoke, genuine Defender/EDR, accessibility observations, signed/unsigned distribution policy, and SHA-256 checksums.
- Genuine AES-GCM, Ed25519, SQLite, Decimal/provenance regression suite.
- Verified authenticated premium access controls for GrantAudit Studio Pro and ProcureGuard Studio Pro.
- Independent QD and founder approval; no production push, executable publication, or premium URL exposure.

**Next priority:** Diagnose GitHub Actions pre-run failure annotations and hosted-runner eligibility, rerun exact R390 SHA, then execute the native Windows acceptance gate.
