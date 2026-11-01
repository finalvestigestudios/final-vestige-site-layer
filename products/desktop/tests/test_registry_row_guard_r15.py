"""R15 synthetic operator registry semantic guard regression tests."""
import hashlib
import sqlite3
from contextlib import closing
import unittest

from registry_row_guard import RegistryRowError, enforce_registry_rows

DDL = """CREATE TABLE issuance (
    license_id TEXT PRIMARY KEY,
    product TEXT NOT NULL CHECK(product IN ('grants','procurement')),
    kid TEXT NOT NULL,
    output_path_sha256 TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('reserved','issued')),
    license_sha256 TEXT,
    reserved_at TEXT NOT NULL,
    issued_at TEXT
)"""
PATH1 = "a" * 64
PATH2 = "b" * 64
DIGEST = "c" * 64
RESERVED_AT = "2026-10-28T08:00:00Z"
ISSUED_AT = "2026-10-28T08:15:00Z"


class SemanticGuardR15Tests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        self.addCleanup(self.db.close)
        self.db.execute(DDL)

    def insert(self, **changes):
        data = dict(license_id="license-001", product="grants", kid="operator-01",
                    output_path_sha256=PATH1, state="reserved", license_sha256=None,
                    reserved_at=RESERVED_AT, issued_at=None)
        data.update(changes)
        self.db.execute("INSERT INTO issuance VALUES (?,?,?,?,?,?,?,?)", tuple(data.values()))

    def guard(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            enforce_registry_rows(self.db)
        finally:
            self.db.execute("ROLLBACK")

    def test_empty_registry_is_valid(self):
        self.guard()

    def test_valid_reserved_is_valid(self):
        self.insert()
        self.guard()

    def test_valid_issued_and_reserved_rows_are_valid(self):
        self.insert(state="issued", license_sha256=DIGEST, issued_at=ISSUED_AT)
        self.insert(license_id="license-002", output_path_sha256=PATH2)
        self.guard()

    def test_malformed_identifiers_fail(self):
        for change in ({"license_id": "ab"}, {"license_id": "bad id"},
                       {"kid": "?"}, {"kid": "a" * 65}):
            with self.subTest(change=change):
                self.db.execute("DELETE FROM issuance")
                self.insert(**change)
                with self.assertRaises(RegistryRowError):
                    self.guard()

    def test_invalid_sha256_path_fails(self):
        for val in ("fingerprint", "A" * 64, "!" * 64):
            with self.subTest(val=val):
                self.db.execute("DELETE FROM issuance")
                self.insert(output_path_sha256=val)
                with self.assertRaises(RegistryRowError):
                    self.guard()

    def test_duplicate_destination_hash_fails_across_products(self):
        self.insert()
        self.insert(license_id="license-002", product="procurement")
        with self.assertRaisesRegex(RegistryRowError, "duplicate output"):
            self.guard()

    def test_distinct_destinations_across_products_valid(self):
        self.insert()
        self.insert(license_id="license-002", product="procurement", output_path_sha256=PATH2)
        self.guard()

    def test_reserved_must_not_have_issued_markers(self):
        for changes in ({"license_sha256": DIGEST}, {"issued_at": ISSUED_AT}):
            with self.subTest(changes=changes):
                self.db.execute("DELETE FROM issuance")
                self.insert(**changes)
                with self.assertRaises(RegistryRowError):
                    self.guard()

    def test_issued_must_have_valid_digest(self):
        for digest in (None, "z" * 64, "C" * 64, "short"):
            with self.subTest(digest=digest):
                self.db.execute("DELETE FROM issuance")
                self.insert(state="issued", license_sha256=digest, issued_at=ISSUED_AT)
                with self.assertRaises(RegistryRowError):
                    self.guard()

    def test_issued_must_have_canonical_chronology(self):
        for issued in (None, "2026-10-28T07:00:00Z", "2026-10-28 08:15:00Z",
                       "2026-13-28T08:15:00Z", "2026-10-28T8:15:00Z"):
            with self.subTest(issued=issued):
                self.db.execute("DELETE FROM issuance")
                self.insert(state="issued", license_sha256=DIGEST, issued_at=issued)
                with self.assertRaises(RegistryRowError):
                    self.guard()

    def test_invalid_reservation_time_fails(self):
        for reserved in ("2026-10-28T8:00:00Z", "2026-02-30T08:00:00Z", ""):
            with self.subTest(reserved=reserved):
                self.db.execute("DELETE FROM issuance")
                self.insert(reserved_at=reserved)
                with self.assertRaises(RegistryRowError):
                    self.guard()

    def test_sqlite_failure_fails_closed(self):
        self.db.execute("DROP TABLE issuance")
        with self.assertRaisesRegex(RegistryRowError, "Unable to inspect"):
            self.guard()


class RegistryEntryPointR15Tests(unittest.TestCase):
    def setUp(self):
        import tempfile
        from pathlib import Path
        from license_registry import IssuanceRegistry
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.registry_file = self.root / "operator.sqlite3"
        self.registry = IssuanceRegistry(self.registry_file)
        self.output = self.root / "entitlement.fvslicense"
        self.params = dict(license_id="synthetic-001", product="grants",
                           kid="test-key-001", output=self.output)

    def test_first_reservation_then_finalization_still_works(self):
        import hashlib
        self.registry.reserve(**self.params)
        self.output.write_bytes(b"synthetic signed entitlement bytes")
        digest = self.registry.finalize(**self.params, expected_sha256=hashlib.sha256(self.output.read_bytes()).hexdigest())
        self.assertEqual(digest, hashlib.sha256(self.output.read_bytes()).hexdigest())
        with closing(sqlite3.connect(self.registry_file)) as db, db:
            self.assertEqual(db.execute("SELECT state FROM issuance").fetchone(), ("issued",))

    def test_same_output_path_cannot_be_reserved_twice(self):
        from license_registry import RegistryError
        self.registry.reserve(**self.params)
        with self.assertRaisesRegex(RegistryError, "destination already reserved"):
            self.registry.reserve(**{**self.params, "license_id": "synthetic-002"})
        with closing(sqlite3.connect(self.registry_file)) as db, db:
            self.assertEqual(db.execute("SELECT count(*) FROM issuance").fetchone(), (1,))

    def test_semantic_corruption_blocks_new_reservations(self):
        from license_registry import RegistryError
        self.registry.reserve(**self.params)
        with closing(sqlite3.connect(self.registry_file)) as db, db:
            db.execute("UPDATE issuance SET license_sha256=? WHERE license_id=?",
                       ("f" * 64, "synthetic-001"))
        with self.assertRaisesRegex(RegistryError, "Unsafe registry schema or issuance records"):
            self.registry.reserve(license_id="synthetic-002", product="procurement",
                                  kid="test-key-001", output=self.root / "other.fvslicense")
        with closing(sqlite3.connect(self.registry_file)) as db, db:
            self.assertEqual(db.execute("SELECT count(*) FROM issuance").fetchone(), (1,))

    def test_finalize_rejects_clock_rollback_without_poisoning_record(self):
        from unittest.mock import patch
        from license_registry import RegistryError
        self.registry.reserve(**self.params)
        self.output.write_bytes(b"synthetic entitlement")
        with patch("license_registry._stamp", return_value="2000-01-01T00:00:00Z"):
            with self.assertRaisesRegex(RegistryError, "No matching reserved issuance"):
                self.registry.finalize(**self.params, expected_sha256=hashlib.sha256(self.output.read_bytes()).hexdigest())
        with closing(sqlite3.connect(self.registry_file)) as db, db:
            self.assertEqual(db.execute("SELECT state,issued_at FROM issuance").fetchone(),
                             ("reserved", None))

    def test_tampered_finalized_digest_blocks_other_reservations(self):
        from license_registry import RegistryError
        self.registry.reserve(**self.params)
        self.output.write_bytes(b"synthetic entitlement")
        self.registry.finalize(**self.params, expected_sha256=hashlib.sha256(self.output.read_bytes()).hexdigest())
        with closing(sqlite3.connect(self.registry_file)) as db, db:
            db.execute("UPDATE issuance SET license_sha256='tampered'")
        with self.assertRaisesRegex(RegistryError, "Unsafe registry"):
            self.registry.reserve(license_id="synthetic-002", product="grants",
                                  kid="test-key-001", output=self.root / "other.fvslicense")


if __name__ == "__main__":
    unittest.main()
