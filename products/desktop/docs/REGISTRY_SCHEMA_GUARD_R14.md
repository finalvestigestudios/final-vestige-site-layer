# R14 — fail-closed operator registry schema validation (PRE-RELEASE)

## Problem

The R13 offline license issuer depends on SQLite's `issuance.license_id`
primary key and state/product CHECK constraints. Before R14,
`CREATE TABLE IF NOT EXISTS issuance` silently accepted an existing database
whose `issuance` table was redefined without the unique primary key.
A trigger could also rewrite/delete newly reserved or finalized rows, or an
unrelated view could expose registry fields. A compromised or incorrectly
migrated registry must **never silently permit another license to be issued**.

## Change

- New `registry_schema_guard.py` pins the **exact R13 SQLite table DDL**,
  checks the single primary-key index, rejects any additional user-defined
  tables, views, triggers or indexes, and executes `PRAGMA integrity_check(1)`.
- `IssuanceRegistry.reserve` and `IssuanceRegistry.finalize` both validate
  the live schema **after `BEGIN IMMEDIATE` and before a data write**. This
  blocks concurrent legitimate SQLite schema changes between inspection and
  transaction under SQLite's normal writer-lock semantics.
- Existing valid R13 registry files are accepted without a migration or
  changes to reservations, amounts, private keys, entitlements, or customer
  files. Unsafe schema changes fail closed with `RegistryError`, preserving
  existing reservations/issued states rather than attempting auto-repair.
- This validation is operator-only. No runtime dependencies or telemetry are
  added to the four free customer applications or the two premium GUIs.

## Reproduction and tests

From the repository root, with Python 3.13 and the desktop imports available:

```sh
PYTHONPATH=products/desktop python -m unittest discover \
    -s products/desktop/tests -p test_registry_schema_guard_r14.py -v
PYTHONPATH=products/desktop python -OO -m unittest discover \
    -s products/desktop/tests -p test_registry_schema_guard_r14.py -v
```

**Local development evidence (Linux, synthetic SQLite):** 17/17 new
tests passed normally and 17/17 passed under `-OO`. This included four
integration calls into the R13 registry source; its original source was
reconstructed exactly and independently checked against Git blob
`d8ee248a0891032107c2d57e322c18f7b2a1d6f4`. The three exact
committed R14 source blobs must match the locally tested bytes before
counting this result as branch-specific evidence.

Cases: existing R13 schema succeeds; reservation and finalization succeed;
an issuance table without `PRIMARY KEY` is refused before insert;
deleted product/state CHECK constraints are refused; added columns,
views, tables, triggers and indexes are refused; schema changes introduced
after a reservation block finalization; SQLite internal primary-key index
is allowed. The full repository suite and actual Windows x64 EXEs remain
**unverified** while GitHub-hosted runner startup is blocked.

## Operator action on rejection

Stop. Do **not** delete, recreate, rewrite, or bypass the registry. Preserve
a secure copy and its SHA-256, collect operator evidence, inspect
`sqlite_schema` independently on an approved machine, compare against
this exact revision, and obtain a separately reviewed data recovery plan.
A later intentional schema change must be designed as a reviewed migration,
with regression tests and reconciliation of all issued IDs. Do not run
arbitrary SQL from suspicious registry files in privileged environments.

## Limitations / release status

This is **schema drift detection, not authentication**. An operator or local
administrator can still change row values, swap a complete valid SQLite file,
replace a trusted filesystem path during a race, replay an older backup, or
issue licenses using an alternate registry. The Windows NTFS ACL posture has
not been verified. `PRAGMA integrity_check` does not authenticate history,
and exact DDL matching can reject legitimate future schema formats until a
reviewed migration exists.

No real signing authority, premium download access, code-signed executable,
customer payment, Windows smoke-test pass, production/QD approval or release
is created by R14. Keep draft PRs unmerged and releases disabled.
