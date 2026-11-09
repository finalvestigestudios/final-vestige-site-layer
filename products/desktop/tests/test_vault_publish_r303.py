"""R303: encrypted premium vault atomic private publication (synthetic)."""
from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import vault_publish as vault

SECRET = "SYNTHETIC-CONFIDENTIAL-GRANT-30719"


class VaultPublishR303Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r303-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.target = self.root / (SECRET + ".fvault")
        self.payload = b"\x00FVS synthetic ciphertext\xff" * 128

    def artifacts(self):
        return list(self.root.glob(".fvs-vault-*.partial"))

    def clean(self, call, expected=OSError, code=None):
        with self.assertRaises(expected) as e:
            call()
        fault = e.exception
        self.assertIsNone(fault.__context__)
        self.assertIsNone(fault.__cause__)
        self.assertNotIn(SECRET, repr(fault))
        self.assertIsNone(getattr(fault, "filename", None))
        if code is not None:
            self.assertEqual(fault.errno, code)
        self.assertFalse(self.target.exists())
        self.assertEqual(self.artifacts(), [])

    def test_exact_ciphertext_and_return_path(self):
        self.assertEqual(vault.publish_vault(self.target, self.payload), self.target)
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertEqual(self.artifacts(), [])

    def test_empty_ciphertext_is_byte_exact(self):
        vault.publish_vault(self.target, b"")
        self.assertEqual(self.target.read_bytes(), b"")

    def test_large_multi_block_ciphertext(self):
        data = bytes(range(256)) * 3072
        vault.publish_vault(self.target, data)
        self.assertEqual(self.target.read_bytes(), data)

    def test_existing_target_preserved(self):
        self.target.write_bytes(b"EXISTING")
        with self.assertRaises(FileExistsError) as e:
            vault.publish_vault(self.target, self.payload)
        self.assertIsNone(e.exception.__cause__)
        self.assertIsNone(e.exception.__context__)
        self.assertEqual(self.target.read_bytes(), b"EXISTING")
        self.assertEqual(self.artifacts(), [])

    def test_dangling_symlink_not_overwritten(self):
        try:
            self.target.symlink_to(self.root / "missing.fvault")
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable")
        with self.assertRaises(FileExistsError):
            vault.publish_vault(self.target, self.payload)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.artifacts(), [])

    def test_missing_folder_fails_before_write(self):
        with self.assertRaises(OSError):
            vault.publish_vault(self.root / "missing" / "file.fvault", self.payload)
        self.assertEqual(self.artifacts(), [])

    def test_symlink_directory_rejected(self):
        linked = self.root / "linked"
        try:
            linked.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable")
        with self.assertRaisesRegex(ValueError, "regular vault output folder"):
            vault.publish_vault(linked / "file.fvault", self.payload)
        self.assertFalse((self.root / "file.fvault").exists())

    def test_wrong_type_never_creates_staging(self):
        for data in (bytearray(b"secret"), memoryview(b"secret"), "secret", None):
            with self.subTest(data=type(data)):
                with self.assertRaisesRegex(ValueError, "Invalid or oversized"):
                    vault.publish_vault(self.target, data)
                self.assertEqual(self.artifacts(), [])

    def test_oversized_rejected_before_stage(self):
        with patch.object(vault, "MAX_VAULT_PUBLICATION_BYTES", 3):
            with self.assertRaisesRegex(ValueError, "Invalid or oversized"):
                vault.publish_vault(self.target, b"four")
        self.assertEqual(self.artifacts(), [])

    def test_mkstemp_oserror_has_no_private_chain(self):
        with patch.object(vault.tempfile, "mkstemp", side_effect=OSError(errno.ENOSPC, SECRET, str(self.target))):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.ENOSPC)

    def test_lstat_oserror_has_no_private_chain(self):
        with patch.object(Path, "lstat", side_effect=PermissionError(errno.EACCES, SECRET, str(self.target))):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.EACCES)

    def test_write_oserror_has_no_private_chain(self):
        with patch.object(vault.os, "write", side_effect=OSError(errno.EIO, SECRET, str(self.target))):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.EIO)

    def test_write_lying_zero_progress_rejected(self):
        with patch.object(vault.os, "write", return_value=0):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.EIO)

    def test_write_invalid_bool_rejected(self):
        with patch.object(vault.os, "write", return_value=True):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.EIO)

    def test_write_short_valid_is_retried(self):
        original = os.write
        def short(fd, data):
            return original(fd, data[:23])
        with patch.object(vault.os, "write", side_effect=short):
            vault.publish_vault(self.target, self.payload)
        self.assertEqual(self.target.read_bytes(), self.payload)

    def test_os_fsync_failure_has_no_private_chain(self):
        with patch.object(vault.os, "fsync", side_effect=OSError(errno.EIO, SECRET, str(self.target))):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.EIO)

    def test_staged_same_length_corruption_rejected(self):
        original = os.read
        def corrupt(fd, n):
            data = original(fd, n)
            return (b"!" + data[1:]) if data else data
        with patch.object(vault.os, "read", side_effect=corrupt):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.EIO)

    def test_staged_length_corruption_rejected(self):
        original = os.fstat
        def inflated(fd):
            class Stat:
                st_size = len(self.payload) + 1
            return Stat()
        with patch.object(vault.os, "fstat", side_effect=inflated):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.EIO)

    def test_publish_link_or_rename_failure_private(self):
        step = "rename" if os.name == "nt" else "link"
        with patch.object(vault.os, step, side_effect=PermissionError(errno.EACCES, SECRET, str(self.target))):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.EACCES)

    def test_late_collision_does_not_replace_target(self):
        original = os.rename if os.name == "nt" else os.link
        step = "rename" if os.name == "nt" else "link"
        def collision(src, dst):
            Path(dst).write_bytes(b"RACING_OWNER")
            raise FileExistsError(errno.EEXIST, SECRET, str(dst))
        with patch.object(vault.os, step, side_effect=collision):
            with self.assertRaises(FileExistsError) as caught:
                vault.publish_vault(self.target, self.payload)
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)
        self.assertEqual(self.target.read_bytes(), b"RACING_OWNER")
        self.assertEqual(self.artifacts(), [])

    def test_interrupt_passthrough_and_cleanup(self):
        with patch.object(vault.os, "fsync", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                vault.publish_vault(self.target, self.payload)
        self.assertFalse(self.target.exists())
        self.assertEqual(self.artifacts(), [])

    def test_staging_names_do_not_expose_customer_path(self):
        real = tempfile.mkstemp
        observed = []
        def capture(*args, **kwargs):
            observed.append((kwargs["prefix"], kwargs["suffix"]))
            return real(*args, **kwargs)
        with patch.object(vault.tempfile, "mkstemp", side_effect=capture):
            vault.publish_vault(self.target, self.payload)
        self.assertEqual(observed, [(".fvs-vault-", ".partial")])
        self.assertEqual(self.artifacts(), [])

    def test_final_name_invisible_until_fsync_completed(self):
        real = os.fsync
        observed = []
        def inspect(fd):
            observed.append(self.target.exists())
            return real(fd)
        with patch.object(vault.os, "fsync", side_effect=inspect):
            vault.publish_vault(self.target, self.payload)
        self.assertEqual(observed, [False])
        self.assertEqual(self.target.read_bytes(), self.payload)

    def test_descriptor_close_fault_is_sanitized_once(self):
        real = os.close
        closed = []
        def close(fd):
            closed.append(fd)
            real(fd)
            raise OSError(errno.EIO, SECRET, str(self.target))
        with patch.object(vault.os, "close", side_effect=close):
            self.clean(lambda: vault.publish_vault(self.target, self.payload), code=errno.EIO)
        self.assertEqual(len(closed), 1)


if __name__ == "__main__":
    unittest.main()
