"""R440 operator-only premium issuance: private CLI and SQLite teardown custody.

All canaries, paths, registry rows and signed-byte fixtures are synthetic.
No licenses are signed, distributed or accepted by a public customer flow.
"""
from __future__ import annotations

import hashlib
import io
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import license_issuer as issuer
import license_registry as registry

SECRET = "PRIVATE-R440-CUSTOMER-PATH-SQL-887766"


class CloseFaultConnection:
    """Commit through real SQLite, then simulate a private close diagnostic."""

    def __init__(self, real):
        self.real = real

    def execute(self, *args, **kwargs):
        return self.real.execute(*args, **kwargs)

    def close(self):
        self.real.close()
        raise sqlite3.OperationalError(SECRET)


class R440PrivateRegistryTeardownTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        if os.name == "posix":
            self.root.chmod(0o700)
        self.ledger = registry.IssuanceRegistry(self.root / "synthetic.sqlite3")
        self.output = self.root / "synthetic.fvslicense"
        self.fields = {"license_id": "synthetic-r440-license", "kid": "synthetic-r440-kid",
                       "product": "grants", "output": self.output}
        self.real_connect = sqlite3.connect

    def wrapped_close(self):
        original = self.real_connect
        return patch.object(registry.sqlite3, "connect",
                            side_effect=lambda *a, **k: CloseFaultConnection(original(*a, **k)))

    def rows(self):
        with closing(self.real_connect(self.ledger.path)) as db:
            return db.execute(
                "SELECT license_id,state,license_sha256 FROM issuance"
            ).fetchall()

    def check_public(self, error):
        self.assertIs(type(error), registry.RegistryError)
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn(SECRET, str(error))
        self.assertNotIn(SECRET, repr(error))

    def test_reservation_committed_before_close_fault_stays_reserved(self):
        with self.wrapped_close(), self.assertRaises(registry.RegistryError) as caught:
            self.ledger.reserve(**self.fields)
        self.check_public(caught.exception)
        self.assertIn("close", str(caught.exception))
        self.assertEqual(self.rows(), [(self.fields["license_id"], "reserved", None)])
        with self.assertRaises(registry.RegistryError):
            self.ledger.reserve(**self.fields)

    def test_finalization_committed_before_close_fault_requires_manual_review(self):
        self.ledger.reserve(**self.fields)
        data = b"synthetic-byte-evidence-not-a-signed-license"
        self.output.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        with self.wrapped_close(), self.assertRaises(registry.RegistryError) as caught:
            self.ledger.finalize(**self.fields, expected_sha256=digest)
        self.check_public(caught.exception)
        self.assertEqual(self.rows(), [(self.fields["license_id"], "issued", digest)])
        self.assertEqual(self.output.read_bytes(), data)
        with self.assertRaises(registry.RegistryError):
            self.ledger.finalize(**self.fields, expected_sha256=digest)

    def test_close_fault_does_not_replace_schema_refusal(self):
        self.ledger.reserve(**self.fields)
        with closing(self.real_connect(self.ledger.path)) as db, db:
            db.execute("CREATE TABLE synthetic_extra (private_data TEXT)")
        other = dict(self.fields, license_id="synthetic-r440-other",
                     output=self.root / "other.fvslicense")
        with self.wrapped_close(), self.assertRaises(registry.RegistryError) as caught:
            self.ledger.reserve(**other)
        self.check_public(caught.exception)
        self.assertIn("Unsafe registry schema", str(caught.exception))
        self.assertEqual(self.rows(), [(self.fields["license_id"], "reserved", None)])

    def test_successful_close_keeps_normal_reserve_finalize_behavior(self):
        self.ledger.reserve(**self.fields)
        content = b"synthetic-original-bytes"
        self.output.write_bytes(content)
        digest = hashlib.sha256(content).hexdigest()
        self.assertEqual(self.ledger.finalize(**self.fields, expected_sha256=digest), digest)
        self.assertEqual(self.rows(), [(self.fields["license_id"], "issued", digest)])


class R440PrivateCliFaultTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.args = [
            "--key", str(root / "secret-key.pem"), "--registry", str(root / "private.sqlite3"),
            "--kid", "synthetic-r440-kid", "--product", "grants",
            "--license-id", "synthetic-r440-license", "--holder", "Test Entity",
            "--expires-at", "2027-11-14T00:00:00Z",
            "--output", str(root / "synthetic.fvslicense"), "--confirm-issue",
        ]
        self.target = root / "synthetic.fvslicense"

    def invoke(self, *, phase="reserve", fault=None):
        stderr = io.StringIO()
        stdout = io.StringIO()
        with patch.object(issuer.sys.stdin, "isatty", return_value=True), \
             patch.object(issuer.getpass, "getpass", return_value="synthetic-only"), \
             patch.object(issuer, "IssuanceRegistry") as reg_class, \
             patch.object(issuer, "issue_entitlement",
                          return_value=(self.target, "a" * 64)) as issue, \
             redirect_stderr(stderr), redirect_stdout(stdout):
            reg_class.return_value.finalize.return_value = "a" * 64
            if fault is not None:
                if phase == "issue":
                    issue.side_effect = fault
                else:
                    getattr(reg_class.return_value, phase).side_effect = fault
            try:
                returned = issuer.main(self.args)
            except SystemExit as exit_error:
                returned = exit_error
        return returned, stderr.getvalue(), stdout.getvalue(), reg_class, issue

    def assert_refusal(self, result, stderr, *, contains=None):
        self.assertIs(type(result), SystemExit)
        self.assertEqual(result.code, 1)
        self.assertIsNone(result.__cause__)
        self.assertIsNone(result.__context__)
        self.assertNotIn(SECRET, stderr)
        self.assertNotIn(SECRET, str(result))
        if contains:
            self.assertIn(contains, stderr)

    def test_os_fault_is_generic_not_private_in_cli_or_exception_chain(self):
        result, stderr, _, _, _ = self.invoke(fault=OSError(SECRET))
        self.assert_refusal(result, stderr, contains="Unexpected protected issuance failure")

    def test_unexpected_value_fault_is_generic_not_private(self):
        result, stderr, _, _, _ = self.invoke(fault=ValueError(SECRET))
        self.assert_refusal(result, stderr, contains="Unexpected protected issuance failure")

    def test_unexpected_sqlite_fault_is_generic_not_traceback(self):
        result, stderr, _, _, _ = self.invoke(fault=sqlite3.OperationalError(SECRET))
        self.assert_refusal(result, stderr, contains="Unexpected protected issuance failure")

    def test_post_reservation_issuer_fault_does_not_finalize(self):
        result, stderr, _, reg_class, _ = self.invoke(phase="issue", fault=OSError(SECRET))
        self.assert_refusal(result, stderr, contains="manual review")
        reg_class.return_value.reserve.assert_called_once()
        reg_class.return_value.finalize.assert_not_called()

    def test_post_issuance_finalize_fault_is_not_reported_as_success(self):
        result, stderr, stdout, reg_class, _ = self.invoke(
            phase="finalize", fault=sqlite3.DatabaseError(SECRET))
        self.assert_refusal(result, stderr, contains="Unexpected protected issuance failure")
        self.assertEqual(stdout, "")
        reg_class.return_value.finalize.assert_called_once()

    def test_known_sanitized_refusals_remain_informative(self):
        for exc, phrase in (
            (registry.RegistryError("Registry requires manual inspection"), "Registry requires manual inspection"),
            (issuer.IssuanceError("Cannot decrypt encrypted signing key"), "Cannot decrypt encrypted signing key"),
            (issuer.verifier.EntitlementError("Invalid entitlement signature"), "Invalid entitlement signature"),
        ):
            with self.subTest(phrase=phrase):
                result, stderr, _, _, _ = self.invoke(fault=exc)
                self.assert_refusal(result, stderr, contains=phrase)

    def test_success_keeps_digest_and_does_not_emit_customer_private_paths(self):
        result, stderr, stdout, reg_class, _ = self.invoke()
        self.assertEqual(result, 0)
        self.assertEqual(stderr, "")
        self.assertIn("SHA-256 " + "a" * 64, stdout)
        self.assertIn("Distribution NOT authorized", stdout)
        self.assertNotIn(str(self.target), stdout)
        reg_class.return_value.finalize.assert_called_once()


if __name__ == "__main__":
    unittest.main()
