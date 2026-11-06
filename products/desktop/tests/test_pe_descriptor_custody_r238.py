"""R238: never leak PE verifier input descriptors across open/inspect failures.

Synthetic executable bytes only. These tests do not certify any Windows binary.
"""
from __future__ import annotations

import errno
import os
import stat
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pe_image_guard import PEFormatError, verify_amd64_pe


class PEOpenDescriptorCustodyR238(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.file = self.root / "private-financial-data-candidate.exe"
        self.file.write_bytes(b"X" * 1024)
        self.real_open = os.open
        self.opened = []

    def instrument_open(self, *args, **kwargs):
        fd = self.real_open(*args, **kwargs)
        self.opened.append(fd)
        return fd

    def assert_all_closed(self):
        self.assertEqual(len(self.opened), 1)
        for fd in self.opened:
            with self.assertRaises(OSError) as raised:
                os.fstat(fd)
            self.assertEqual(raised.exception.errno, errno.EBADF)

    def test_regular_truncated_format_closes_fd(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with self.assertRaises(PEFormatError):
                verify_amd64_pe(self.file)
        self.assert_all_closed()

    def test_metadata_permission_error_closes_fd_and_redacts(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with patch("pe_image_guard.os.fstat", side_effect=PermissionError(errno.EACCES, "payroll-secret", str(self.file))):
                with self.assertRaises(PEFormatError) as raised:
                    verify_amd64_pe(self.file)
        self.assertEqual(str(raised.exception), "Cannot inspect candidate file")
        self.assertNotIn(str(self.file), str(raised.exception))
        self.assert_all_closed()

    def test_metadata_disk_io_error_closes_fd_and_redacts(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with patch("pe_image_guard.os.fstat", side_effect=OSError(errno.EIO, "secret", str(self.file))):
                with self.assertRaisesRegex(PEFormatError, "Cannot inspect candidate file"):
                    verify_amd64_pe(self.file)
        self.assert_all_closed()

    def test_fdopen_oserror_closes_fd_and_redacts(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with patch("pe_image_guard.os.fdopen", side_effect=OSError(errno.EMFILE, "confidential", str(self.file))):
                with self.assertRaises(PEFormatError) as raised:
                    verify_amd64_pe(self.file)
        self.assertEqual(str(raised.exception), "Cannot inspect candidate file")
        self.assert_all_closed()

    def test_fdopen_keyboard_interrupt_closes_fd(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with patch("pe_image_guard.os.fdopen", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    verify_amd64_pe(self.file)
        self.assert_all_closed()

    def test_fdopen_system_exit_closes_fd(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with patch("pe_image_guard.os.fdopen", side_effect=SystemExit(2)):
                with self.assertRaises(SystemExit):
                    verify_amd64_pe(self.file)
        self.assert_all_closed()

    def test_fdopen_value_error_closes_fd_without_client_message(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with patch("pe_image_guard.os.fdopen", side_effect=ValueError("client secret")):
                with self.assertRaises(PEFormatError) as caught:
                    verify_amd64_pe(self.file)
        self.assertEqual(str(caught.exception), "Cannot inspect candidate file")
        self.assert_all_closed()

    def test_fstat_interrupt_closes_fd(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with patch("pe_image_guard.os.fstat", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    verify_amd64_pe(self.file)
        self.assert_all_closed()

    def test_fstat_system_exit_closes_fd(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with patch("pe_image_guard.os.fstat", side_effect=SystemExit(17)):
                with self.assertRaises(SystemExit):
                    verify_amd64_pe(self.file)
        self.assert_all_closed()

    def test_minimal_valid_synthetic_amd64_pe_passes_and_keeps_original(self):
        # A synthetic PE32+ format fixture, NEVER a built/safe application.
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
        data[section:section+5] = b".text"
        struct.pack_into("<IIII", data, section+8, 0x100, 0x1000, 0x200, 0x200)
        struct.pack_into("<I", data, section+36, 0x60000020)
        self.file.write_bytes(data)
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            self.assertIsNone(verify_amd64_pe(self.file))
        self.assert_all_closed()
        self.assertEqual(self.file.read_bytes(), data)

    def test_nonregular_metadata_closes_fd(self):
        fake = os.stat_result((stat.S_IFDIR | 0o755,) + (0,) * 9)
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with patch("pe_image_guard.os.fstat", return_value=fake):
                with self.assertRaisesRegex(PEFormatError, "not a regular file"):
                    verify_amd64_pe(self.file)
        self.assert_all_closed()

    def test_open_failure_no_fd_error_contains_no_private_path(self):
        with patch("pe_image_guard.os.open", side_effect=PermissionError(errno.EACCES, "private", str(self.file))):
            with self.assertRaises(PEFormatError) as raised:
                verify_amd64_pe(self.file)
        self.assertEqual(str(raised.exception), "Cannot open candidate without following file symlinks")
        self.assertNotIn(str(self.file), str(raised.exception))

    def test_bad_mz_fails_without_disrupting_original_bytes(self):
        original = self.file.read_bytes()
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with self.assertRaisesRegex(PEFormatError, "Missing DOS MZ signature"):
                verify_amd64_pe(self.file)
        self.assert_all_closed()
        self.assertEqual(self.file.read_bytes(), original)

    def test_successful_stream_ownership_uses_original_fd(self):
        with patch("pe_image_guard.os.open", side_effect=self.instrument_open):
            with self.assertRaises(PEFormatError):
                verify_amd64_pe(self.file)
        self.assert_all_closed()


if __name__ == "__main__":
    unittest.main()
