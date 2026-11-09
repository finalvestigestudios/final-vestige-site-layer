"""R304: short-read-tolerant and fail-closed encrypted vault staging verification."""
from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import vault_publish as vault

PRIVATE = "SYNTHETIC-PRIVATE-REPORT-41112"


class VaultReadR304(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="r304-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.out = self.folder / (PRIVATE + ".fvault")
        self.payload = bytes(range(256)) * 2049

    def assert_clean(self, expected_errno=errno.EIO):
        self.assertFalse(self.out.exists())
        self.assertEqual(list(self.folder.glob(".fvs-vault-*.partial")), [])

    def assert_redacted_error(self, operation, number=errno.EIO):
        with self.assertRaises(OSError) as cm:
            operation()
        caught = cm.exception
        self.assertEqual(caught.errno, number)
        self.assertIsNone(caught.__context__)
        self.assertIsNone(caught.__cause__)
        self.assertIsNone(caught.filename)
        self.assertNotIn(PRIVATE, repr(caught))
        self.assert_clean()

    def test_actual_file_multi_block_readback(self):
        self.assertEqual(vault.publish_vault(self.out, self.payload), self.out)
        self.assertEqual(self.out.read_bytes(), self.payload)

    def test_one_byte_at_a_time_readback(self):
        # Use small ciphertext to keep the deliberately tiny read test quick.
        data = b"genuine-ciphertext-bytes" * 4
        original = os.read
        with patch.object(vault.os, "read", side_effect=lambda fd, n: original(fd, min(n, 1))):
            vault.publish_vault(self.out, data)
        self.assertEqual(self.out.read_bytes(), data)

    def test_seven_byte_short_readback(self):
        original = os.read
        with patch.object(vault.os, "read", side_effect=lambda fd, n: original(fd, min(n, 7))):
            vault.publish_vault(self.out, self.payload)
        self.assertEqual(self.out.read_bytes(), self.payload)

    def test_short_reads_cross_verification_block_boundary(self):
        data = (b"\x00\xffFVS" * (vault._BLOCK // 5 + 11))
        original = os.read
        def uneven(fd, n):
            return original(fd, min(n, 8191))
        with patch.object(vault.os, "read", side_effect=uneven):
            vault.publish_vault(self.out, data)
        self.assertEqual(self.out.read_bytes(), data)

    def test_empty_ciphertext_preserves_existing_behavior(self):
        vault.publish_vault(self.out, b"")
        self.assertEqual(self.out.read_bytes(), b"")

    def test_premature_eof_rejected_before_publication(self):
        original = os.read
        calls = 0
        def early_eof(fd, n):
            nonlocal calls
            calls += 1
            return b"" if calls == 2 else original(fd, min(n, 3))
        with patch.object(vault.os, "read", side_effect=early_eof):
            self.assert_redacted_error(lambda: vault.publish_vault(self.out, self.payload))

    def test_zero_bytes_immediately_rejected(self):
        with patch.object(vault.os, "read", return_value=b""):
            self.assert_redacted_error(lambda: vault.publish_vault(self.out, self.payload))

    def test_non_bytes_read_rejected(self):
        for unexpected in (None, "unsafe", bytearray(b"x"), memoryview(b"x"), True, 1):
            with self.subTest(kind=type(unexpected).__name__):
                with patch.object(vault.os, "read", return_value=unexpected):
                    self.assert_redacted_error(lambda: vault.publish_vault(self.out, self.payload))

    def test_overlong_read_rejected(self):
        def overlong(fd, n):
            return b"!" * (n + 1)
        with patch.object(vault.os, "read", side_effect=overlong):
            self.assert_redacted_error(lambda: vault.publish_vault(self.out, self.payload))

    def test_short_read_then_one_byte_corruption_rejected(self):
        original = os.read
        calls = 0
        def corrupt(fd, n):
            nonlocal calls
            calls += 1
            result = original(fd, min(n, 31))
            if calls == 3 and result:
                return b"!" + result[1:]
            return result
        with patch.object(vault.os, "read", side_effect=corrupt):
            self.assert_redacted_error(lambda: vault.publish_vault(self.out, self.payload))

    def test_short_read_then_oserror_private_chain_sanitized(self):
        original = os.read
        calls = 0
        def fail(fd, n):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError(errno.EACCES, PRIVATE, str(self.out))
            return original(fd, min(n, 3))
        with patch.object(vault.os, "read", side_effect=fail):
            self.assert_redacted_error(lambda: vault.publish_vault(self.out, self.payload), errno.EACCES)

    def test_interrupt_during_partial_read_cleans_stage(self):
        original = os.read
        calls = 0
        def interrupted(fd, n):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt()
            return original(fd, min(n, 3))
        with patch.object(vault.os, "read", side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt):
                vault.publish_vault(self.out, self.payload)
        self.assert_clean()

    def test_existing_destination_is_never_overwritten(self):
        self.out.write_bytes(b"owner")
        with self.assertRaises(FileExistsError):
            vault.publish_vault(self.out, self.payload)
        self.assertEqual(self.out.read_bytes(), b"owner")
        self.assertEqual(list(self.folder.glob(".fvs-vault-*.partial")), [])

    def test_late_destination_collision_is_preserved(self):
        step = "rename" if os.name == "nt" else "link"
        def collision(source, destination):
            Path(destination).write_bytes(b"rival")
            raise FileExistsError(errno.EEXIST, PRIVATE, str(destination))
        with patch.object(vault.os, step, side_effect=collision):
            with self.assertRaises(FileExistsError) as cm:
                vault.publish_vault(self.out, self.payload)
        self.assertIsNone(cm.exception.__context__)
        self.assertEqual(self.out.read_bytes(), b"rival")
        self.assertEqual(list(self.folder.glob(".fvs-vault-*.partial")), [])

    def test_fsync_still_precedes_publish(self):
        original = os.fsync
        observations = []
        def check(fd):
            observations.append(self.out.exists())
            original(fd)
        with patch.object(vault.os, "fsync", side_effect=check):
            vault.publish_vault(self.out, b"exact")
        self.assertEqual(observations, [False])
        self.assertEqual(self.out.read_bytes(), b"exact")


if __name__ == "__main__":
    unittest.main()
