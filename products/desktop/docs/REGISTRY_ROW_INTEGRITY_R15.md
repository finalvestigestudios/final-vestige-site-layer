# R15 — Operator issuance row integrity (PRE-RELEASE)

The R14 guard verifies the **structure** of the local premium license registry. R15 checks the **existing rows** under the same `BEGIN IMMEDIATE` write lock, before a new ID can be reserved or a license marked issued. The R13 SQLite schema is unchanged; existing valid registries need no migration.

## Refusal conditions

- Invalid license/key identifiers, product codes, or noncanonical output-path SHA-256 values.
- Multiple license IDs reserving the same hashed destination path, including across GrantAudit Studio Pro and ProcureGuard Studio Pro.
- Reserved rows with an issuance timestamp or license digest; issued rows without a lowercase SHA-256 digest, valid canonical UTC timestamps, or chronological `reserved_at <= issued_at`.
- Attempts to reserve a destination hash that already exists, even if the old attempt was interrupted and left its ID reserved.
- A backwards system clock during finalization: the update must satisfy `reserved_at <= finalized_at`, otherwise the record stays reserved.

Data validation happens **in addition to**, not instead of, R14's schema integrity check. Anomalous or ambiguous records stop issuance with generic operator-facing errors. Do not silently edit, delete, or reset the ledger. Back up the exact suspect file, review licensing events and original signed output, and obtain a separate operator/security disposition before attempting recovery.

## Limitations and release status

These are **structural and semantic checks, not authenticated audit evidence**. An operator with database write access could fabricate a plausible row, roll back a registry backup, use another registry database, alter the system clock, or patch the Python executable. Destination SHA-256 equality is a preventive local check, not proof of physical path identity on every filesystem. Protect the single canonical registry, its backups, private key custody and issuance process independently; add tamper-evident externally anchored audit evidence before commercial launch. No signing keys are bundled, and the two premium GUIs remain locked without approved production public keys.

This sprint does not make any of the six Windows x64 binaries release-ready. The actual Windows EXEs, full repository test suite, AV/signing, premium fulfillment, and QD release approval remain outstanding.

## Focused tests

From repository root:

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_registry_row_guard_r15.py -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p test_registry_row_guard_r15.py -v
```

Locally verified: **17/17** both normal and `-OO` on a reconstructed R14 registry integration harness using identical new R15 module/test bytes. The remote full-repository checkout and actual Windows CI remain unverified; do not call this a clean Windows build.
