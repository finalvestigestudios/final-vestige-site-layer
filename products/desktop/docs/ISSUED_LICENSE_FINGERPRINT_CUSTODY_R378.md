# R378 — issued premium entitlement fingerprint custody (DRAFT / release HOLD)

**Scope:** Issue #73, GrantAudit Studio Pro and ProcureGuard Studio Pro **operator-side offline license issuance**, stacked on R377. No production, download, entitlement-policy or site changes.

## Reproduced pre-fix defect

The R377 `license_registry.IssuanceRegistry.finalize` opened a pathname, then handed the raw descriptor to `os.fdopen`. When `fdopen` failed, the raw descriptor was never closed. Its `raise RegistryError(...) from exc` also retained a private operator pathname in `__cause__`. Locally reproduced on Linux Python 3.13.5 with a synthetic entitlement file and a permission-error canary: **cause retained the canary** and `os.fstat(fd)` proved the raw descriptor **remained open** until the test closed it.

The old fingerprint reader also accepted ordinary hardlinks and did not verify source identity after hashing. These are distinct from signature validity; the digest is still compared with the signed payload previously generated in memory.

## Working correction

- New `products/desktop/issued_entitlement_guard.py`: open **read-only** with `O_NOFOLLOW` and `O_NONBLOCK` where available; descriptor `fstat` rejects special files and multiply linked files before reading. No `fdopen` handoff.
- Bounded `os.read` loop (at most **8,193** total bytes); reject empty, excessive, incomplete and changed file evidence. Compare descriptor device/inode/type/link count/size/mtime/ctime before and after reading. SHA-256 results are deterministic; original bytes are never altered.
- Always close the owned descriptor; a close failure refuses finalization. Public `RegistryError` is raised **outside** the private `OSError` catch and without a retained `__cause__`/`__context__`.
- `license_registry.finalize` now delegates to this helper before comparing `hmac.compare_digest` against the *in-memory signed-payload* SHA-256. Its existing protected SQLite transaction, reservation uniqueness, product/key binding, human issuance confirmation, and no-retry semantics are unchanged.
- Four additional CI invocations: Ubuntu/Windows × normal/optimized `-OO`, before any Windows candidate packaging.

## Executed local focused evidence (Linux Python 3.13.5)

- Reproduced original `fdopen` failure defect with the R377 finalization read stanza: leaked descriptor **TRUE**, leaked exception cause **TRUE** (synthetic canary; descriptor explicitly closed after test).
- Exact source-controlled `issued_entitlement_guard.py` and `test_issued_entitlement_guard_r378.py` Git blob hashes were matched against locally executed bytes.
- `python -W error -m unittest discover -p test_issued_entitlement_guard_r378.py`: **18/18 PASS**.
- `python -OO -W error -m unittest discover -p test_issued_entitlement_guard_r378.py`: **18/18 PASS**.
- `compileall`: **PASS**. Total: **36 passing focused test executions**, not 36 unique tests.
- Covered exact digest and byte preservation, 8,192-byte boundary, empty/8,193-byte rejection, symlink/hardlink/directory/FIFO controls, open/path/fstat/read/close fault redaction, raw-descriptor cleanup, partial/truncated reads, metadata mutation, and immutable read-only flags.

**Limit of evidence:** Focused helper/test source on Linux; no complete exact-head checkout, inherited `test_license_registry_r13.py`, genuine Ed25519 issuer-to-registry integration, 22 AES-GCM tests, or native Windows 11 x64 binary was executed in this local run. Linux can simulate but not prove Windows junctions, ACLs or reparse-point defense. A privileged/same-user pathname-swap outside the open descriptor remains a boundary risk. No claim of an independently security-audited or release-ready entitlement flow.

## Acceptance / block

Restore hosted Actions runner execution and run exact-head full six-app suites, including R13 license/real Ed25519 CLI integration, genuine AES-GCM cases and R378 Windows tests. Then build and smoke six real Windows x64 EXEs, run Defender scanning, GUI accessibility review and gated premium entitlement checks. No binaries or unrestricted premium links may be published until independent QD review and founder approval.

If Actions jobs still fail before step 1, the **smallest unblock** is for the repository owner to inspect failed-check annotations, GitHub Actions billing/spending limits and hosted-runner eligibility, then rerun the precise draft-PR head. Failure before any recorded steps is not a passing or failing application test.
