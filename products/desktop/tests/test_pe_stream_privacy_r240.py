"""R240: post-handoff PE file I/O cannot leak private filesystem details.

No executable is built, run, published or approved. Tests use local synthetic PE
headers, real descriptors, and intentionally failing stream operations.
"""
from __future__ import annotations

import errno
import os
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pe_image_guard
from pe_image_guard import PEFormatError, verify_amd64_pe


class _StreamProxy:
    """Wrap a real buffered file while forcing controlled enter/exit faults."""
    def __init__(self, real, *, enter_error=None, exit_error=None, read_error=None, seek_error=None):
        self.real = real
        self.enter_error = enter_error
        self.exit_error = exit_error
        self.read_error = read_error
        self.seek_error = seek_error
        self.close_called = False

    def __enter__(self):
        if self.enter_error is not None:
            raise self.enter_error
        self.real.__enter__()
        return self

    def __exit__(self, *args):
        self.real.__exit__(*args)
        if self.exit_error is not None:
            raise self.exit_error

    def close(self):
        self.close_called = True
        self.real.close()

    def read(self, *args, **kwargs):
        if self.read_error is not None:
            raise self.read_error
        return self.real.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        if self.seek_error is not None:
            raise self.seek_error
        return self.real.seek(*args, **kwargs)

    def __getattr__(self, key):
        return getattr(self.real, key)


class PEStreamPrivacyR240(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r240-")
        self.addCleanup(temp.cleanup)
        self.candidate = Path(temp.name) / "customer-bank-reconciliation-secret.exe"
        self.candidate.write_bytes(self._synthetic_pe())
        self.pristine = self.candidate.read_bytes()
        self.original_open = os.open
        self.original_fdopen = os.fdopen
        self.opened = []
        self.original_read_at = pe_image_guard._read_at

    @staticmethod
    def _synthetic_pe() -> bytes:
        data = bytearray(1024)
        data[:2] = b"MZ"
        struct.pack_into("<I", data, 0x3c, 0x80)
        data[0x80:0x84] = b"PE\x00\x00"
        struct.pack_into("<HHIIIHH", data, 0x84, 0x8664, 1, 0, 0, 0, 240, 0x0022)
        opt = 0x80 + 24
        struct.pack_into("<H", data, opt, 0x20B)
        struct.pack_into("<I", data, opt + 16, 0x1000)
        struct.pack_into("<I", data, opt + 32, 0x1000)
        struct.pack_into("<I", data, opt + 36, 0x200)
        struct.pack_into("<I", data, opt + 56, 0x2000)
        struct.pack_into("<I", data, opt + 60, 0x200)
        struct.pack_into("<H", data, opt + 68, 2)
        section = opt + 240
        data[section:section + 5] = b".text"
        struct.pack_into("<IIII", data, section + 8, 0x100, 0x1000, 0x200, 0x200)
        struct.pack_into("<I", data, section + 36, 0x60000020)
        return bytes(data)

    def tracking_open(self, *args, **kwargs):
        descriptor = self.original_open(*args, **kwargs)
        self.opened.append(descriptor)
        return descriptor

    def assert_clean(self):
        self.assertEqual(len(self.opened), 1)
        with self.assertRaises(OSError) as raised:
            os.fstat(self.opened[0])
        self.assertEqual(raised.exception.errno, errno.EBADF)
        self.assertEqual(self.candidate.read_bytes(), self.pristine)

    def failing_read_at(self, position, error):
        seen = 0
        def read_at(stream, start, count, length):
            nonlocal seen
            seen += 1
            if seen == position:
                raise error
            return self.original_read_at(stream, start, count, length)
        return read_at

    def expect_private_failure(self, failure, position):
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            with patch("pe_image_guard._read_at", side_effect=self.failing_read_at(position, failure)):
                with self.assertRaises(PEFormatError) as raised:
                    verify_amd64_pe(self.candidate)
        self.assertEqual(str(raised.exception), "Cannot inspect candidate file")
        self.assertIsNone(raised.exception.__cause__)
        self.assertNotIn(str(self.candidate), str(raised.exception))
        self.assertNotIn("secret", str(raised.exception).lower())
        self.assert_clean()

    def test_dos_header_read_permission_error_redacted(self):
        self.expect_private_failure(PermissionError(errno.EACCES, "secret customer", str(self.candidate)), 1)

    def test_nt_header_seek_io_error_redacted(self):
        self.expect_private_failure(OSError(errno.EIO, "secret customer", str(self.candidate)), 2)

    def test_optional_header_path_error_redacted(self):
        self.expect_private_failure(FileNotFoundError(errno.ENOENT, "secret customer", str(self.candidate)), 3)

    def test_section_table_io_error_redacted(self):
        self.expect_private_failure(OSError(errno.EBADF, "secret customer", str(self.candidate)), 4)

    def test_dos_header_type_error_redacted(self):
        self.expect_private_failure(TypeError("secret source filename"), 1)

    def test_optional_header_unicode_error_redacted(self):
        self.expect_private_failure(UnicodeError("secret source filename"), 3)

    def test_table_parse_value_error_redacted(self):
        self.expect_private_failure(ValueError("secret private storage"), 4)

    def test_stream_enter_failure_is_redacted_and_closed(self):
        proxy = []
        def failing_fdopen(*args, **kwargs):
            wrapper = _StreamProxy(self.original_fdopen(*args, **kwargs),
                                   enter_error=OSError(errno.EIO, "secret", str(self.candidate)))
            proxy.append(wrapper)
            return wrapper
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            with patch("pe_image_guard.os.fdopen", side_effect=failing_fdopen):
                with self.assertRaises(PEFormatError) as caught:
                    verify_amd64_pe(self.candidate)
        self.assertEqual(str(caught.exception), "Cannot inspect candidate file")
        self.assertTrue(proxy[0].close_called)
        self.assert_clean()

    def test_stream_exit_failure_is_redacted_and_closed(self):
        def failing_fdopen(*args, **kwargs):
            return _StreamProxy(self.original_fdopen(*args, **kwargs),
                                exit_error=OSError(errno.EIO, "secret", str(self.candidate)))
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            with patch("pe_image_guard.os.fdopen", side_effect=failing_fdopen):
                with self.assertRaises(PEFormatError) as caught:
                    verify_amd64_pe(self.candidate)
        self.assertEqual(str(caught.exception), "Cannot inspect candidate file")
        self.assert_clean()

    def test_real_stream_seek_error_is_redacted_and_closed(self):
        def failing_fdopen(*args, **kwargs):
            return _StreamProxy(self.original_fdopen(*args, **kwargs),
                                seek_error=PermissionError(errno.EACCES, "secret", str(self.candidate)))
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            with patch("pe_image_guard.os.fdopen", side_effect=failing_fdopen):
                with self.assertRaises(PEFormatError) as caught:
                    verify_amd64_pe(self.candidate)
        self.assertEqual(str(caught.exception), "Cannot inspect candidate file")
        self.assert_clean()

    def test_real_stream_read_error_is_redacted_and_closed(self):
        def failing_fdopen(*args, **kwargs):
            return _StreamProxy(self.original_fdopen(*args, **kwargs),
                                read_error=OSError(errno.EIO, "secret", str(self.candidate)))
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            with patch("pe_image_guard.os.fdopen", side_effect=failing_fdopen):
                with self.assertRaises(PEFormatError) as caught:
                    verify_amd64_pe(self.candidate)
        self.assertEqual(str(caught.exception), "Cannot inspect candidate file")
        self.assert_clean()

    def test_enter_keyboard_interrupt_preserves_interrupt_and_closes(self):
        proxy = []
        def failing_fdopen(*args, **kwargs):
            wrapper = _StreamProxy(self.original_fdopen(*args, **kwargs),
                                   enter_error=KeyboardInterrupt())
            proxy.append(wrapper)
            return wrapper
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            with patch("pe_image_guard.os.fdopen", side_effect=failing_fdopen):
                with self.assertRaises(KeyboardInterrupt):
                    verify_amd64_pe(self.candidate)
        self.assertTrue(proxy[0].close_called)
        self.assert_clean()

    def test_structural_validation_stays_specific(self):
        self.candidate.write_bytes(b"X" * 1024)
        self.pristine = self.candidate.read_bytes()
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            with self.assertRaisesRegex(PEFormatError, "Missing DOS MZ signature"):
                verify_amd64_pe(self.candidate)
        self.assert_clean()

    def test_native_synthetic_pe_passes(self):
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            self.assertIsNone(verify_amd64_pe(self.candidate))
        self.assert_clean()

    def test_keyboard_interrupt_keeps_interrupt_semantics_and_closes(self):
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            with patch("pe_image_guard._read_at", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    verify_amd64_pe(self.candidate)
        self.assert_clean()

    def test_system_exit_keeps_interrupt_semantics_and_closes(self):
        with patch("pe_image_guard.os.open", side_effect=self.tracking_open):
            with patch("pe_image_guard._read_at", side_effect=SystemExit(31)):
                with self.assertRaises(SystemExit) as caught:
                    verify_amd64_pe(self.candidate)
        self.assertEqual(caught.exception.code, 31)
        self.assert_clean()


if __name__ == "__main__":
    unittest.main()
