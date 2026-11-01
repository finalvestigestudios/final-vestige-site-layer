"""R14 fail-closed schema guard regression tests (synthetic SQLite only)."""
import hashlib
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path

from registry_schema_guard import (
    EXPECTED_ISSUANCE_DDL,
    RegistrySchemaError,
    enforce_registry_schema,
)


class RegistrySchemaGuardR14Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.database = Path(tmp.name) / "license-issuer.sqlite3"
        self.db = sqlite3.connect(self.database, isolation_level=None)
        self.addCleanup(self.db.close)

    def _safe_table(self):
        self.db.execute(EXPECTED_ISSUANCE_DDL)

    def _validate(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            enforce_registry_schema(self.db)
        finally:
            self.db.execute("ROLLBACK")

    def test_valid_r13_schema_accepts_clean_registry(self):
        self._safe_table()
        self._validate()

    def test_valid_schema_with_reserved_issuance_accepts(self):
        self._safe_table()
        self.db.execute("""INSERT INTO issuance
            (license_id,product,kid,output_path_sha256,state,reserved_at)
            VALUES ('safe-id-001','grants','kid-001','fingerprint','reserved','2026-10-28T01:00:00Z')""")
        self._validate()

    def test_no_primary_key_schema_is_refused(self):
        self.db.execute(EXPECTED_ISSUANCE_DDL.replace("license_id TEXT PRIMARY KEY", "license_id TEXT"))
        with self.assertRaises(RegistrySchemaError):
            self._validate()

    def test_removed_product_check_is_refused(self):
        self.db.execute(EXPECTED_ISSUANCE_DDL.replace(
            "product TEXT NOT NULL CHECK(product IN ('grants','procurement'))",
            "product TEXT NOT NULL"))
        with self.assertRaises(RegistrySchemaError):
            self._validate()

    def test_removed_state_check_is_refused(self):
        self.db.execute(EXPECTED_ISSUANCE_DDL.replace(
            "state TEXT NOT NULL CHECK(state IN ('reserved','issued'))",
            "state TEXT NOT NULL"))
        with self.assertRaises(RegistrySchemaError):
            self._validate()

    def test_unexpected_column_is_refused(self):
        self._safe_table()
        self.db.execute("ALTER TABLE issuance ADD COLUMN secret TEXT")
        with self.assertRaises(RegistrySchemaError):
            self._validate()

    def test_trigger_is_refused(self):
        self._safe_table()
        self.db.execute("""CREATE TRIGGER discard_issuance AFTER INSERT ON issuance
            BEGIN DELETE FROM issuance WHERE license_id=NEW.license_id; END""")
        with self.assertRaises(RegistrySchemaError):
            self._validate()

    def test_additional_view_is_refused(self):
        self._safe_table()
        self.db.execute("CREATE VIEW leakage AS SELECT * FROM issuance")
        with self.assertRaises(RegistrySchemaError):
            self._validate()

    def test_additional_index_is_refused(self):
        self._safe_table()
        self.db.execute("CREATE INDEX lookup_key ON issuance(kid)")
        with self.assertRaises(RegistrySchemaError):
            self._validate()

    def test_extra_table_is_refused(self):
        self._safe_table()
        self.db.execute("CREATE TABLE unsafe (x TEXT)")
        with self.assertRaises(RegistrySchemaError):
            self._validate()

    def test_missing_table_is_refused(self):
        with self.assertRaises(RegistrySchemaError):
            self._validate()

    def test_internal_primary_key_index_does_not_trigger_false_positive(self):
        self._safe_table()
        # The autoindex is an intentional sqlite_ internal object; visible
        # user-owned objects are restricted to the single issuance table.
        self.assertEqual(len(self.db.execute("PRAGMA index_list('issuance')").fetchall()), 1)
        self._validate()

    def test_view_replacing_issuance_is_refused(self):
        self.db.execute("CREATE TABLE other_data (id INTEGER)")
        self.db.execute("CREATE VIEW issuance AS SELECT id FROM other_data")
        with self.assertRaises(RegistrySchemaError):
            self._validate()


class RegistryIntegrationR14Tests(unittest.TestCase):
    """Exercise the actual R13 reservation/finalization entry points."""

    def setUp(self):
        from license_registry import IssuanceRegistry
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.registry_path = self.root / "registry.sqlite3"
        self.registry = IssuanceRegistry(self.registry_path)
        self.output = self.root / "sample.fvslicense"
        self.kwargs = {"license_id": "regression-id-001", "product": "grants",
                       "kid": "test-key-001", "output": self.output}

    def test_new_registry_remains_compatible_with_r13_reserve_finalize(self):
        import hashlib
        self.registry.reserve(**self.kwargs)
        self.output.write_bytes(b'synthetic-license-content')
        digest = self.registry.finalize(**self.kwargs, expected_sha256=hashlib.sha256(self.output.read_bytes()).hexdigest())
        self.assertEqual(digest, hashlib.sha256(b'synthetic-license-content').hexdigest())
        with closing(sqlite3.connect(self.registry_path)) as con, con:
            self.assertEqual(con.execute("SELECT state FROM issuance").fetchone(), ("issued",))

    def test_missing_unique_primary_key_blocks_reservation_before_write(self):
        from license_registry import RegistryError
        with closing(sqlite3.connect(self.registry_path)) as con, con:
            con.execute(EXPECTED_ISSUANCE_DDL.replace(
                "license_id TEXT PRIMARY KEY", "license_id TEXT"))
        # sqlite3.connect created this external test database outside the
        # protected registry constructor; apply R13 owner-only file policy.
        import os
        if os.name == "posix":
            self.registry_path.chmod(0o600)
        with self.assertRaisesRegex(RegistryError, "Unsafe registry schema"):
            self.registry.reserve(**self.kwargs)
        with closing(sqlite3.connect(self.registry_path)) as con, con:
            self.assertEqual(con.execute("SELECT count(*) FROM issuance").fetchone(), (0,))

    def test_trigger_inserted_after_reservation_blocks_finalization(self):
        from license_registry import RegistryError
        self.registry.reserve(**self.kwargs)
        self.output.write_bytes(b'synthetic-license-content')
        with closing(sqlite3.connect(self.registry_path)) as con, con:
            con.execute("""CREATE TRIGGER rewriting AFTER UPDATE ON issuance
                BEGIN UPDATE issuance SET state='reserved' WHERE license_id=NEW.license_id; END""")
        with self.assertRaisesRegex(RegistryError, "Unsafe registry schema"):
            self.registry.finalize(**self.kwargs, expected_sha256=hashlib.sha256(self.output.read_bytes()).hexdigest())
        with closing(sqlite3.connect(self.registry_path)) as con, con:
            self.assertEqual(con.execute("SELECT state FROM issuance").fetchone(), ("reserved",))

    def test_secondary_index_inserted_after_reservation_blocks_new_id(self):
        from license_registry import RegistryError
        self.registry.reserve(**self.kwargs)
        with closing(sqlite3.connect(self.registry_path)) as con, con:
            con.execute("CREATE INDEX unexpected ON issuance(kid)")
        with self.assertRaisesRegex(RegistryError, "Unsafe registry schema"):
            self.registry.reserve(**{**self.kwargs,
                "license_id": "regression-id-002",
                "output": self.root / "another.fvslicense"})
        with closing(sqlite3.connect(self.registry_path)) as con, con:
            self.assertEqual(con.execute("SELECT count(*) FROM issuance").fetchone(), (1,))


if __name__ == "__main__":
    unittest.main()
