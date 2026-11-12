"""R378: premium entitlement fingerprint bytes, alias and FD custody."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import issued_entitlement_guard as guard


PRIVATE = "/PRIVATE/CLIENT-BILLING-R378/SECRET.fvslicense"


class PublicError(ValueError):
    pass


class IssuedEntitlementGuardR378Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / "signed.fvslicense"

    def fingerprint(self):
        return guard.fingerprint_issued_entitlement(self.target, 8192, PublicError)

    def check_error(self, caught, fragment):
        err = caught.exception
        self.assertIs(type(err), PublicError)
        self.assertIn(fragment, str(err))
        self.assertIsNone(err.__context__)
        self.assertIsNone(err.__cause__)
        self.assertNotIn(PRIVATE, repr(err))

    def test_exact_signed_bytes_have_stable_sha256(self):
        data = b'{"synthetic":true,"holder":"test-only"}\n'
        self.target.write_bytes(data)
        self.assertEqual(self.fingerprint(), hashlib.sha256(data).hexdigest())
        self.assertEqual(self.target.read_bytes(), data)

    def test_maximum_length_file_is_accepted(self):
        self.target.write_bytes(b"a" * 8192)
        self.assertEqual(self.fingerprint(), hashlib.sha256(b"a" * 8192).hexdigest())

    def test_empty_file_is_rejected_without_modification(self):
        self.target.write_bytes(b"")
        with self.assertRaises(PublicError) as caught:
            self.fingerprint()
        self.check_error(caught, "empty")
        self.assertEqual(self.target.read_bytes(), b"")

    def test_oversize_file_is_rejected_without_reading(self):
        self.target.write_bytes(b"a" * 8193)
        with patch.object(guard.os, "read", side_effect=AssertionError("must not read")):
            with self.assertRaises(PublicError) as caught:
                self.fingerprint()
        self.check_error(caught, "bounded")

    def test_missing_file_does_not_reveal_path(self):
        with self.assertRaises(PublicError) as caught:
            self.fingerprint()
        self.check_error(caught, "Cannot read")

    def test_symlink_is_rejected_without_reading_target(self):
        original = self.root / "private.fvslicense"
        original.write_bytes(b"PRIVATE ORIGINAL")
        try:
            self.target.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(PublicError) as caught:
            self.fingerprint()
        self.check_error(caught, "regular file")
        self.assertEqual(original.read_bytes(), b"PRIVATE ORIGINAL")

    @unittest.skipUnless(hasattr(os, "link"), "hardlinks unavailable")
    def test_hardlinked_file_is_rejected_without_mutation(self):
        original = self.root / "unrelated.fvslicense"
        original.write_bytes(b"DO NOT READ ALIAS")
        try:
            os.link(original, self.target)
        except OSError:
            self.skipTest("filesystem denies hardlinks")
        with self.assertRaises(PublicError) as caught:
            self.fingerprint()
        self.check_error(caught, "single-link")
        self.assertEqual(original.read_bytes(), b"DO NOT READ ALIAS")

    def test_directory_rejected_as_nonregular_file(self):
        self.target.mkdir()
        with self.assertRaises(PublicError) as caught:
            self.fingerprint()
        self.check_error(caught, "regular file")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "named pipes unavailable")
    def test_fifo_rejected_without_blocking(self):
        try:
            os.mkfifo(self.target)
        except OSError:
            self.skipTest("filesystem denies fifos")
        with self.assertRaises(PublicError) as caught:
            self.fingerprint()
        self.check_error(caught, "regular file")

    def test_open_failure_cleans_exception_chain(self):
        with patch.object(guard.os, "open", side_effect=PermissionError(PRIVATE)):
            with self.assertRaises(PublicError) as caught:
                self.fingerprint()
        self.check_error(caught, "Cannot read")

    def test_path_inspection_failure_cleans_exception_chain(self):
        with patch.object(Path, "is_symlink", side_effect=PermissionError(PRIVATE)):
            with self.assertRaises(PublicError) as caught:
                self.fingerprint()
        self.check_error(caught, "Cannot read")

    def test_metadata_fault_closes_owned_fd_and_redacts(self):
        self.target.write_bytes(b"safe")
        real_fstat, real_close = os.fstat, os.close
        captured = []
        def fail_metadata(fd):
            captured.append(fd)
            raise OSError(PRIVATE)
        with patch.object(guard.os, "fstat", side_effect=fail_metadata), \
             patch.object(guard.os, "close", side_effect=real_close) as close:
            with self.assertRaises(PublicError) as caught:
                self.fingerprint()
        self.check_error(caught, "Cannot read")
        self.assertEqual(close.call_count, 1)
        with self.assertRaises(OSError):
            real_fstat(captured[0])

    def test_midstream_read_failure_closes_and_redacts(self):
        self.target.write_bytes(b"safe")
        real_close = os.close
        with patch.object(guard.os, "read", side_effect=OSError(PRIVATE)), \
             patch.object(guard.os, "close", side_effect=real_close) as close:
            with self.assertRaises(PublicError) as caught:
                self.fingerprint()
        self.check_error(caught, "Cannot read")
        self.assertEqual(close.call_count, 1)

    def test_close_fault_is_fail_closed_and_redacted(self):
        self.target.write_bytes(b"safe")
        real_close = os.close
        def closed_then_raise(fd):
            real_close(fd)
            raise OSError(PRIVATE)
        with patch.object(guard.os, "close", side_effect=closed_then_raise):
            with self.assertRaises(PublicError) as caught:
                self.fingerprint()
        self.check_error(caught, "Cannot close")

    def test_short_read_is_not_mistaken_for_complete_evidence(self):
        self.target.write_bytes(b"proof")
        with patch.object(guard.os, "read", side_effect=[b"pro", b""]):
            with self.assertRaises(PublicError) as caught:
                self.fingerprint()
        self.check_error(caught, "changed")

    def test_partial_reads_are_accumulated_deterministically(self):
        self.target.write_bytes(b"proof")
        with patch.object(guard.os, "read", side_effect=[b"p", b"ro", b"of", b""]):
            self.assertEqual(self.fingerprint(), hashlib.sha256(b"proof").hexdigest())

    def test_descriptor_identity_change_is_rejected(self):
        self.target.write_bytes(b"proof")
        original_fstat = os.fstat
        count = 0
        def forged_fstat(fd):
            nonlocal count
            count += 1
            meta = original_fstat(fd)
            if count == 2:
                class Changed:
                    pass
                altered = Changed()
                for field in ("st_mode", "st_nlink", "st_size", "st_dev", "st_ino", "st_mtime_ns", "st_ctime_ns"):
                    setattr(altered, field, getattr(meta, field))
                altered.st_mtime_ns += 1
                return altered
            return meta
        with patch.object(guard.os, "fstat", side_effect=forged_fstat):
            with self.assertRaises(PublicError) as caught:
                self.fingerprint()
        self.check_error(caught, "changed")

    def test_never_opens_for_write_or_creates_output(self):
        self.target.write_bytes(b"signed")
        real_open = os.open
        flags_used = []
        def observe(path, flags, *args, **kwargs):
            flags_used.append(flags)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(guard.os, "open", side_effect=observe):
            self.fingerprint()
        self.assertEqual(len(flags_used), 1)
        self.assertEqual(flags_used[0] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT), 0)
        if hasattr(os, "O_NONBLOCK"):
            self.assertTrue(flags_used[0] & os.O_NONBLOCK)


if __name__ == "__main__":
    unittest.main()
