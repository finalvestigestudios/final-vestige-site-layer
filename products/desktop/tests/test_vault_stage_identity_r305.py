"""R305: staged ciphertext pathname identity and fail-closed cleanup custody."""
from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import vault_publish as vault

SECRET = 'SYNTHETIC-PRIVATE-AUDIT-PATH-R305'


class VaultStageIdentityR305(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='fvs-r305-')
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.out = self.folder / f'{SECRET}.fvault'
        self.payload = bytes(range(256)) * 1029

    def stages(self):
        return list(self.folder.glob('.fvs-vault-*.partial'))

    def redacted(self, func, code=errno.EIO):
        with self.assertRaises(OSError) as cm:
            func()
        self.assertEqual(cm.exception.errno, code)
        self.assertIsNone(cm.exception.__context__)
        self.assertIsNone(cm.exception.__cause__)
        self.assertIsNone(cm.exception.filename)
        self.assertNotIn(SECRET, repr(cm.exception))
        self.assertFalse(self.out.exists())

    def test_exact_multi_block_ciphertext_passes(self):
        self.assertEqual(vault.publish_vault(self.out, self.payload), self.out)
        self.assertEqual(self.out.read_bytes(), self.payload)
        self.assertFalse(self.stages())

    def test_empty_bytes_legacy_contract(self):
        vault.publish_vault(self.out, b'')
        self.assertEqual(self.out.read_bytes(), b'')
        self.assertFalse(self.stages())

    def test_failed_fsync_preserves_no_stages(self):
        with patch.object(vault.os, 'fsync', side_effect=OSError(errno.ENOSPC, SECRET, str(self.out))):
            self.redacted(lambda: vault.publish_vault(self.out, self.payload), errno.ENOSPC)
        self.assertFalse(self.stages())

    def test_nonempty_original_destination_not_overwritten(self):
        self.out.write_bytes(b'original')
        with self.assertRaises(FileExistsError):
            vault.publish_vault(self.out, self.payload)
        self.assertEqual(self.out.read_bytes(), b'original')
        self.assertFalse(self.stages())

    def test_stage_name_swapped_to_other_regular_file_not_published_or_deleted(self):
        original = os.close
        replacement = b'other-private-file'
        moved = self.folder / 'held-original.bin'
        staged = []
        def swap(fd):
            path = self.stages()
            if path and not staged:
                staged.extend(path)
                os.rename(path[0], moved)
                path[0].write_bytes(replacement)
            return original(fd)
        with patch.object(vault.os, 'close', side_effect=swap):
            self.redacted(lambda: vault.publish_vault(self.out, self.payload))
        self.assertEqual(staged[0].read_bytes(), replacement, 'never delete an unrelated replacement')
        self.assertEqual(moved.read_bytes(), self.payload)

    def test_staged_name_swapped_to_symlink_not_published_or_deleted(self):
        moved = self.folder / 'held.bin'
        protected = self.folder / 'protected.txt'
        protected.write_bytes(b'protected')
        staged = []
        original = os.close
        def swap(fd):
            matches = self.stages()
            if matches and not staged:
                staged.extend(matches)
                os.rename(matches[0], moved)
                try:
                    matches[0].symlink_to(protected)
                except (OSError, NotImplementedError):
                    # Windows runner accounts may lack symlink privilege.
                    # Exercise the path-replacement invariant without a skip.
                    matches[0].write_bytes(b'replacement')
            return original(fd)
        with patch.object(vault.os, 'close', side_effect=swap):
            self.redacted(lambda: vault.publish_vault(self.out, self.payload))
        if staged[0].is_symlink():
            self.assertEqual(staged[0].resolve(), protected)
        else:
            self.assertEqual(staged[0].read_bytes(), b'replacement')
        self.assertEqual(protected.read_bytes(), b'protected')
        self.assertEqual(moved.read_bytes(), self.payload)

    def test_staged_name_deleted_before_publish_is_not_recreated(self):
        original = os.close
        def delete(fd):
            for path in self.stages():
                os.unlink(path)
            return original(fd)
        with patch.object(vault.os, 'close', side_effect=delete):
            self.redacted(lambda: vault.publish_vault(self.out, self.payload))
        self.assertFalse(self.stages())

    def test_hardlink_count_prepublication_rejected(self):
        # Simulate st_nlink=2 without requiring hardlink privileges on Windows.
        original = os.lstat
        seen = 0
        def linked(path):
            nonlocal seen
            result = original(path)
            if '.fvs-vault-' in str(path):
                seen += 1
                if seen > 1:
                    class Fake:
                        st_mode = result.st_mode
                        st_dev = result.st_dev
                        st_ino = result.st_ino
                        st_nlink = 2
                        st_size = result.st_size
                    return Fake()
            return result
        with patch.object(vault.os, 'lstat', side_effect=linked):
            self.redacted(lambda: vault.publish_vault(self.out, self.payload))
        self.assertFalse(self.stages())

    def test_descriptor_identity_mismatch_rejected_before_link(self):
        original = os.fstat
        calls = 0
        def mismatch(fd):
            nonlocal calls
            calls += 1
            observed = original(fd)
            if calls == 2:
                class Fake:
                    st_mode = observed.st_mode
                    st_dev = observed.st_dev
                    st_ino = observed.st_ino + 1
                return Fake()
            return observed
        with patch.object(vault.os, 'fstat', side_effect=mismatch):
            self.redacted(lambda: vault.publish_vault(self.out, self.payload))
        self.assertFalse(self.stages())

    def test_invalid_staging_inode_is_rejected(self):
        original = os.lstat
        def zero_inode(path):
            result = original(path)
            if '.fvs-vault-' in str(path):
                class Fake:
                    st_mode = result.st_mode
                    st_dev = result.st_dev
                    st_ino = 0
                    st_nlink = 1
                return Fake()
            return result
        with patch.object(vault.os, 'lstat', side_effect=zero_inode):
            self.redacted(lambda: vault.publish_vault(self.out, self.payload))
        # Identity could not be established; an untrusted stage is intentionally not unlinked.

    def test_oserror_on_staging_preflight_redacted(self):
        original = os.lstat
        def forbidden(path):
            if '.fvs-vault-' in str(path):
                raise OSError(errno.EACCES, SECRET, str(path))
            return original(path)
        with patch.object(vault.os, 'lstat', side_effect=forbidden):
            self.redacted(lambda: vault.publish_vault(self.out, self.payload), errno.EACCES)

    def test_interruption_closes_descriptor_and_unlinks_owned_temp(self):
        with patch.object(vault.os, 'fsync', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                vault.publish_vault(self.out, self.payload)
        self.assertFalse(self.out.exists())
        self.assertFalse(self.stages())

    def test_collision_after_validation_never_overwrites(self):
        step = 'rename' if os.name == 'nt' else 'link'
        def collide(a, b):
            Path(b).write_bytes(b'other-writer')
            raise FileExistsError(errno.EEXIST, SECRET, str(b))
        with patch.object(vault.os, step, side_effect=collide):
            with self.assertRaises(FileExistsError) as cm:
                vault.publish_vault(self.out, self.payload)
        self.assertIsNone(cm.exception.__context__)
        self.assertEqual(self.out.read_bytes(), b'other-writer')
        self.assertFalse(self.stages())

    def test_short_read_still_succeeds(self):
        data = b'cryptotext' * 15
        original = os.read
        with patch.object(vault.os, 'read', side_effect=lambda fd, count: original(fd, min(count, 2))):
            vault.publish_vault(self.out, data)
        self.assertEqual(self.out.read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
