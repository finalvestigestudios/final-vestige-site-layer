"""R242: fail closed BEFORE publication of six-app SHA256SUMS; synthetic data only.

Real temporary files and OS descriptors, no EXE execution or live distribution.
"""
from __future__ import annotations

import errno
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_inventory as inv


class StagingStream:
    """Fault-injection proxy with a genuine underlying native descriptor."""

    def __init__(self, native, mode, error=None):
        self.native = native
        self.mode = mode
        self.error = error
        self.close_called = False

    def __enter__(self):
        if self.mode == "enter":
            raise self.error
        self.native.__enter__()
        return self

    def __exit__(self, *args):
        self.native.__exit__(*args)
        if self.mode == "exit":
            raise self.error

    def write(self, data):
        if self.mode == "write_error":
            raise self.error
        if self.mode == "short":
            self.native.write(data[:5])
            return 5
        if self.mode == "fake_complete":
            self.native.write(b"X" * len(data))
            return len(data)
        if self.mode == "overlong":
            self.native.write(data + b"evil")
            return len(data)
        if self.mode == "bool":
            self.native.write(data)
            return True
        if self.mode == "none":
            self.native.write(data)
            return None
        if self.mode == "wrong_count":
            self.native.write(data)
            return len(data) + 1
        return self.native.write(data)

    def flush(self):
        if self.mode == "flush":
            raise self.error
        return self.native.flush()

    def fileno(self):
        if self.mode == "fileno":
            raise self.error
        return self.native.fileno()

    def close(self):
        self.close_called = True
        return self.native.close()


class InventoryStagingCustodyR242(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r242-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "dist"
        self.root.mkdir()
        self.input = {}
        for index, name in enumerate(inv.EXPECTED):
            data = b"MZnot-a-real-exe" + bytes([index + 3]) * (23 + index)
            self.input[name] = data
            (self.root / name).write_bytes(data)
        self.open_fds = []
        self.wrappers = []
        self.native_fdopen = os.fdopen

    def assert_pristine(self):
        self.assertEqual({p.name for p in self.root.iterdir()}, set(inv.EXPECTED))
        self.assertFalse((self.root / inv.MANIFEST).exists())
        for name, content in self.input.items():
            self.assertEqual((self.root / name).read_bytes(), content)
        for fd in self.open_fds:
            with self.assertRaises(OSError) as caught:
                os.fstat(fd)
            self.assertEqual(caught.exception.errno, errno.EBADF)

    def run_fault(self, *, mode, error=None, expected=inv.InventoryBuildError):
        def fdopen(fd, file_mode, *args, **kwargs):
            if file_mode != "wb":
                return self.native_fdopen(fd, file_mode, *args, **kwargs)
            self.open_fds.append(fd)
            if mode == "fdopen":
                raise error
            wrapper = StagingStream(self.native_fdopen(fd, file_mode, *args, **kwargs), mode, error)
            self.wrappers.append(wrapper)
            return wrapper

        with patch("build_inventory.os.fdopen", side_effect=fdopen):
            with patch("build_inventory.os.link", side_effect=AssertionError("bad data reached publication")):
                with self.assertRaises(expected) as raised:
                    inv.build_inventory(self.root)
        self.assert_pristine()
        if expected is inv.InventoryBuildError:
            self.assertNotIn("secret", str(raised.exception))
            self.assertNotIn("private", str(raised.exception))
            self.assertNotIn(str(self.root), str(raised.exception))
            self.assertIsNone(raised.exception.__cause__)
        return raised.exception

    def test_fdopen_permission_failure_closes_raw_descriptor(self):
        self.run_fault(mode="fdopen", error=PermissionError(errno.EACCES, "secret private name", str(self.root)))

    def test_fdopen_value_failure_redacted_and_closed(self):
        self.run_fault(mode="fdopen", error=ValueError("private ledger path"))

    def test_fdopen_type_failure_redacted_and_closed(self):
        self.run_fault(mode="fdopen", error=TypeError("private ledger path"))

    def test_fdopen_keyboard_interrupt_closes_and_propagates(self):
        self.run_fault(mode="fdopen", error=KeyboardInterrupt(), expected=KeyboardInterrupt)

    def test_fdopen_system_exit_closes_and_propagates(self):
        self.run_fault(mode="fdopen", error=SystemExit(23), expected=SystemExit)

    def test_stream_entry_failure_closes_descriptor(self):
        self.run_fault(mode="enter", error=OSError(errno.EIO, "secret private name", str(self.root)))
        self.assertTrue(self.wrappers[0].close_called)

    def test_stream_entry_interrupt_closes_and_propagates(self):
        self.run_fault(mode="enter", error=KeyboardInterrupt(), expected=KeyboardInterrupt)
        self.assertTrue(self.wrappers[0].close_called)

    def test_short_write_fails_before_publication(self):
        self.run_fault(mode="short")

    def test_wrong_byte_count_fails_before_publication(self):
        self.run_fault(mode="wrong_count")

    def test_bool_write_count_fails_before_publication(self):
        self.run_fault(mode="bool")

    def test_none_write_count_fails_before_publication(self):
        self.run_fault(mode="none")

    def test_equal_length_content_corruption_fails_before_publication(self):
        self.run_fault(mode="fake_complete")

    def test_unreported_appended_bytes_fail_before_publication(self):
        self.run_fault(mode="overlong")

    def test_write_value_error_is_redacted(self):
        self.run_fault(mode="write_error", error=ValueError("private client report"))

    def test_write_permission_error_is_redacted(self):
        self.run_fault(mode="write_error", error=PermissionError(errno.EACCES, "private client report", str(self.root)))

    def test_flush_failure_is_redacted_and_closed(self):
        self.run_fault(mode="flush", error=RuntimeError("secret invoice file"))

    def test_fileno_failure_is_redacted_and_closed(self):
        self.run_fault(mode="fileno", error=TypeError("private client report"))

    def test_exit_failure_is_redacted_and_closed(self):
        self.run_fault(mode="exit", error=ValueError("secret client report"))

    def test_normal_manifest_is_exact_and_staging_removed(self):
        self.assertEqual(inv.build_inventory(self.root), inv.MANIFEST)
        expected = b"".join(hashlib.sha256(self.input[name]).hexdigest().encode("ascii")
                            + b"  " + name.encode("ascii") + b"\n"
                            for name in inv.EXPECTED)
        self.assertEqual((self.root / inv.MANIFEST).read_bytes(), expected)
        self.assertEqual({p.name for p in self.root.iterdir()}, set(inv.EXPECTED) | {inv.MANIFEST})
        self.assertEqual([p for p in self.root.iterdir() if p.name.startswith(".fvs-inventory-")], [])
        for name, content in self.input.items():
            self.assertEqual((self.root / name).read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
