"""Fail-closed SQLite schema guard for operator-side license issuance.

Only the exact R13 database schema is accepted. This prevents alternate tables,
removed uniqueness constraints, user-defined triggers/views and schema drift from
silently changing the issuance ledger's reservation semantics. This is *not*
authentication: an operator/admin with write access can still alter rows or
replace an otherwise valid database, so it is not a tamper-proof audit archive.
"""
from __future__ import annotations

import sqlite3

# sqlite_schema.sql drops "IF NOT EXISTS" from our CREATE TABLE statement.
# Preserve the exact R13 column order, constraints and whitespace so existing
# R13 SQLite files remain compatible without migration or rewriting.
EXPECTED_ISSUANCE_DDL = """CREATE TABLE issuance (
                license_id TEXT PRIMARY KEY,
                product TEXT NOT NULL CHECK(product IN ('grants','procurement')),
                kid TEXT NOT NULL,
                output_path_sha256 TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('reserved','issued')),
                license_sha256 TEXT,
                reserved_at TEXT NOT NULL,
                issued_at TEXT
            )"""


class RegistrySchemaError(ValueError):
    """Existing registry cannot be trusted for issuing a new license."""


def enforce_registry_schema(db: sqlite3.Connection) -> None:
    """Verify the live schema while the caller holds BEGIN IMMEDIATE.

    Must run *inside* the reservation/finalization write transaction; checking
    only at connection startup leaves a race with another SQLite writer.
    """
    io_fault = False
    try:
        # SQLite reserves names with a literal 'sqlite_' prefix. Use substr,
        # not LIKE 'sqlite_%', where '_' is a wildcard.
        objects = db.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_schema "
            "WHERE substr(name,1,7) <> 'sqlite_' ORDER BY name"
        ).fetchall()
        expected = [("table", "issuance", "issuance", EXPECTED_ISSUANCE_DDL)]
        if objects != expected:
            raise RegistrySchemaError(
                "Unexpected issuance registry schema or extra SQL objects; manual review required"
            )
        # Confirm SQLite still exposes exactly the primary-key unique index.
        # Different explicit indexes/triggers must not silently alter behavior.
        indexes = db.execute("PRAGMA index_list('issuance')").fetchall()
        if len(indexes) != 1 or indexes[0][2:] != (1, "pk", 0):
            raise RegistrySchemaError("Registry primary-key index mismatch")
        if db.execute("PRAGMA integrity_check(1)").fetchone() != ("ok",):
            raise RegistrySchemaError("Registry file failed SQLite integrity check")
    except sqlite3.Error:
        io_fault = True
    # Raise outside the SQLite exception handler: even ``from None`` retains
    # private SQL/filename data in ``__context__`` for programmatic callers.
    if io_fault:
        raise RegistrySchemaError("Cannot establish registry schema integrity")
