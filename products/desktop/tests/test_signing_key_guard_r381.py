"""R381: operator-only signing key custody with synthetic private PEM fixtures.

No customer records, live keys, network requests or premium distribution.
"""
from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import signing_key_guard as guard

CANARY = "/confidential/operator/customer-name/do-not-log.pem"


class OperatorKeyError(ValueError):
    pass


class SigningKeyGuardR381Tests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="fvs-r381-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.path = self.root / "operator.pem"
        self.secret = b"SYNTHETIC-ENCRYPTED-PEM-CONTENT" * 4
        self.path.write_bytes(self.secret)
        if os.name == "posix":
            self.path.chmod(0o600)

    def read(self, path=None, limit=16384):
        return guard.read_signing_key(path or self.path, limit, OperatorKeyError)

    def denied(self, fragment):
        with self.assertRaises(OperatorKeyError) as caught:
            self.read()
        err = caught.exception
        self.assertIn(fragment, str(err))
        self.assertIsNone(err.__cause__)
        self.assertIsNone(err.__context__)
        self.assertNotIn(CANARY, repr(err))

    def test_private_regular_file_returns_exact_bytes_without_writes(self):
        self.assertEqual(self.read(), self.secret)
        self.assertEqual(self.path.read_bytes(), self.secret)

    def test_reject_missing_file_without_create(self):
        self.path.unlink()
        self.denied("Cannot open")
        self.assertFalse(self.path.exists())

    def test_reject_directory(self):
        self.path.unlink()
        self.path.mkdir()
        self.denied("regular file")

    def test_reject_hardlink_alias_without_mutating_original(self):
        alias = self.root / "second-name.pem"
        try:
            os.link(self.path, alias)
        except (OSError, NotImplementedError):
            self.skipTest("Hard links not supported on filesystem")
        self.denied("hard links")
        self.assertEqual(alias.read_bytes(), self.secret)

    def test_reject_symlink_without_following(self):
        alias = self.root / "actual.pem"
        self.path.rename(alias)
        try:
            self.path.symlink_to(alias)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not supported")
        self.denied("symlink")
        self.assertEqual(alias.read_bytes(), self.secret)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation unsupported")
    def test_reject_fifo_without_blocking_on_open(self):
        self.path.unlink()
        os.mkfifo(self.path)
        self.denied("regular file")

    @unittest.skipUnless(os.name == "posix", "POSIX permission check")
    def test_reject_world_readable_key(self):
        self.path.chmod(0o644)
        self.denied("owner-only")

    def test_reject_file_too_large_before_read(self):
        self.denied_with_limit(4, "bounded")

    def denied_with_limit(self, limit, expected):
        with self.assertRaises(OperatorKeyError) as caught:
            self.read(limit=limit)
        self.assertIn(expected, str(caught.exception))

    def test_reject_bad_limit_without_file_access(self):
        for bad in (0, -1, True, 0.5):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.read(limit=bad)

    def test_detect_path_replacement_before_open(self):
        old_open = guard.os.open
        other = self.root / "replacement.pem"
        other.write_bytes(self.secret)
        if os.name == "posix":
            other.chmod(0o600)
        def replace(path, flags):
            self.path.unlink()
            other.rename(self.path)
            return old_open(path, flags)
        with patch.object(guard.os, "open", side_effect=replace):
            self.denied("identity changed")

    def test_detect_path_replacement_after_read(self):
        original_read = guard.os.read
        other = self.root / "replacement.pem"
        other.write_bytes(self.secret)
        if os.name == "posix":
            other.chmod(0o600)
        seen = False
        def replace(fd, length):
            nonlocal seen
            data = original_read(fd, length)
            if not seen:
                seen = True
                self.path.unlink()
                other.rename(self.path)
            return data
        with patch.object(guard.os, "read", side_effect=replace):
            self.denied("identity changed")

    def test_detect_in_place_length_mutation_mid_read(self):
        old_read = guard.os.read
        seen = False
        def corrupt(fd, n):
            nonlocal seen
            data = old_read(fd, n)
            if not seen:
                seen = True
                with open(self.path, "ab") as out:
                    out.write(b"UNEXPECTED-TRAILER")
            return data
        with patch.object(guard.os, "read", side_effect=corrupt):
            self.denied("identity changed")

    def test_reparse_metadata_denied_even_when_regular(self):
        original_lstat = guard.os.lstat
        def reparse(path):
            actual = original_lstat(path)
            return SimpleNamespace(**{name: getattr(actual, name)
                for name in ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
                             "st_mtime_ns", "st_ctime_ns", "st_uid")},
                st_file_attributes=0x400)
        with patch.object(guard.os, "lstat", side_effect=reparse):
            self.denied("reparse")

    def test_open_oserror_hides_private_path_and_chains(self):
        with patch.object(guard.os, "open", side_effect=PermissionError(CANARY)):
            self.denied("Cannot open")

    def test_fstat_oserror_hides_private_path_and_closes_descriptor(self):
        opened = []
        real_open = guard.os.open
        def track(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd
        with patch.object(guard.os, "open", side_effect=track), \
             patch.object(guard.os, "fstat", side_effect=OSError(CANARY)):
            self.denied("Cannot inspect")
        self.assertEqual(len(opened), 1)
        with self.assertRaises(OSError):
            os.fstat(opened[0])

    def test_read_oserror_hides_private_path(self):
        with patch.object(guard.os, "read", side_effect=OSError(CANARY)):
            self.denied("Cannot inspect")

    def test_postread_lstat_oserror_hides_private_path(self):
        real_lstat = guard.os.lstat
        count = 0
        def fail_after(*args):
            nonlocal count
            count += 1
            if count > 1:
                raise OSError(CANARY)
            return real_lstat(*args)
        with patch.object(guard.os, "lstat", side_effect=fail_after):
            self.denied("Cannot inspect")

    def test_close_oserror_hides_private_path(self):
        real_close = guard.os.close
        def failed_close(fd):
            real_close(fd)
            raise OSError(CANARY)
        with patch.object(guard.os, "close", side_effect=failed_close):
            self.denied("Cannot close")

    def test_real_encrypted_ed25519_key_roundtrip(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        real_key = Ed25519PrivateKey.generate()
        password = b"synthetic-test-only-password"
        self.path.write_bytes(real_key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(password)))
        restored = serialization.load_pem_private_key(self.read(), password=password)
        signature = restored.sign(b"R381 synthetic fixture")
        real_key.public_key().verify(signature, b"R381 synthetic fixture")


if __name__ == "__main__":
    unittest.main()
