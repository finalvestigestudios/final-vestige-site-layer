"""R308 deterministic synthetic regression: final-name rollback provenance.

Checks a narrow same-directory rename/link race in premium encrypted evidence
publication without customer data, networking, or executable distribution.
"""
from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import vault_publish as vault

SENSITIVE = "SYNTHETIC-CONFIDENTIAL-INVOICE-R308"


class VaultRollbackCustodyR308(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r308-")
        self.addCleanup(tmp.cleanup)
        self.directory = Path(tmp.name)
        self.target = self.directory / (SENSITIVE + ".fvault")
        self.payload = bytes(range(256)) * 1031

    def _stages(self):
        return list(self.directory.glob(".fvs-vault-*.partial"))

    def _assert_redacted(self, call, number=errno.EIO):
        with self.assertRaises(OSError) as raised:
            call()
        exc = raised.exception
        self.assertEqual(exc.errno, number)
        self.assertIsNone(exc.__context__)
        self.assertIsNone(exc.__cause__)
        self.assertIsNone(exc.filename)
        self.assertNotIn(SENSITIVE, repr(exc))

    def _replace_final_after_link(self, content, *, symlink=False):
        action = "rename" if os.name == "nt" else "link"
        replacement = self.directory / "another-writer.txt"
        original = getattr(os, action)

        def replace(stage, destination, *args, **kwargs):
            result = original(stage, destination, *args, **kwargs)
            if symlink:
                replacement.symlink_to(self.directory / "protected.txt")
            else:
                replacement.write_bytes(content)
            os.replace(replacement, destination)
            return result
        return action, replace

    def test_good_large_payload_no_temp_files(self):
        self.assertEqual(vault.publish_vault(self.target, self.payload), self.target)
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertFalse(self._stages())

    def test_good_empty_payload_no_temp_files(self):
        vault.publish_vault(self.target, b"")
        self.assertEqual(self.target.read_bytes(), b"")
        self.assertFalse(self._stages())

    def test_final_regular_replaced_before_first_stat_preserved(self):
        alien = b"This belongs to another local writer, not the vault"
        action, replace = self._replace_final_after_link(alien)
        with patch.object(vault.os, action, side_effect=replace):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload))
        self.assertEqual(self.target.read_bytes(), alien)
        self.assertFalse(self._stages())

    def test_final_equal_size_regular_replaced_before_first_stat_preserved(self):
        alien = bytes([self.payload[0] ^ 0x01]) + self.payload[1:]
        action, replace = self._replace_final_after_link(alien)
        with patch.object(vault.os, action, side_effect=replace):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload))
        self.assertEqual(self.target.read_bytes(), alien)
        self.assertFalse(self._stages())

    def test_final_same_bytes_different_inode_replaced_before_first_stat_preserved(self):
        action, replace = self._replace_final_after_link(self.payload)
        with patch.object(vault.os, action, side_effect=replace):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload))
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertFalse(self._stages())

    @unittest.skipIf(os.name == "nt", "Symlink creation may require Windows privileges")
    def test_final_symlink_swapped_before_first_stat_is_not_deleted(self):
        private = self.directory / "protected.txt"
        private.write_bytes(b"protected source content")
        action, replace = self._replace_final_after_link(b"", symlink=True)
        with patch.object(vault.os, action, side_effect=replace):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload), errno.ELOOP)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.target.resolve(), private)
        self.assertEqual(private.read_bytes(), b"protected source content")
        self.assertFalse(self._stages())

    def test_first_postpublication_stat_failure_removes_original(self):
        original = os.lstat
        calls = 0
        def fail_once(path, *args, **kwargs):
            nonlocal calls
            if str(path) == str(self.target) and self.target.exists():
                calls += 1
                if calls == 1:
                    raise OSError(errno.EACCES, SENSITIVE, str(path))
            return original(path, *args, **kwargs)
        with patch.object(vault.os, "lstat", side_effect=fail_once):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload), errno.EACCES)
        self.assertGreaterEqual(calls, 2)
        self.assertFalse(self.target.exists())
        self.assertFalse(self._stages())

    def test_first_postpublication_stat_interrupt_rolls_back(self):
        original = os.lstat
        calls = 0
        def interrupt(path, *args, **kwargs):
            nonlocal calls
            if str(path) == str(self.target) and self.target.exists():
                calls += 1
                if calls == 1:
                    raise KeyboardInterrupt()
            return original(path, *args, **kwargs)
        with patch.object(vault.os, "lstat", side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                vault.publish_vault(self.target, self.payload)
        self.assertGreaterEqual(calls, 2)
        self.assertFalse(self.target.exists())
        self.assertFalse(self._stages())

    def test_first_stat_fails_with_missing_target_after_link(self):
        original = os.lstat
        calls = 0
        def vanished(path, *args, **kwargs):
            nonlocal calls
            if str(path) == str(self.target) and self.target.exists():
                calls += 1
                if calls == 1:
                    os.unlink(path)
                    raise FileNotFoundError(errno.ENOENT, SENSITIVE, str(path))
            return original(path, *args, **kwargs)
        with patch.object(vault.os, "lstat", side_effect=vanished):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload), errno.ENOENT)
        self.assertEqual(calls, 1)
        self.assertFalse(self.target.exists())
        self.assertFalse(self._stages())

    @unittest.skipIf(os.name == "nt", "POSIX source-stage swap fixture")
    def test_linked_prepublication_stage_replacement_removed(self):
        original = os.link
        replacement_contents = b"source hijacked by a writer"
        remaining = []
        def swap_source(source, destination, *args, **kwargs):
            new = Path(str(source) + ".alien")
            new.write_bytes(replacement_contents)
            os.replace(new, source)
            remaining.append(Path(source))
            return original(source, destination, *args, **kwargs)
        with patch.object(vault.os, "link", side_effect=swap_source):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.target.exists(), "remove the link made to a replaced source")
        self.assertEqual(remaining[0].read_bytes(), replacement_contents)

    @unittest.skipIf(os.name == "nt", "POSIX source-stage swap fixture")
    def test_linked_prepublication_stage_symlink_removed(self):
        original = os.link
        protected = self.directory / "private-policy.txt"
        protected.write_bytes(b"do not change")
        def swap_source(source, destination, *args, **kwargs):
            new = Path(str(source) + ".other")
            new.symlink_to(protected)
            os.replace(new, source)
            return original(source, destination, *args, **kwargs)
        with patch.object(vault.os, "link", side_effect=swap_source):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload), errno.ELOOP)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(protected.read_bytes(), b"do not change")

    def test_postpublication_verify_fails_for_owned_file_rollback(self):
        with patch.object(vault, "_verify_published_bytes", side_effect=OSError(errno.EIO, SENSITIVE, str(self.target))):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.target.exists())
        self.assertFalse(self._stages())

    def test_postpublication_verify_interrupt_owned_file_rollback(self):
        with patch.object(vault, "_verify_published_bytes", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                vault.publish_vault(self.target, self.payload)
        self.assertFalse(self.target.exists())
        self.assertFalse(self._stages())

    def test_postpublication_target_replaced_during_verification_preserved(self):
        alien = b"someone else's records"
        def fail(*args):
            self.target.unlink()
            self.target.write_bytes(alien)
            raise OSError(errno.EIO, SENSITIVE, str(self.target))
        with patch.object(vault, "_verify_published_bytes", side_effect=fail):
            self._assert_redacted(lambda: vault.publish_vault(self.target, self.payload))
        self.assertEqual(self.target.read_bytes(), alien)
        self.assertFalse(self._stages())

    def test_external_original_destination_never_overwritten(self):
        self.target.write_bytes(b"do not overwrite")
        with self.assertRaises(FileExistsError):
            vault.publish_vault(self.target, self.payload)
        self.assertEqual(self.target.read_bytes(), b"do not overwrite")
        self.assertFalse(self._stages())

    def test_rejects_wrong_payload_type_without_file_touch(self):
        for invalid in (bytearray(b"bytes"), "not bytes", None, True):
            with self.subTest(payload_type=type(invalid).__name__):
                with self.assertRaises(ValueError):
                    vault.publish_vault(self.target, invalid)
            self.assertFalse(self.target.exists())
            self.assertFalse(self._stages())


if __name__ == "__main__":
    unittest.main()
