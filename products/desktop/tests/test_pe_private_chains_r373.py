"""R373: PE release-candidate guard must not retain private OS fault chains.

Synthetic PE bytes and synthetic path/output canaries only; this is NOT a
Windows binary scan, a release decision, or a claim of premium entitlement.
"""
from __future__ import annotations

import os
import struct
import tempfile
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch

import pe_image_guard
from pe_image_guard import PEFormatError, verify_amd64_pe

PRIVATE = "FVS_R373_SYNTHETIC_CLIENT_PAYROLL_KEY"


def synthetic_pe() -> bytes:
    raw = bytearray(1024)
    raw[:2] = b"MZ"
    struct.pack_into("<I", raw, 0x3C, 0x80)
    raw[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", raw, 0x84, 0x8664, 1, 0, 0, 0, 240, 0x22)
    opt = 0x80 + 24
    for off, fmt, value in ((0, "<H", 0x20B), (16, "<I", 0x1000),
                            (32, "<I", 0x1000), (36, "<I", 0x200),
                            (56, "<I", 0x2000), (60, "<I", 0x200),
                            (68, "<H", 2)):
        struct.pack_into(fmt, raw, opt + off, value)
    sec = opt + 240
    raw[sec:sec + 5] = b".text"
    struct.pack_into("<IIII", raw, sec + 8, 0x100, 0x1000, 0x200, 0x200)
    struct.pack_into("<I", raw, sec + 36, 0x60000020)
    return bytes(raw)


class _StreamProxy:
    def __init__(self, actual, *, fail=None, when=None):
        self.actual = actual
        self.fail = fail
        self.when = when
        self.closed_on_enter_failure = False

    def __enter__(self):
        if self.when == "enter":
            raise self.fail
        self.actual.__enter__()
        return self

    def __exit__(self, *args):
        self.actual.__exit__(*args)
        if self.when == "exit":
            raise self.fail

    def close(self):
        self.closed_on_enter_failure = True
        self.actual.close()

    def seek(self, *args):
        if self.when == "seek":
            raise self.fail
        return self.actual.seek(*args)

    def read(self, *args):
        if self.when == "read":
            raise self.fail
        return self.actual.read(*args)


class PEPrivateExceptionChainsR373(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="r373-inert-fixture-")
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "GrantAuditStudioPro.exe"
        self.path.write_bytes(synthetic_pe())
        self.original = self.path.read_bytes()
        self.fdopen = os.fdopen

    def assert_private_failure(self, msg, **patches):
        from contextlib import ExitStack
        with ExitStack() as stack:
            for target, value in patches.items():
                stack.enter_context(patch(target, side_effect=value))
            with self.assertRaises(PEFormatError) as caught:
                verify_amd64_pe(self.path)
        error = caught.exception
        self.assertEqual(str(error), msg)
        self.assertIsNone(error.__cause__, "original exception retained as __cause__")
        self.assertIsNone(error.__context__, "original exception retained as __context__")
        self.assertNotIn(PRIVATE, "".join(traceback.format_exception(error)))
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_open_path_fault_has_no_chain(self):
        self.assert_private_failure("Cannot open candidate without following file symlinks",
                                    **{"pe_image_guard.os.open": PermissionError(PRIVATE)})

    def test_open_symlink_loop_fault_has_no_chain(self):
        self.assert_private_failure("Cannot open candidate without following file symlinks",
                                    **{"pe_image_guard.os.open": OSError(PRIVATE)})

    def test_fstat_os_error_has_no_chain(self):
        self.assert_private_failure("Cannot inspect candidate file",
                                    **{"pe_image_guard.os.fstat": PermissionError(PRIVATE)})

    def test_fstat_unexpected_error_has_no_chain(self):
        self.assert_private_failure("Cannot inspect candidate file",
                                    **{"pe_image_guard.os.fstat": RuntimeError(PRIVATE)})

    def test_fdopen_os_error_has_no_chain(self):
        self.assert_private_failure("Cannot inspect candidate file",
                                    **{"pe_image_guard.os.fdopen": OSError(PRIVATE)})

    def test_fdopen_unexpected_error_has_no_chain(self):
        self.assert_private_failure("Cannot inspect candidate file",
                                    **{"pe_image_guard.os.fdopen": ValueError(PRIVATE)})

    def run_stream_failure(self, where, error):
        proxies = []
        def fdopen(*args, **kwargs):
            wrapped = _StreamProxy(self.fdopen(*args, **kwargs), fail=error, when=where)
            proxies.append(wrapped)
            return wrapped
        self.assert_private_failure("Cannot inspect candidate file",
                                    **{"pe_image_guard.os.fdopen": fdopen})
        self.assertTrue(proxies)
        self.assertTrue(proxies[0].actual.closed)
        if where == "enter":
            self.assertTrue(proxies[0].closed_on_enter_failure)

    def test_stream_enter_private_fault_has_no_chain(self):
        self.run_stream_failure("enter", OSError(PRIVATE))

    def test_stream_exit_private_fault_has_no_chain(self):
        self.run_stream_failure("exit", OSError(PRIVATE))

    def test_stream_read_private_fault_has_no_chain(self):
        self.run_stream_failure("read", OSError(PRIVATE))

    def test_stream_seek_private_fault_has_no_chain(self):
        self.run_stream_failure("seek", RuntimeError(PRIVATE))

    def test_no_private_fault_still_passes_structurally_valid_inert_pe(self):
        self.assertIsNone(verify_amd64_pe(self.path))
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_structural_failure_remains_specific(self):
        self.path.write_bytes(b"X" * 1024)
        with self.assertRaisesRegex(PEFormatError, "Missing DOS MZ signature") as caught:
            verify_amd64_pe(self.path)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)

    def test_fstat_interrupt_propagates(self):
        with patch("pe_image_guard.os.fstat", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                verify_amd64_pe(self.path)

    def test_fdopen_failure_closes_original_descriptor(self):
        real_open = os.open
        handles = []
        def tracked_open(*args, **kwargs):
            handle = real_open(*args, **kwargs)
            handles.append(handle)
            return handle
        with patch("pe_image_guard.os.open", side_effect=tracked_open):
            self.assert_private_failure("Cannot inspect candidate file",
                                        **{"pe_image_guard.os.fdopen": OSError(PRIVATE)})
        self.assertEqual(len(handles), 1)
        with self.assertRaises(OSError):
            os.fstat(handles[0])

    def test_fstat_failure_closes_original_descriptor(self):
        real_open = os.open
        handles = []
        def tracked_open(*args, **kwargs):
            handle = real_open(*args, **kwargs)
            handles.append(handle)
            return handle
        with patch("pe_image_guard.os.open", side_effect=tracked_open):
            self.assert_private_failure("Cannot inspect candidate file",
                                        **{"pe_image_guard.os.fstat": OSError(PRIVATE)})
        self.assertEqual(len(handles), 1)
        with self.assertRaises(OSError):
            os.fstat(handles[0])

    def test_six_inert_launcher_filenames_share_same_verification(self):
        for launcher in ("LedgerDiffLite.exe", "InvoiceTwinScout.exe",
                         "SpendMapLite.exe", "PolicyDeltaDesk.exe",
                         "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe"):
            with self.subTest(launcher=launcher):
                candidate = self.path.with_name(launcher)
                candidate.write_bytes(self.original)
                self.assertIsNone(verify_amd64_pe(candidate))
                self.assertEqual(candidate.read_bytes(), self.original)

    def test_stream_interrupt_propagates(self):
        def fdopen(*args, **kwargs):
            return _StreamProxy(self.fdopen(*args, **kwargs), fail=SystemExit(73), when="seek")
        with patch("pe_image_guard.os.fdopen", side_effect=fdopen):
            with self.assertRaises(SystemExit) as caught:
                verify_amd64_pe(self.path)
        self.assertEqual(caught.exception.code, 73)


if __name__ == "__main__":
    unittest.main()
