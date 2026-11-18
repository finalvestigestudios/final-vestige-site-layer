# R515 — Immutable source files across sequential test launches (DRAFT/HOLD)

Scope: Issue #73, six Windows x64 Final Vestige Labs utilities; four free (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk), two premium (GrantAudit Studio Pro, ProcureGuard Studio Pro). This is a **read-only test-evidence integrity improvement**, not a Windows release or app availability claim.

## Failure mode closed

The R509 source runner validates the immutable, SHA-pinned list of 416 shell-free Python commands and checks all referenced files once. But those commands are run **sequentially**. A previous test or local process could replace the regular Python test file referenced by a later command after the initial manifest preflight. Existing symlink checks therefore did not establish continuity of executable source bytes between the start of a 416-command run and each launch.

R515 records SHA-256 **content digests for each distinct referenced source test or smoke script before any subprocess begins**, with a 1-MiB per-source cap and rejects missing files, symlink/junction ancestry, malformed path components and oversized source before executing test processes. Immediately before every launch, it reopens and recomputes the source digest. If any file changed, the runner stops before launching that test, logs only the command index and fixed rejection text, and **never outputs source bytes, private paths or child stdout/stderr**. Both standard and optimized executions of the same test receive the same baseline digest.

This is a fail-closed **prelaunch consistency check**; it is not a cryptographic source signature, an atomic inode pin on every operating system, an OS security sandbox, a replacement for running the tests, or approval for premium distribution.

## Files and preserved contracts

- `products/desktop/scripts/source_path_snapshot_r515.py`: source bytes to digest-only snapshot with 1-MiB cap; link/junction and path-component rejection; fixed sanitized errors
- `products/desktop/scripts/source_evidence_runner_r509.py`: full-matrix baseline capture plus source recheck immediately before each subprocess; `main()` forces `verify_source_snapshots=True`; isolated existing `execute()` fixtures preserve their explicitly disabled prelaunch option
- `products/desktop/tests/test_source_evidence_runner_r509.py`: 13 new R515 methods, including late modification of the second of two synthetically tested sources, missing/linked source, exact launch gating, and mandatory main entrypoint enforcement
- This runbook: `products/desktop/docs/SOURCE_PRELAUNCH_SNAPSHOTS_R515.md`

The 416-line pinned command manifest is **unchanged**; the R385 independent Linux/Windows workflow, R507 identity checks and internal Windows build workflow are **unchanged**. No global timeout, permissions, action pins, premium entitlement enforcement, catalog, executable, source CSV or money logic is modified.

## Reproducible execution evidence

Before committing, an exact-Git-blob-matching local copy of the **new helper** was exercised using 10 isolated Python unittest methods with fake source files in temporary directories:

- Standard Python: **10/10 PASS**
- Python `-OO`: **10/10 PASS**
- Total: **20/20 focused executions PASS**

These validate normal, missing, mutated, linked, oversized and malformed source; sanitizer behavior; malformed digests; and absence of source changes. They **do not** represent a run of the entire committed runner or committed R515 test class. Those 13 methods were added to the already-included test file in the immutable matrix and **await exact-commit CI execution**. No native Windows executables were built or scanned locally.

The source fingerprint is SHA-256 of each local source file, *not* a signer attestation. It carries no customer data into CI logs.

## Release and QD gates

GitHub Actions previously failed all six Linux/Windows jobs before any execution (e.g. [R514 independent source #44241636211](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44241636211)); the root infrastructure cause is not established. Verify exact R515 head CI after draft PR creation. A repository/account administrator should inspect billing limits, private-repository runner eligibility and workflow policy, then rerun at the exact head commit. If that is unavailable, execute the R515 R509 test module in normal and `-OO` modes from a trusted full checkout and attach command receipts.

**Next highest-impact step:** run all 416 source commands on both Ubuntu and Windows, and six distinct native Windows x64 executable builds plus Defender, checksums, signed/unsigned provenance, keyboard accessibility, offline operation and premium entitlement/controlled-download verification. Only after independently reviewed QD approval and explicit founder authorization may product or site publishing proceed.

**HARD HOLD:** No merges into `main`, WordPress writes, site download URLs, public EXEs, or unrestricted premium assets. Local-first financial privacy, Decimal-safe calculations, deterministic evidence and human compliance decisions are unchanged.
