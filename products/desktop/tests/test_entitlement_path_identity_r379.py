"""R379: prove issued-license filename cannot silently diverge from the read FD.

All data is synthetic. No private keys, payment records, network or production paths.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import issued_entitlement_guard as guard

PRIVATE = "/PRIVATE/FINANCIAL-FILES/SCANNED-LICENSE.fvslicense"


class PublicError(ValueError):
    pass


class EntitlementPathIdentityR379Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / 'issued.fvslicense'
        self.target.write_bytes(b'original signed entitlement')
        self.unrelated = self.root / 'operator-private.bin'
        self.unrelated.write_bytes(b'synthetic private unrelated evidence')

    def fingerprint(self):
        return guard.fingerprint_issued_entitlement(self.target, 8192, PublicError)

    def assert_public_failure(self, fragment):
        with self.assertRaises(PublicError) as caught:
            self.fingerprint()
        self.assertIn(fragment, str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(PRIVATE, repr(caught.exception))

    def test_unmodified_regular_file_preserves_deterministic_digest(self):
        original = self.target.read_bytes()
        self.assertEqual(self.fingerprint(), hashlib.sha256(original).hexdigest())
        self.assertEqual(self.target.read_bytes(), original)

    def test_target_replaced_between_validation_and_fd_open_is_rejected_before_read(self):
        real_open = os.open
        original = self.target.read_bytes()
        unrelated = self.unrelated.read_bytes()
        opened = []
        def replace_before_open(path, flags, *args, **kwargs):
            opened.append(True)
            os.replace(self.unrelated, self.target)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(guard.os, 'open', side_effect=replace_before_open), \
             patch.object(guard.os, 'read', side_effect=AssertionError('must not read swapped FD')) as reader:
            self.assert_public_failure('changed')
        self.assertEqual(len(opened), 1)
        reader.assert_not_called()
        self.assertEqual(self.target.read_bytes(), unrelated)
        self.assertNotEqual(original, unrelated)

    def test_target_replaced_with_identical_bytes_still_fails_identity_check(self):
        self.unrelated.write_bytes(self.target.read_bytes())
        real_open = os.open
        def swap(path, flags, *args, **kwargs):
            os.replace(self.unrelated, self.target)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(guard.os, 'open', side_effect=swap):
            self.assert_public_failure('changed')

    def test_target_replaced_after_read_but_before_return_is_rejected(self):
        real_read = os.read
        original = self.target.read_bytes()
        unrelated = self.unrelated.read_bytes()
        swapped = False
        def swap_after_read(fd, count):
            nonlocal swapped
            block = real_read(fd, count)
            if block and not swapped:
                os.replace(self.unrelated, self.target)
                swapped = True
            return block
        with patch.object(guard.os, 'read', side_effect=swap_after_read):
            self.assert_public_failure('changed')
        self.assertTrue(swapped)
        self.assertEqual(self.target.read_bytes(), unrelated)
        self.assertNotEqual(original, unrelated)

    def test_target_unlinked_after_read_is_not_successfully_fingerprinted(self):
        real_read = os.read
        unlinked = False
        def unlink_after_read(fd, count):
            nonlocal unlinked
            block = real_read(fd, count)
            if block and not unlinked:
                self.target.unlink()
                unlinked = True
            return block
        with patch.object(guard.os, 'read', side_effect=unlink_after_read):
            self.assert_public_failure('Cannot read')
        self.assertTrue(unlinked)
        self.assertFalse(self.target.exists())

    def test_preopen_lstat_private_error_is_sanitized(self):
        with patch.object(guard.os, 'lstat', side_effect=PermissionError(PRIVATE)):
            self.assert_public_failure('Cannot read')
        self.assertEqual(self.target.read_bytes(), b'original signed entitlement')

    def test_postread_lstat_private_error_is_sanitized(self):
        real_lstat = os.lstat
        count = 0
        def error_second(path, *args, **kwargs):
            nonlocal count
            count += 1
            if count == 2:
                raise PermissionError(PRIVATE)
            return real_lstat(path, *args, **kwargs)
        with patch.object(guard.os, 'lstat', side_effect=error_second):
            self.assert_public_failure('Cannot read')
        self.assertEqual(count, 2)

    def test_reparse_attribute_rejects_entry_before_open(self):
        real_lstat = os.lstat
        def synthesize_reparse(path, *args, **kwargs):
            actual = real_lstat(path, *args, **kwargs)
            return SimpleNamespace(**{name: getattr(actual, name) for name in (
                'st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns')},
                st_file_attributes=0x400)
        with patch.object(guard.os, 'lstat', side_effect=synthesize_reparse), \
             patch.object(guard.os, 'open', side_effect=AssertionError('must not follow reparse')) as opened:
            self.assert_public_failure('regular file')
        opened.assert_not_called()

    def test_reparse_attribute_appearing_after_read_fails_closed(self):
        real_lstat = os.lstat
        count = 0
        def second_reparse(path, *args, **kwargs):
            nonlocal count
            count += 1
            actual = real_lstat(path, *args, **kwargs)
            if count == 2:
                return SimpleNamespace(**{name: getattr(actual, name) for name in (
                    'st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns')},
                    st_file_attributes=0x400)
            return actual
        with patch.object(guard.os, 'lstat', side_effect=second_reparse):
            self.assert_public_failure('changed')
        self.assertEqual(count, 2)

    def test_preopen_multilink_rejected_without_descriptor_open(self):
        alias = self.root / 'hardlink.fvslicense'
        try:
            os.link(self.target, alias)
        except (OSError, NotImplementedError):
            self.skipTest('hardlinks unavailable')
        with patch.object(guard.os, 'open', side_effect=AssertionError('must not open alias')) as opened:
            self.assert_public_failure('single-link')
        opened.assert_not_called()

    def test_fstat_metadata_mismatch_vs_initial_path_is_rejected_before_read(self):
        real_fstat = os.fstat
        def forged_fd_metadata(fd):
            actual = real_fstat(fd)
            data = {name: getattr(actual, name) for name in (
                'st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns')}
            data['st_ino'] += 1
            return SimpleNamespace(**data)
        with patch.object(guard.os, 'fstat', side_effect=forged_fd_metadata), \
             patch.object(guard.os, 'read', side_effect=AssertionError('must not read')) as reader:
            self.assert_public_failure('changed')
        reader.assert_not_called()


if __name__ == '__main__':
    unittest.main()
