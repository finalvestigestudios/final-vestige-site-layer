"""R376: fail-closed premium SQLite write transactions; no private error chains."""
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import MagicMock

from registry_write_guard import run_protected_write


PRIVATE = "C:/Private/ClientLedger/SECRET-CANARY-376.sqlite3"
CONFLICT = "License ID already reserved or issued; do not reuse"
DATABASE = "Could not durably reserve license ID"


class PublicRegistryError(ValueError):
    pass


class RegistryWriteR376Tests(unittest.TestCase):
    def run_write(self, db, action=lambda _db: "result"):
        return run_protected_write(
            db, action,
            conflict_message=CONFLICT,
            database_message=DATABASE,
            error_type=PublicRegistryError,
        )

    def assert_clean_error(self, caught, expected):
        error = caught.exception
        self.assertIs(type(error), PublicRegistryError)
        self.assertEqual(str(error), expected)
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)
        self.assertNotIn(PRIVATE, repr(error))

    def test_success_commits_exactly_once_without_rollback(self):
        db = MagicMock()
        output = self.run_write(db, lambda connection: (connection.execute("INSERT INTO demo VALUES (1)"), 123)[1])
        self.assertEqual(output, 123)
        self.assertEqual([call.args[0] for call in db.execute.call_args_list],
                         ["BEGIN IMMEDIATE", "INSERT INTO demo VALUES (1)", "COMMIT"])

    def test_begin_failure_is_redacted_and_never_rolls_back_unowned_transaction(self):
        db = MagicMock()
        db.execute.side_effect = sqlite3.OperationalError(PRIVATE)
        with self.assertRaises(PublicRegistryError) as caught:
            self.run_write(db)
        self.assert_clean_error(caught, DATABASE)
        self.assertEqual(db.execute.call_count, 1)

    def test_action_database_failure_rolls_back_and_redacts(self):
        db = MagicMock()
        def action(_):
            raise sqlite3.OperationalError(PRIVATE)
        with self.assertRaises(PublicRegistryError) as caught:
            self.run_write(db, action)
        self.assert_clean_error(caught, DATABASE)
        self.assertEqual([call.args[0] for call in db.execute.call_args_list],
                         ["BEGIN IMMEDIATE", "ROLLBACK"])

    def test_integrity_error_gets_specific_conflict_message(self):
        db = MagicMock()
        def action(_):
            raise sqlite3.IntegrityError(PRIVATE)
        with self.assertRaises(PublicRegistryError) as caught:
            self.run_write(db, action)
        self.assert_clean_error(caught, CONFLICT)
        self.assertEqual([call.args[0] for call in db.execute.call_args_list],
                         ["BEGIN IMMEDIATE", "ROLLBACK"])

    def test_commit_failure_rolls_back_and_does_not_return_result(self):
        db = MagicMock()
        def execute(statement):
            if statement == "COMMIT":
                raise sqlite3.OperationalError(PRIVATE)
        db.execute.side_effect = execute
        with self.assertRaises(PublicRegistryError) as caught:
            self.run_write(db, lambda _: "must-not-return")
        self.assert_clean_error(caught, DATABASE)
        self.assertEqual([call.args[0] for call in db.execute.call_args_list],
                         ["BEGIN IMMEDIATE", "COMMIT", "ROLLBACK"])

    def test_rollback_failure_never_masks_primary_error_or_leaks(self):
        db = MagicMock()
        def execute(statement):
            if statement == "ROLLBACK":
                raise sqlite3.OperationalError(PRIVATE)
        db.execute.side_effect = execute
        with self.assertRaises(PublicRegistryError) as caught:
            self.run_write(db, lambda _: (_ for _ in ()).throw(sqlite3.DatabaseError(PRIVATE)))
        self.assert_clean_error(caught, DATABASE)
        self.assertEqual(db.execute.call_count, 2)

    def test_registry_domain_error_propagates_with_cleanup(self):
        db = MagicMock()
        domain_error = PublicRegistryError("Manual review needed")
        with self.assertRaises(PublicRegistryError) as caught:
            self.run_write(db, lambda _: (_ for _ in ()).throw(domain_error))
        self.assertIs(caught.exception, domain_error)
        self.assertEqual([call.args[0] for call in db.execute.call_args_list],
                         ["BEGIN IMMEDIATE", "ROLLBACK"])

    def test_keyboard_interrupt_is_not_swallowed(self):
        db = MagicMock()
        with self.assertRaises(KeyboardInterrupt):
            self.run_write(db, lambda _: (_ for _ in ()).throw(KeyboardInterrupt()))
        self.assertEqual([call.args[0] for call in db.execute.call_args_list],
                         ["BEGIN IMMEDIATE", "ROLLBACK"])

    def test_system_exit_is_not_swallowed(self):
        db = MagicMock()
        with self.assertRaises(SystemExit) as caught:
            self.run_write(db, lambda _: (_ for _ in ()).throw(SystemExit(37)))
        self.assertEqual(caught.exception.code, 37)
        self.assertEqual([call.args[0] for call in db.execute.call_args_list],
                         ["BEGIN IMMEDIATE", "ROLLBACK"])

    def test_rollback_failure_does_not_hide_non_sqlite_domain_error(self):
        db = MagicMock()
        db.execute.side_effect = lambda statement: (_ for _ in ()).throw(sqlite3.DatabaseError(PRIVATE)) if statement == "ROLLBACK" else None
        with self.assertRaisesRegex(PublicRegistryError, "Manual review"):
            self.run_write(db, lambda _: (_ for _ in ()).throw(PublicRegistryError("Manual review")))

    def test_real_sqlite_commit_is_durable(self):
        with tempfile.TemporaryDirectory() as directory:
            db = sqlite3.connect(Path(directory) / "issuer.sqlite3", isolation_level=None)
            try:
                db.execute("CREATE TABLE issuance (license_id TEXT PRIMARY KEY)")
                result = self.run_write(db, lambda conn: (conn.execute("INSERT INTO issuance VALUES ('ONE-001')"), "success")[1])
                self.assertEqual(result, "success")
            finally:
                db.close()
            check = sqlite3.connect(Path(directory) / "issuer.sqlite3")
            try:
                self.assertEqual(check.execute("SELECT license_id FROM issuance").fetchall(), [("ONE-001",)])
            finally:
                check.close()

    def test_real_sqlite_integrity_failure_does_not_change_existing_row(self):
        with closing(sqlite3.connect(":memory:", isolation_level=None)) as db:
            db.execute("CREATE TABLE issuance (license_id TEXT PRIMARY KEY)")
            self.run_write(db, lambda conn: conn.execute("INSERT INTO issuance VALUES ('ONE-001')"))
            with self.assertRaises(PublicRegistryError) as caught:
                self.run_write(db, lambda conn: conn.execute("INSERT INTO issuance VALUES ('ONE-001')"))
            self.assert_clean_error(caught, CONFLICT)
            self.assertEqual(db.execute("SELECT count(*) FROM issuance").fetchone()[0], 1)
            self.assertFalse(db.in_transaction)

    def test_real_sqlite_domain_failure_rolls_back_prior_write(self):
        with closing(sqlite3.connect(":memory:", isolation_level=None)) as db:
            db.execute("CREATE TABLE issuance (license_id TEXT PRIMARY KEY)")
            def failing(conn):
                conn.execute("INSERT INTO issuance VALUES ('ONE-001')")
                raise PublicRegistryError("manual inspection")
            with self.assertRaisesRegex(PublicRegistryError, "manual inspection"):
                self.run_write(db, failing)
            self.assertEqual(db.execute("SELECT count(*) FROM issuance").fetchone()[0], 0)
            self.assertFalse(db.in_transaction)

    def test_real_sqlite_followup_writes_after_integrity_failure(self):
        with closing(sqlite3.connect(":memory:", isolation_level=None)) as db:
            db.execute("CREATE TABLE issuance (license_id TEXT PRIMARY KEY)")
            self.run_write(db, lambda conn: conn.execute("INSERT INTO issuance VALUES ('ONE-001')"))
            with self.assertRaises(PublicRegistryError):
                self.run_write(db, lambda conn: conn.execute("INSERT INTO issuance VALUES ('ONE-001')"))
            self.run_write(db, lambda conn: conn.execute("INSERT INTO issuance VALUES ('TWO-002')"))
            self.assertEqual(db.execute("SELECT license_id FROM issuance ORDER BY license_id").fetchall(),
                             [("ONE-001",), ("TWO-002",)])


if __name__ == "__main__":
    unittest.main()
