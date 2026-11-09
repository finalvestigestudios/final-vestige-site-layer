"""R307 synthetic postpublication custody checks for both premium vault products.

No real customer files, telemetry, network access or released binaries.
"""
from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import vault_publish as vault

PRIVATE = 'SYNTHETIC-PRIVATE-FINANCE-R307'


class PublishedVaultCustodyR307(unittest.TestCase):
    def setUp(self):
        root = tempfile.TemporaryDirectory(prefix='labs-r307-')
        self.addCleanup(root.cleanup)
        self.dir = Path(root.name)
        self.target = self.dir / (PRIVATE + '.fvault')
        self.payload = bytes(range(256)) * 1031

    def stages(self):
        return list(self.dir.glob('.fvs-vault-*.partial'))

    def assert_safe_error(self, call, code=errno.EIO):
        with self.assertRaises(OSError) as observed:
            call()
        error = observed.exception
        self.assertEqual(error.errno, code)
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn(PRIVATE, repr(error))
        return error

    def _stage_swap(self, contents=None, *, symlink_target=None):
        real_link = os.link
        def swap(source, target, *args, **kwargs):
            stage = Path(source)
            # Create the replacement BEFORE replacing the owned stage to
            # prevent immediate inode reuse from obscuring the swap.
            replacement = stage.with_suffix('.attacker')
            if symlink_target is not None:
                replacement.symlink_to(symlink_target)
            else:
                replacement.write_bytes(contents)
            os.replace(replacement, stage)
            return real_link(source, target, *args, **kwargs)
        return swap

    def test_normal_multiblock_payload_is_identical(self):
        self.assertEqual(vault.publish_vault(self.target, self.payload), self.target)
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertEqual(self.stages(), [])

    def test_empty_ciphertext_keeps_existing_legacy_contract(self):
        vault.publish_vault(self.target, b'')
        self.assertEqual(self.target.read_bytes(), b'')
        self.assertFalse(self.stages())

    @unittest.skipIf(os.name == 'nt', 'POSIX hardlink race fixture')
    def test_rejects_stage_swap_to_different_inode_same_length(self):
        changed = bytes([self.payload[0] ^ 1]) + self.payload[1:]
        with patch.object(vault.os, 'link', side_effect=self._stage_swap(changed)):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.target.exists())
        self.assertEqual(self.stages()[0].read_bytes(), changed)

    @unittest.skipIf(os.name == 'nt', 'POSIX hardlink race fixture')
    def test_rejects_stage_swap_even_if_bytes_match(self):
        with patch.object(vault.os, 'link', side_effect=self._stage_swap(self.payload)):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.target.exists())

    @unittest.skipIf(os.name == 'nt', 'POSIX hardlink race fixture')
    def test_symlink_swap_does_not_leave_published_symlink(self):
        secret = self.dir / PRIVATE
        secret.write_bytes(b'EXTERNAL-PRIVATE-FILE')
        with patch.object(vault.os, 'link', side_effect=self._stage_swap(symlink_target=secret)):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, self.payload), errno.ELOOP)
        self.assertFalse(self.target.is_symlink())
        self.assertFalse(self.target.exists())
        self.assertEqual(secret.read_bytes(), b'EXTERNAL-PRIVATE-FILE')

    @unittest.skipIf(os.name == 'nt', 'POSIX hardlink race fixture')
    def test_rejects_swap_with_extra_bytes(self):
        with patch.object(vault.os, 'link', side_effect=self._stage_swap(self.payload+b'X')):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.target.exists())

    def test_final_read_supports_legitimate_short_reads(self):
        real_verify = vault._verify_published_bytes
        real_read = os.read
        def short_read_verify(*args):
            with patch.object(vault.os, 'read', side_effect=lambda fd, count: real_read(fd, min(101, count))):
                return real_verify(*args)
        with patch.object(vault, '_verify_published_bytes', side_effect=short_read_verify):
            vault.publish_vault(self.target, self.payload[:2049])
        self.assertEqual(self.target.read_bytes(), self.payload[:2049])

    def test_final_read_corruption_is_rejected_and_rolled_back(self):
        real_verify = vault._verify_published_bytes
        def unreadable(*args):
            with patch.object(vault.os, 'read', return_value=b'?' * vault._BLOCK):
                return real_verify(*args)
        with patch.object(vault, '_verify_published_bytes', side_effect=unreadable):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.target.exists())
        self.assertFalse(self.stages())

    def test_final_read_premature_eof_is_rejected_and_rolled_back(self):
        real_verify = vault._verify_published_bytes
        def fail(*args):
            with patch.object(vault.os, 'read', return_value=b''):
                return real_verify(*args)
        with patch.object(vault, '_verify_published_bytes', side_effect=fail):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, self.payload))
        self.assertFalse(self.target.exists())

    def test_final_open_oserror_does_not_retain_sensitive_path(self):
        real_open = os.open
        def deny(path, flags, *args, **kwargs):
            if str(path) == str(self.target):
                raise OSError(errno.EACCES, PRIVATE, PRIVATE)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(vault.os, 'open', side_effect=deny):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, b'XYZ'), errno.EACCES)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.stages())

    def test_final_read_oserror_does_not_retain_sensitive_path(self):
        real_verify = vault._verify_published_bytes
        def fail(*args):
            with patch.object(vault.os, 'read', side_effect=OSError(errno.EIO, PRIVATE, PRIVATE)):
                return real_verify(*args)
        with patch.object(vault, '_verify_published_bytes', side_effect=fail):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, b'XYZ'))
        self.assertFalse(self.target.exists())

    def test_interruption_after_link_cleans_created_name(self):
        with patch.object(vault, '_verify_published_bytes', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                vault.publish_vault(self.target, self.payload)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.stages())

    def test_does_not_erase_unrelated_replacement_during_rollback(self):
        def replace(*args):
            self.target.unlink()
            self.target.write_bytes(b'unrelated-data')
            raise OSError(errno.EIO, PRIVATE, PRIVATE)
        with patch.object(vault, '_verify_published_bytes', side_effect=replace):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, self.payload))
        self.assertEqual(self.target.read_bytes(), b'unrelated-data')
        self.assertFalse(self.stages())

    def test_no_clobber_if_another_writer_wins_link_race(self):
        if os.name == 'nt':
            self.skipTest('POSIX hardlink race fixture')
        actual = os.link
        def collision(src, dst):
            Path(dst).write_bytes(b'other-user')
            return actual(src, dst)
        with patch.object(vault.os, 'link', side_effect=collision):
            self.assert_safe_error(lambda: vault.publish_vault(self.target, self.payload), None)
        self.assertEqual(self.target.read_bytes(), b'other-user')
        self.assertFalse(self.stages())

    def test_existing_final_archive_remains_unchanged(self):
        self.target.write_bytes(b'existing')
        with self.assertRaises(FileExistsError):
            vault.publish_vault(self.target, self.payload)
        self.assertEqual(self.target.read_bytes(), b'existing')
        self.assertFalse(self.stages())

    def test_postpublication_final_open_uses_nofollow_and_binary_flags(self):
        real_open = os.open
        observed = []
        def spy(path, flags, *args, **kwargs):
            if str(path) == str(self.target):
                observed.append(flags)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(vault.os, 'open', side_effect=spy):
            vault.publish_vault(self.target, b'123')
        self.assertEqual(len(observed), 1)
        if hasattr(os, 'O_NOFOLLOW'):
            self.assertTrue(observed[0] & os.O_NOFOLLOW)
        if hasattr(os, 'O_BINARY'):
            self.assertTrue(observed[0] & os.O_BINARY)


if __name__ == '__main__':
    unittest.main()
