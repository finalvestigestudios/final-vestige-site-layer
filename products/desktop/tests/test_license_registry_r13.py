"""R13: offline issuance registry regression tests; synthetic IDs/files only."""
import hashlib
import os
import sqlite3
from contextlib import closing
import tempfile
import threading
import unittest
from pathlib import Path

from license_registry import IssuanceRegistry, RegistryError


class RegistryR13Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.database = self.root / "issuer.sqlite3"
        self.registry = IssuanceRegistry(self.database)
        self.output = self.root / "test.fvslicense"
        self.data = {"license_id": "test-license-0001", "product": "grants",
                     "kid": "example-key-001", "output": self.output}

    def reserve(self, **kw):
        self.registry.reserve(**{**self.data, **kw})

    def finalize(self, **kw):
        # Existing synthetic registry tests have no signing authority; pass
        # the exact synthetic fixture digest to exercise the R16 API contract.
        target = Path(kw.get("output", self.output))
        expected = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else "0" * 64
        return self.registry.finalize(**{**self.data, **kw}, expected_sha256=expected)

    def status(self):
        with closing(sqlite3.connect(self.database)) as con, con:
            return con.execute("SELECT state,license_sha256 FROM issuance WHERE license_id=?",
                               (self.data["license_id"],)).fetchone()

    def test_reserve_and_finalize_have_no_holder_or_path_plaintext(self):
        self.reserve()
        self.assertEqual(self.status(), ("reserved", None))
        self.output.write_bytes(b'{"synthetic":true}\n')
        digest = self.finalize()
        self.assertEqual(self.status(), ("issued", digest))
        contents = self.database.read_bytes()
        self.assertNotIn(str(self.output).encode(), contents)
        self.assertNotIn(b"Authorized Customer", contents)
        self.assertNotIn(b"PRIVATE KEY", contents)

    def test_reusing_id_even_for_other_premium_product_is_rejected(self):
        self.reserve()
        with self.assertRaisesRegex(RegistryError, "already reserved"):
            self.reserve(product="procurement", output=self.root / "another.fvslicense")
        self.assertEqual(self.status(), ("reserved", None))

    def test_reservation_persists_after_failed_issuer_attempt(self):
        self.reserve()
        self.assertFalse(self.output.exists())
        with self.assertRaises(RegistryError):
            IssuanceRegistry(self.database).reserve(**self.data)
        self.assertEqual(self.status(), ("reserved", None))

    def test_finalization_requires_matching_reserved_attributes(self):
        self.reserve()
        self.output.write_bytes(b"test")
        for update in ({"product": "procurement"}, {"kid": "different-kid"},
                       {"output": self.root / "other.fvslicense"}):
            with self.subTest(update=update), self.assertRaises(RegistryError):
                self.finalize(**update)
            self.assertEqual(self.status(), ("reserved", None))

    def test_missing_file_does_not_finalize(self):
        self.reserve()
        with self.assertRaisesRegex(RegistryError, "Cannot read"):
            self.finalize()
        self.assertEqual(self.status(), ("reserved", None))

    def test_issued_row_cannot_be_finalized_twice(self):
        self.reserve()
        self.output.write_bytes(b"first")
        self.finalize()
        self.output.write_bytes(b"tampered")
        with self.assertRaisesRegex(RegistryError, "No matching reserved"):
            self.finalize()
        self.assertNotEqual(self.status()[1], "tampered")

    def test_concurrent_process_style_id_reservation_is_serialized(self):
        barrier = threading.Barrier(3)
        results = []
        def worker():
            other = IssuanceRegistry(self.database)
            barrier.wait()
            try:
                other.reserve(**self.data)
                results.append("ok")
            except RegistryError:
                results.append("duplicate")
        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)
        t1.start(); t2.start(); barrier.wait()
        t1.join(timeout=10); t2.join(timeout=10)
        self.assertFalse(t1.is_alive() or t2.is_alive())
        self.assertCountEqual(results, ["ok", "duplicate"])

    def test_invalid_id_product_path_and_collision_are_denied(self):
        for changes in ({"license_id": "x"}, {"kid": "?"},
                        {"product": "free"}, {"output": Path("relative.fvslicense")},
                        {"output": self.root / "wrong.json"}):
            with self.subTest(changes=changes), self.assertRaises(RegistryError):
                self.reserve(**changes)
        self.assertFalse(self.database.exists())
        self.output.write_bytes(b"do not overwrite")
        with self.assertRaisesRegex(RegistryError, "already exists"):
            self.reserve()
        self.assertEqual(self.output.read_bytes(), b"do not overwrite")

    def test_symlink_database_and_output_are_rejected(self):
        original = self.root / "original"
        original.write_bytes(b"not a database")
        try:
            self.database.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink unavailable")
        with self.assertRaisesRegex(RegistryError, "symlink"):
            self.reserve()
        self.database.unlink()
        self.reserve()
        other = self.root / "another"
        other.write_bytes(b"preserve")
        self.output.symlink_to(other)
        with self.assertRaisesRegex(RegistryError, "regular file"):
            self.finalize()
        self.assertEqual(other.read_bytes(), b"preserve")
        self.assertEqual(self.status(), ("reserved", None))

    def test_reject_registry_in_git_worktree(self):
        workspace = self.root / "code"
        workspace.mkdir()
        (workspace / ".git").mkdir()
        with self.assertRaisesRegex(RegistryError, "outside Git"):
            IssuanceRegistry(workspace / "registry.sqlite3")

    @unittest.skipUnless(os.name == "posix", "POSIX filesystem mode test")
    def test_reject_group_readable_parent_and_registry_file(self):
        self.root.chmod(0o755)
        with self.assertRaisesRegex(RegistryError, "owner-only"):
            IssuanceRegistry(self.database)
        self.root.chmod(0o700)
        self.reserve()
        self.database.chmod(0o644)
        with self.assertRaisesRegex(RegistryError, "operator"):
            self.registry.reserve(license_id="another-id-001", product="grants",
                                  kid="example-key-001", output=self.root / "other.fvslicense")

    def test_wrong_or_missing_file_fails_without_marking_issued(self):
        self.reserve()
        self.output.write_bytes(b"Z" * 8193)
        with self.assertRaisesRegex(RegistryError, "bounded"):
            self.finalize()
        self.assertEqual(self.status(), ("reserved", None))


class RegistryCliIntegrationR13Tests(unittest.TestCase):
    """Execute the actual R12 cryptographic CLI with a temporary test-only key."""

    def setUp(self):
        from datetime import datetime, timedelta, timezone
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.key = Ed25519PrivateKey.generate()
        self.password = "synthetic-passphrase-only"
        self.pem = self.root / "test-key.pem"
        self.pem.write_bytes(self.key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(self.password.encode("utf-8"))))
        if os.name == "posix":
            self.pem.chmod(0o600)
        self.target = self.root / "test-license.fvslicense"
        self.registry_path = self.root / "issuance.sqlite3"
        expires = (datetime.now(timezone.utc) + timedelta(days=400)).replace(microsecond=0)
        self.args = [
            "--key", str(self.pem), "--registry", str(self.registry_path),
            "--kid", "test-only-operator-01", "--product", "grants",
            "--license-id", "test-only-license-001", "--holder", "Synthetic Org",
            "--expires-at", expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "--output", str(self.target), "--confirm-issue",
        ]

    def run_cli(self, password=None):
        import io
        from contextlib import redirect_stdout, redirect_stderr
        from unittest.mock import patch
        import license_issuer
        with patch.object(license_issuer.sys.stdin, "isatty", return_value=True), \
             patch.object(license_issuer.getpass, "getpass",
                          return_value=self.password if password is None else password), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return license_issuer.main(self.args)

    def test_real_signed_cli_issues_only_once_and_registry_hash_matches(self):
        from cryptography.hazmat.primitives import serialization
        from fvs_suite import offline_entitlement as verifier
        self.assertEqual(self.run_cli(), 0)
        public = self.key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        license_data = verifier.verify_license(
            self.target, "grants", trusted_keys={"test-only-operator-01": public})
        self.assertEqual(license_data.license_id, "test-only-license-001")
        before = self.target.read_bytes()
        with closing(sqlite3.connect(self.registry_path)) as con, con:
            state, digest = con.execute(
                "SELECT state,license_sha256 FROM issuance WHERE license_id=?",
                ("test-only-license-001",)).fetchone()
        import hashlib
        self.assertEqual(state, "issued")
        self.assertEqual(digest, hashlib.sha256(before).hexdigest())
        with self.assertRaises(SystemExit) as error:
            self.run_cli()
        self.assertEqual(error.exception.code, 1)
        self.assertEqual(self.target.read_bytes(), before)

    def test_wrong_passphrase_reservation_cannot_be_reused(self):
        with self.assertRaises(SystemExit) as error:
            self.run_cli(password="invalid-passphrase")
        self.assertEqual(error.exception.code, 1)
        self.assertFalse(self.target.exists())
        with closing(sqlite3.connect(self.registry_path)) as con, con:
            self.assertEqual(con.execute(
                "SELECT state FROM issuance WHERE license_id=?",
                ("test-only-license-001",)).fetchone(), ("reserved",))
        with self.assertRaises(SystemExit) as error:
            self.run_cli()
        self.assertEqual(error.exception.code, 1)
        self.assertFalse(self.target.exists())



if __name__ == "__main__":
    unittest.main()
