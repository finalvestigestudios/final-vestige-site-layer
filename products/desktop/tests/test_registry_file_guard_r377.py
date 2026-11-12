"""R377: offline premium SQLite registry path safety and descriptor privacy."""
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import registry_file_guard as guard


PRIVATE = "/PRIVATE/BILLING-CLIENT/PRIVATE-ISSUER-R377.sqlite3"


class PublicError(ValueError):
    pass


class RegistryFileGuardR377Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.db = self.root / "issuer.sqlite3"

    def check(self):
        guard.verify_registry_file(self.db, PublicError)

    def assert_private_failure(self, caught, message):
        err = caught.exception
        self.assertIs(type(err), PublicError)
        self.assertEqual(str(err), message)
        self.assertIsNone(err.__context__)
        self.assertIsNone(err.__cause__)
        self.assertNotIn(PRIVATE, repr(err))

    def test_creates_0600_private_registry(self):
        self.check()
        self.assertTrue(self.db.is_file())
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.db.stat().st_mode), 0o600)
        self.assertEqual(self.db.read_bytes(), b"")

    def test_existing_registry_is_not_truncated_or_modified(self):
        payload = b"pretend SQLite data \x00 and private identifiers"
        self.db.write_bytes(payload)
        if os.name == "posix":
            self.db.chmod(0o600)
        self.check()
        self.assertEqual(self.db.read_bytes(), payload)

    def test_existing_file_must_be_regular(self):
        self.db.write_bytes(b"nonempty")
        if os.name == "posix":
            self.db.chmod(0o600)
        with patch.object(guard.stat, "S_ISREG", return_value=False):
            with self.assertRaises(PublicError) as caught:
                self.check()
        self.assert_private_failure(caught, "Registry must be a regular file")

    def test_existing_symlink_rejected_and_target_unchanged(self):
        original = self.root / "target.sqlite3"
        original.write_bytes(b"do not modify")
        try:
            self.db.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        with self.assertRaises(PublicError) as caught:
            self.check()
        self.assert_private_failure(caught, "Registry must not be a symlink")
        self.assertEqual(original.read_bytes(), b"do not modify")

    @unittest.skipUnless(hasattr(os, "link"), "Hardlinks unavailable")
    def test_hardlink_alias_is_rejected_without_modification(self):
        original = self.root / "unrelated-operator-file.sqlite3"
        original.write_bytes(b"KEEP-ORIGINAL-OPERATOR-DATA")
        try:
            os.link(original, self.db)
        except OSError:
            self.skipTest("Filesystem hardlinks unavailable")
        with self.assertRaises(PublicError) as caught:
            self.check()
        self.assert_private_failure(caught, "Registry must not have hard links")
        self.assertEqual(original.read_bytes(), b"KEEP-ORIGINAL-OPERATOR-DATA")
        self.assertEqual(self.db.stat().st_nlink, 2)

    @unittest.skipUnless(os.name == "posix", "Owner and mode enforced on POSIX")
    def test_group_readable_existing_registry_rejected(self):
        self.db.write_bytes(b"original")
        self.db.chmod(0o640)
        with self.assertRaises(PublicError) as caught:
            self.check()
        self.assert_private_failure(caught, "Registry file must be owned and readable only by operator")
        self.assertEqual(self.db.read_bytes(), b"original")

    def test_initial_create_fault_redacted_without_exception_chain(self):
        with patch.object(guard.os, "open", side_effect=PermissionError(PRIVATE)):
            with self.assertRaises(PublicError) as caught:
                self.check()
        self.assert_private_failure(caught, "Cannot create protected registry")

    def test_existing_open_fault_redacted_without_exception_chain(self):
        with patch.object(guard.os, "open", side_effect=[FileExistsError(PRIVATE), PermissionError(PRIVATE)]):
            with self.assertRaises(PublicError) as caught:
                self.check()
        self.assert_private_failure(caught, "Cannot open protected registry")

    def test_metadata_fault_redacted_and_descriptor_closed(self):
        real_open = os.open
        real_close = os.close
        seen = []
        def tracked_open(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            seen.append(fd)
            return fd
        with patch.object(guard.os, "open", side_effect=tracked_open), \
             patch.object(guard.os, "fstat", side_effect=PermissionError(PRIVATE)), \
             patch.object(guard.os, "close", side_effect=real_close) as close:
            with self.assertRaises(PublicError) as caught:
                self.check()
        self.assert_private_failure(caught, "Cannot inspect protected registry")
        self.assertEqual(close.call_count, 1)
        self.assertEqual(close.call_args.args[0], seen[0])
        with self.assertRaises(OSError):
            os.fstat(seen[0])

    def test_close_fault_redacted_without_exception_chain(self):
        real_close = os.close
        def closed_but_reported_failed(fd):
            real_close(fd)
            raise PermissionError(PRIVATE)
        with patch.object(guard.os, "close", side_effect=closed_but_reported_failed):
            with self.assertRaises(PublicError) as caught:
                self.check()
        self.assert_private_failure(caught, "Cannot close protected registry")

    def test_file_inspection_path_fault_does_not_leak(self):
        with patch.object(Path, "is_symlink", side_effect=OSError(PRIVATE)):
            with self.assertRaises(PublicError) as caught:
                self.check()
        self.assert_private_failure(caught, "Cannot inspect protected registry path")

    def test_repeated_checks_never_rewrite_existing_registry(self):
        self.check()
        self.db.write_bytes(b"immutable bytes")
        for _ in range(4):
            self.check()
        self.assertEqual(self.db.read_bytes(), b"immutable bytes")

    def test_protection_is_independent_of_product_license_tier(self):
        for name in ("grant-audit.sqlite3", "procure-guard.sqlite3"):
            self.db = self.root / name
            self.check()
            self.assertTrue(self.db.is_file())

    def test_never_imports_external_financial_content(self):
        self.db.write_bytes(b"private source records stay untouched")
        if os.name == "posix":
            self.db.chmod(0o600)
        with patch.object(guard.os, "read", side_effect=AssertionError("read forbidden")):
            self.check()
        self.assertEqual(self.db.read_bytes(), b"private source records stay untouched")


if __name__ == "__main__":
    unittest.main()
