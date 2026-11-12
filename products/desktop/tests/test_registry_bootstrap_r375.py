"""R375: synthetic operator-side SQLite bootstrap custody and audit regression tests."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from contextlib import closing
from unittest.mock import MagicMock, patch

from license_registry import IssuanceRegistry, RegistryError

SECRET = "C:/Customers/private-client/license-ledger.sqlite3 SECRET-CANARY"


class RegistryBootstrapR375Tests(unittest.TestCase):
    def setUp(self):
        # Bypass only the pathname preflight to inject controlled SQLite faults.
        # R13/R14/R15 cover real file ownership, schema and record validation.
        self.registry = object.__new__(IssuanceRegistry)
        self.registry.path = Path("/synthetic/registry.sqlite3")
        self.registry._check_file = lambda: None
        self.db = MagicMock()

    def _assert_private(self, error):
        self.assertEqual(str(error), "Cannot initialize protected registry")
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)
        self.assertNotIn(SECRET, repr(error))

    def test_each_of_four_setup_statements_closes_connection_with_clean_public_error(self):
        for index in range(4):
            with self.subTest(statement=index):
                conn = MagicMock()
                count = 0

                def execute(_sql):
                    nonlocal count
                    old = count
                    count += 1
                    if old == index:
                        raise sqlite3.OperationalError(SECRET)

                conn.execute.side_effect = execute
                with patch("license_registry.sqlite3.connect", return_value=conn):
                    with self.assertRaises(RegistryError) as caught:
                        with self.registry._db():
                            self.fail("Never allow partially configured SQLite connection")
                self._assert_private(caught.exception)
                conn.close.assert_called_once_with()
                self.assertEqual(count, index + 1)

    def test_connect_failure_redacted_without_inherited_exception(self):
        with patch("license_registry.sqlite3.connect", side_effect=sqlite3.OperationalError(SECRET)):
            with self.assertRaises(RegistryError) as caught:
                with self.registry._db():
                    pass
        self._assert_private(caught.exception)

    def test_sqlite_connection_is_closed_after_valid_body(self):
        with patch("license_registry.sqlite3.connect", return_value=self.db):
            with self.registry._db() as conn:
                self.assertIs(conn, self.db)
                conn.execute("SELECT 1")
        self.db.close.assert_called_once()
        self.assertEqual(self.db.execute.call_count, 5)

    def test_sqlite_connection_is_closed_if_body_raises(self):
        with patch("license_registry.sqlite3.connect", return_value=self.db):
            with self.assertRaisesRegex(RuntimeError, "synthetic body failure"):
                with self.registry._db():
                    raise RuntimeError("synthetic body failure")
        self.db.close.assert_called_once()

    def test_keyboard_interrupt_during_initialization_closes_connection(self):
        self.db.execute.side_effect = KeyboardInterrupt()
        with patch("license_registry.sqlite3.connect", return_value=self.db):
            with self.assertRaises(KeyboardInterrupt):
                with self.registry._db():
                    pass
        self.db.close.assert_called_once()

    def test_system_exit_during_initialization_closes_connection(self):
        self.db.execute.side_effect = SystemExit(9)
        with patch("license_registry.sqlite3.connect", return_value=self.db):
            with self.assertRaises(SystemExit) as caught:
                with self.registry._db():
                    pass
        self.assertEqual(caught.exception.code, 9)
        self.db.close.assert_called_once()

    def test_failed_setup_close_error_is_suppressed_not_exposed(self):
        self.db.execute.side_effect = sqlite3.OperationalError(SECRET)
        self.db.close.side_effect = sqlite3.OperationalError(SECRET)
        with patch("license_registry.sqlite3.connect", return_value=self.db):
            with self.assertRaises(RegistryError) as caught:
                with self.registry._db():
                    pass
        self._assert_private(caught.exception)
        self.db.close.assert_called_once()

    def test_success_uses_exact_busy_timeout_isolation_and_ddl(self):
        with patch("license_registry.sqlite3.connect", return_value=self.db) as connect:
            with self.registry._db():
                pass
        connect.assert_called_once_with(str(self.registry.path), timeout=5, isolation_level=None)
        sql = [call.args[0] for call in self.db.execute.call_args_list]
        self.assertEqual(sql[:3], [
            "PRAGMA busy_timeout=5000", "PRAGMA journal_mode=DELETE",
            "PRAGMA synchronous=FULL",
        ])
        self.assertIn("CREATE TABLE IF NOT EXISTS issuance", sql[3])
        self.assertIn("license_id TEXT PRIMARY KEY", sql[3])
        self.assertIn("product IN ('grants','procurement')", sql[3])

    def test_check_file_failure_prevents_connect(self):
        self.registry._check_file = lambda: (_ for _ in ()).throw(RegistryError("Unsafe file"))
        with patch("license_registry.sqlite3.connect") as connect:
            with self.assertRaisesRegex(RegistryError, "Unsafe file"):
                with self.registry._db():
                    pass
        connect.assert_not_called()

    def test_postsetup_failure_never_yields_or_closes_twice(self):
        self.db.execute.side_effect = sqlite3.DatabaseError(SECRET)
        yielded = False
        with patch("license_registry.sqlite3.connect", return_value=self.db):
            with self.assertRaises(RegistryError):
                with self.registry._db():
                    yielded = True
        self.assertFalse(yielded)
        self.db.close.assert_called_once()

    def test_real_sqlite_connection_creates_exact_table_and_closes(self):
        with tempfile.TemporaryDirectory() as directory:
            self.registry.path = Path(directory) / "issuer.sqlite3"
            with self.registry._db() as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute(
                    "INSERT INTO issuance (license_id,product,kid,output_path_sha256,state,reserved_at)"
                    " VALUES ('test-id-001','grants','test-key-001',?,'reserved','2026-11-12T00:00:00Z')",
                    ("a" * 64,),
                )
                db.execute("COMMIT")
            with closing(sqlite3.connect(self.registry.path)) as db:
                state = db.execute("SELECT state FROM issuance").fetchone()[0]
            self.assertEqual(state, "reserved")

    def test_existing_schema_still_requires_separate_r14_schema_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            self.registry.path = Path(directory) / "issuer.sqlite3"
            with closing(sqlite3.connect(self.registry.path)) as db:
                db.execute("CREATE TABLE issuance (some_other_column TEXT)")
            # Bootstrap does not replace the exact R14 schema guard.
            with self.registry._db() as db:
                self.assertEqual(
                    db.execute("SELECT name FROM sqlite_schema").fetchone(), ("issuance",)
                )


if __name__ == "__main__":
    unittest.main()
