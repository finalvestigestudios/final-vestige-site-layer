# R30 — verified financial CSV source snapshots (development only)

**Issue #73.** All six Windows x64 executables remain unreleased. This change is not an accounting certification, compliance decision, payment approval, or an authorization to publish any downloads.

## Defect addressed

The existing five financial CSV engines parsed directly from a mutable file stream. Initial and final file-size checks did not identify a same-size local modification or pathname substitution during parsing. The GrantAudit entry point then **reopened the claim CSV header**, so linked/credit-mode selection could depend on different bytes from the already validated claim records.

This is especially dangerous for audit provenance: the displayed source row could come from one file version while the selected reconciliation mode came from a later version.

## Implementation

- `fvs_suite.csv_snapshot.read_csv_snapshot` uses `lstat` to reject symlinks and nonregular files; opens a single binary descriptor, validates descriptor identity against the original pathname, and reads in bounded chunks to a maximum of `MAX_IMPORT_BYTES` (**64 MiB** by default). It checks bytes read, length, file identity, size and modification/change timestamps before returning, then checks the pathname again. Common growth, replacement and concurrent edits fail closed.
- The actual `engine.table` parser consumes **only a verified in-memory byte snapshot** using `BytesIO` / `TextIOWrapper` with the original `utf-8-sig`, `csv.reader(strict=True)`, physical row-line provenance and NUL/header validations. User-selected originals are never modified. Existing return type remains a list unless `include_headers=True`.
- `engine.grant_audit` requests `include_headers=True` and derives linked-claim mode from the exact same validated header that produced the claim rows; it no longer reopens the claim file. Linked/legacy paths and their review-only semantics remain intact.
- All five financial applications using `engine.table` benefit. Policy Delta Desk retains its separate bounded text parser (R26).

## Scope and verification

The helper regression suite exercises exact byte preservation/BOM, boundaries, oversized sparse files, symlinks, missing and nonregular files, filename/path replacement, mutation during reading, sanitized errors, and no mutation of source inputs. Integration contracts verify engine row provenance, no second claim-header read, both grant modes, and fail-closed export behavior.

The isolated tests use the **actual helper code** with temporary on-disk files. Full checkout integration and native Windows filesystem semantics are **not** established by isolated tests; review CI and issue #73 for actual execution evidence.

## Explicit limits

A snapshot is held in RAM (up to 64 MiB plus parser allocations) and only freezes bytes **during that parse**. It is not an OS filesystem lock, immutable volume snapshot, historical attestation, malicious-adversary protection or cryptographic proof against a later source change. R29's later evidence inventory still hashes the current pathname, which can be changed **after** import. Cross-stage source-hash binding and multi-file all-or-nothing premium packages remain next engineering risks. Users must independently verify the report, local source file custody and accounting decisions.

No telemetry, network transfer, cloud storage, license-key activation, premium access change or WordPress/QD production bypass was introduced.
