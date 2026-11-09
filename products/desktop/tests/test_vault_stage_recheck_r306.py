"""R306: closed-stage in-place mutation regression for private vault publication.

These tests use only synthetic ciphertext and local temporary directories.
"""
from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import vault_publish as vault

PRIVATE = "SYNTHETIC-PRIVATE-VAULT-R306"


class VaultStageRecheckR306(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r306-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.target = self.folder / (PRIVATE + ".fvault")
        self.payload = bytes(range(256)) * 2049

    def stages(self):
        return list(self.folder.glob(".fvs-vault-*.partial"))

    def assert_rejects_without_leaking(self, action, error=errno.EIO):
        with self.assertRaises(OSError) as caught:
            action()
        self.assertEqual(caught.exception.errno, error)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(PRIVATE, repr(caught.exception))
        self.assertFalse(self.target.exists())

    def mutate_after_initial_close(self, content):
        real_close = os.close
        changed = [False]
        def close(fd):
            if not changed[0] and self.stages():
                changed[0] = True
                self.stages()[0].write_bytes(content)
            return real_close(fd)
        return close

    def test_publishes_unchanged_multiblock_bytes(self):
        self.assertEqual(vault.publish_vault(self.target, self.payload), self.target)
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertFalse(self.stages())

    def test_publishes_empty_ciphertext_legacy_contract(self):
        self.assertEqual(vault.publish_vault(self.target, b""), self.target)
        self.assertEqual(self.target.read_bytes(), b"")
        self.assertFalse(self.stages())

    def test_detects_same_inode_same_length_corruption_after_close(self):
        mutated = bytes([self.payload[0] ^ 1]) + self.payload[1:]
        with patch.object(vault.os, "close", side_effect=self.mutate_after_initial_close(mutated)):
            self.assert_rejects_without_leaking(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.stages())

    def test_detects_last_byte_corruption_after_close(self):
        mutated = self.payload[:-1] + bytes([self.payload[-1] ^ 1])
        with patch.object(vault.os, "close", side_effect=self.mutate_after_initial_close(mutated)):
            self.assert_rejects_without_leaking(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.stages())

    def test_detects_same_length_rewrite_even_with_utime_reset(self):
        real_close = os.close
        done = [False]
        def mutate(fd):
            if not done[0] and self.stages():
                done[0] = True
                stage = self.stages()[0]
                old = stage.stat()
                stage.write_bytes(b"X" * len(self.payload))
                os.utime(stage, ns=(old.st_atime_ns, old.st_mtime_ns))
            return real_close(fd)
        with patch.object(vault.os, "close", side_effect=mutate):
            self.assert_rejects_without_leaking(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.stages())

    def test_short_reads_on_both_verification_passes_accepted(self):
        original = os.read
        with patch.object(vault.os, "read", side_effect=lambda fd, count: original(fd, min(count, 97))):
            vault.publish_vault(self.target, self.payload[:2048])
        self.assertEqual(self.target.read_bytes(), self.payload[:2048])

    def test_mutation_to_longer_content_rejected(self):
        with patch.object(vault.os, "close", side_effect=self.mutate_after_initial_close(self.payload + b"X")):
            self.assert_rejects_without_leaking(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.stages())

    def test_mutation_to_shorter_content_rejected(self):
        with patch.object(vault.os, "close", side_effect=self.mutate_after_initial_close(self.payload[:-1])):
            self.assert_rejects_without_leaking(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.stages())

    def test_reopen_permission_error_is_redacted(self):
        real_open = os.open
        def failed_open(path, flags, *args, **kwargs):
            if ".fvs-vault-" in str(path):
                raise OSError(errno.EACCES, PRIVATE, str(path))
            return real_open(path, flags, *args, **kwargs)
        with patch.object(vault.os, "open", side_effect=failed_open):
            self.assert_rejects_without_leaking(lambda: vault.publish_vault(self.target, self.payload), errno.EACCES)
        self.assertFalse(self.stages())

    def test_recheck_read_error_is_redacted(self):
        original = vault._recheck_staged_bytes
        def injected(*args):
            with patch.object(vault.os, "read", side_effect=OSError(errno.EIO, PRIVATE, str(self.target))):
                original(*args)
        with patch.object(vault, "_recheck_staged_bytes", side_effect=injected):
            self.assert_rejects_without_leaking(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.stages())

    def test_recheck_premature_eof_rejected(self):
        original = vault._recheck_staged_bytes
        def injected(*args):
            with patch.object(vault.os, "read", return_value=b""):
                original(*args)
        with patch.object(vault, "_recheck_staged_bytes", side_effect=injected):
            self.assert_rejects_without_leaking(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.stages())

    def test_recheck_rejects_incorrect_bytes_even_when_metadata_unchanged(self):
        original = vault._recheck_staged_bytes
        def injected(*args):
            with patch.object(vault.os, "read", return_value=b"?" * vault._BLOCK):
                original(*args)
        with patch.object(vault, "_recheck_staged_bytes", side_effect=injected):
            self.assert_rejects_without_leaking(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.stages())

    def test_recheck_open_preserves_no_follow_when_supported(self):
        actual_open = os.open
        observed = []
        def watch(path, flags, *args, **kwargs):
            if ".fvs-vault-" in str(path) and not (flags & os.O_CREAT):
                observed.append(flags)
            return actual_open(path, flags, *args, **kwargs)
        with patch.object(vault.os, "open", side_effect=watch):
            vault.publish_vault(self.target, b"hello")
        self.assertEqual(len(observed), 1)
        if hasattr(os, "O_NOFOLLOW"):
            self.assertTrue(observed[0] & os.O_NOFOLLOW)
        if hasattr(os, "O_BINARY"):
            self.assertTrue(observed[0] & os.O_BINARY)

    def test_collision_preserves_existing_destination(self):
        self.target.write_bytes(b"already-here")
        with self.assertRaises(FileExistsError):
            vault.publish_vault(self.target, self.payload)
        self.assertEqual(self.target.read_bytes(), b"already-here")
        self.assertFalse(self.stages())

    def test_interruption_during_recheck_is_not_swallowed(self):
        original = vault._recheck_staged_bytes
        def injected(*args):
            with patch.object(vault.os, "read", side_effect=KeyboardInterrupt):
                original(*args)
        with patch.object(vault, "_recheck_staged_bytes", side_effect=injected):
            with self.assertRaises(KeyboardInterrupt):
                vault.publish_vault(self.target, self.payload)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.stages())

    def test_nonbytes_payload_rejected_without_disk_write(self):
        with self.assertRaises(ValueError):
            vault.publish_vault(self.target, bytearray(b"secret"))
        self.assertFalse(self.stages())

    def test_oversized_payload_rejected_without_disk_write(self):
        with self.assertRaises(ValueError):
            vault.publish_vault(self.target, b"X" * (vault.MAX_VAULT_PUBLICATION_BYTES + 1))
        self.assertFalse(self.stages())


if __name__ == "__main__":
    unittest.main()
