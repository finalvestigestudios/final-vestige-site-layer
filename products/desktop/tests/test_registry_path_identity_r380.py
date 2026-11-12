"""R380: real-file path/descriptor witnesses for the offline premium SQLite registry.

Synthetic temporary files only; no customer data, keys, network or publication.
"""
from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import registry_file_guard as guard

PRIVATE = "/PRIVATE/OPERATOR-RECORDS/SECRET-REGISTRY.sqlite3"


class PublicError(ValueError):
    pass


class RegistryPathIdentityR380Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.db = self.root / "issuer.sqlite3"
        self.other = self.root / "unrelated.sqlite3"
        self.other.write_bytes(b"do not open or modify unrelated file")
        if os.name == "posix":
            self.other.chmod(0o600)

    def check(self):
        return guard.verify_registry_file(self.db, PublicError)

    def failure(self, fragment):
        with self.assertRaises(PublicError) as caught:
            self.check()
        self.assertIn(fragment, str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(PRIVATE, repr(caught.exception))

    def established(self):
        self.db.write_bytes(b"original private registry")
        if os.name == "posix":
            self.db.chmod(0o600)

    @staticmethod
    def with_reparse(actual):
        fields = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
                  "st_mtime_ns", "st_ctime_ns", "st_uid")
        return SimpleNamespace(**{n: getattr(actual, n, 0) for n in fields},
                               st_file_attributes=0x400)

    def test_fresh_private_create_preserves_zero_bytes(self):
        self.check()
        self.assertEqual(self.db.read_bytes(), b"")
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.db.stat().st_mode), 0o600)

    def test_existing_bytes_remain_unread_and_unmodified(self):
        self.established()
        original = self.db.read_bytes()
        with patch.object(guard.os, "read", side_effect=AssertionError("do not read registry")):
            self.check()
        self.assertEqual(self.db.read_bytes(), original)

    def test_original_path_replaced_with_unrelated_file_before_open(self):
        self.established()
        real_open = os.open
        original_other = self.other.read_bytes()
        replaced = []
        def opening(path, flags, *args, **kwargs):
            if not (flags & os.O_EXCL):
                os.replace(self.other, self.db)
                replaced.append(True)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(guard.os, "open", side_effect=opening):
            self.failure("identity changed")
        self.assertEqual(replaced, [True])
        self.assertEqual(self.db.read_bytes(), original_other)

    def test_same_byte_replacement_before_open_is_still_rejected(self):
        self.established()
        self.other.write_bytes(self.db.read_bytes())
        real_open = os.open
        def swap(path, flags, *args, **kwargs):
            if not (flags & os.O_EXCL):
                os.replace(self.other, self.db)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(guard.os, "open", side_effect=swap):
            self.failure("identity changed")
        self.assertEqual(self.db.read_bytes(), b"original private registry")

    def test_path_replaced_after_descriptor_open_is_rejected(self):
        self.established()
        real_fstat = os.fstat
        swapped = []
        def fstat_after_swap(fd):
            result = real_fstat(fd)
            os.replace(self.other, self.db)
            swapped.append(True)
            return result
        with patch.object(guard.os, "fstat", side_effect=fstat_after_swap):
            self.failure("identity changed")
        self.assertEqual(swapped, [True])
        self.assertEqual(self.db.read_bytes(), b"do not open or modify unrelated file")

    def test_missing_path_created_by_other_actor_before_exclusive_create(self):
        real_open = os.open
        interfered = []
        def racing_create(path, flags, *args, **kwargs):
            if (flags & os.O_EXCL) and not interfered:
                self.db.write_bytes(b"external registry")
                if os.name == "posix":
                    self.db.chmod(0o600)
                interfered.append(True)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(guard.os, "open", side_effect=racing_create):
            self.failure("identity changed")
        self.assertEqual(interfered, [True])
        self.assertEqual(self.db.read_bytes(), b"external registry")

    def test_existing_reparse_point_metadata_is_rejected_before_open(self):
        self.established()
        real_lstat = os.lstat
        def reparse(path, *args, **kwargs):
            return self.with_reparse(real_lstat(path, *args, **kwargs))
        with patch.object(guard.os, "lstat", side_effect=reparse), \
             patch.object(guard.os, "open", side_effect=AssertionError("no open")) as opened:
            self.failure("reparse point")
        opened.assert_not_called()

    def test_new_reparse_after_descriptor_open_is_rejected(self):
        self.established()
        real_lstat = os.lstat
        calls = []
        def post_open_reparse(path, *args, **kwargs):
            actual = real_lstat(path, *args, **kwargs)
            calls.append(True)
            return self.with_reparse(actual) if len(calls) >= 2 else actual
        with patch.object(guard.os, "lstat", side_effect=post_open_reparse):
            self.failure("reparse point")
        self.assertGreaterEqual(len(calls), 2)

    def test_preopen_lstat_private_path_is_redacted(self):
        self.established()
        with patch.object(guard.os, "lstat", side_effect=PermissionError(PRIVATE)):
            self.failure("Cannot inspect protected registry path")

    def test_postopen_lstat_private_path_is_redacted_and_fd_closed(self):
        self.established()
        real_lstat, real_open, real_fstat = os.lstat, os.open, os.fstat
        calls, owned = [], []
        def path_fault(path, *args, **kwargs):
            calls.append(True)
            if len(calls) >= 2:
                raise PermissionError(PRIVATE)
            return real_lstat(path, *args, **kwargs)
        def capture_open(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            owned.append(fd)
            return fd
        with patch.object(guard.os, "lstat", side_effect=path_fault), \
             patch.object(guard.os, "open", side_effect=capture_open):
            self.failure("Cannot inspect protected registry path")
        self.assertEqual(len(owned), 1)
        with self.assertRaises(OSError):
            real_fstat(owned[0])

    def test_fd_identity_metadata_mismatch_is_rejected(self):
        self.established()
        real_fstat = os.fstat
        def fake_inode(fd):
            actual = real_fstat(fd)
            keys = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
                    "st_mtime_ns", "st_ctime_ns", "st_uid")
            values = {key: getattr(actual, key, 0) for key in keys}
            values["st_ino"] += 1
            return SimpleNamespace(**values)
        with patch.object(guard.os, "fstat", side_effect=fake_inode):
            self.failure("identity changed")

    def test_both_premium_issuance_registry_names_supported(self):
        for name in ("grantaudit.sqlite3", "procureguard.sqlite3"):
            self.db = self.root / name
            self.check()
            self.assertTrue(self.db.is_file())


if __name__ == "__main__":
    unittest.main()
