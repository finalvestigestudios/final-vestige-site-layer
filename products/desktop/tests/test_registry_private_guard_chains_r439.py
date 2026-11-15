"""R439: confidential SQLite faults never survive operator-facing exception chains.

All IDs and file bytes are synthetic. No actual premium issuance is performed.
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import license_registry as registry
from registry_schema_guard import RegistrySchemaError, enforce_registry_schema
from registry_row_guard import RegistryRowError, enforce_registry_rows


CANARY = "SECRET-SQL-CUSTOMER-ACCOUNT-778899"


class BrokenConnection:
    def execute(self, _sql):
        raise sqlite3.OperationalError(CANARY)


def nested_failure(error_cls):
    """Simulate a private nested SQLite failure raised by an inner guard."""
    try:
        raise sqlite3.DatabaseError(CANARY)
    except sqlite3.DatabaseError as fault:
        raise error_cls("Cannot inspect protected internal state") from fault


class R439PrivateRegistryChainTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        if os.name == "posix":
            self.root.chmod(0o700)
        self.db_path = self.root / "synthetic.sqlite3"
        self.output = self.root / "synthetic.fvslicense"
        self.ledger = registry.IssuanceRegistry(self.db_path)
        self.fields = dict(license_id="test-license-r439", kid="test-key-r439",
                           product="grants", output=self.output)

    def assert_private_chain_cleared(self, error, expected_cls):
        self.assertIs(type(error), expected_cls)
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn(CANARY, str(error))
        self.assertNotIn(CANARY, repr(error))

    def read_rows(self):
        with closing(sqlite3.connect(self.db_path)) as con:
            return con.execute("SELECT license_id,state,license_sha256 FROM issuance").fetchall()

    def test_schema_inspection_private_sql_error_has_no_chain(self):
        with self.assertRaises(RegistrySchemaError) as caught:
            enforce_registry_schema(BrokenConnection())
        self.assert_private_chain_cleared(caught.exception, RegistrySchemaError)

    def test_row_inspection_private_sql_error_has_no_chain(self):
        with self.assertRaises(RegistryRowError) as caught:
            enforce_registry_rows(BrokenConnection())
        self.assert_private_chain_cleared(caught.exception, RegistryRowError)

    def test_reserve_schema_guard_failure_rolls_back_without_secret_chain(self):
        self._check_reserve_guard("enforce_registry_schema", RegistrySchemaError)

    def test_reserve_row_guard_failure_rolls_back_without_secret_chain(self):
        self._check_reserve_guard("enforce_registry_rows", RegistryRowError)

    def _check_reserve_guard(self, guard_name, error_cls):
        with patch.object(registry, guard_name, side_effect=lambda _db: nested_failure(error_cls)):
            with self.assertRaises(registry.RegistryError) as caught:
                self.ledger.reserve(**self.fields)
        self.assert_private_chain_cleared(caught.exception, registry.RegistryError)
        self.assertEqual(self.read_rows(), [])
        # Transaction remains usable after rollback; a failed validation did
        # not partially reserve the identifier or issue a license.
        self.ledger.reserve(**self.fields)
        self.assertEqual(self.read_rows(), [(self.fields["license_id"], "reserved", None)])

    def test_finalize_schema_guard_failure_keeps_reservation(self):
        self._check_finalize_guard("enforce_registry_schema", RegistrySchemaError)

    def test_finalize_row_guard_failure_keeps_reservation(self):
        self._check_finalize_guard("enforce_registry_rows", RegistryRowError)

    def _check_finalize_guard(self, guard_name, error_cls):
        self.ledger.reserve(**self.fields)
        data = b"test-only-signed-payload-not-a-license"
        self.output.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        with patch.object(registry, guard_name, side_effect=lambda _db: nested_failure(error_cls)):
            with self.assertRaises(registry.RegistryError) as caught:
                self.ledger.finalize(**self.fields, expected_sha256=digest)
        self.assert_private_chain_cleared(caught.exception, registry.RegistryError)
        self.assertEqual(self.read_rows(), [(self.fields["license_id"], "reserved", None)])
        self.assertEqual(self.output.read_bytes(), data)
        # Synthetic byte-custody only: no real signature or authorization.
        self.assertEqual(self.ledger.finalize(**self.fields, expected_sha256=digest), digest)
        self.assertEqual(self.read_rows(), [(self.fields["license_id"], "issued", digest)])

    def test_schema_drift_is_still_denied_without_side_effects(self):
        self.ledger.reserve(**self.fields)
        with closing(sqlite3.connect(self.db_path)) as con, con:
            con.execute("CREATE TABLE surprise (private_data TEXT)")
        other = dict(self.fields, license_id="different-id-r439", output=self.root / "other.fvslicense")
        with self.assertRaises(registry.RegistryError) as caught:
            self.ledger.reserve(**other)
        self.assert_private_chain_cleared(caught.exception, registry.RegistryError)
        self.assertEqual(self.read_rows(), [(self.fields["license_id"], "reserved", None)])

    def test_corrupt_row_is_still_denied_without_side_effects(self):
        self.ledger.reserve(**self.fields)
        with closing(sqlite3.connect(self.db_path)) as con, con:
            con.execute("UPDATE issuance SET reserved_at='bad-timestamp'")
        other = dict(self.fields, license_id="different-id-r439", output=self.root / "other.fvslicense")
        with self.assertRaises(registry.RegistryError) as caught:
            self.ledger.reserve(**other)
        self.assert_private_chain_cleared(caught.exception, registry.RegistryError)
        self.assertEqual(self.read_rows(), [(self.fields["license_id"], "reserved", None)])


if __name__ == "__main__":
    unittest.main()
