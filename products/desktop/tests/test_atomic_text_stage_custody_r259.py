"""R259: local text/manifest staging failure redaction and real FD custody.

Uses only synthetic temporary evidence, no cloud, no telemetry, no premium files.
The actual atomic_text publisher is exercised; only fault boundaries are patched.
"""
from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.atomic_text import publish_text


class AtomicTextStageCustodyR259(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.private = "customer-financial-secret-259"
        self.destination = self.root / (self.private + ".txt")
        self.data = "Claim,€29.07\r\nSection,Δ\n"

    def assert_unpublished(self):
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.root.glob(".fvs-text-*.partial")), [])

    def assert_safe(self, exc, expected):
        self.assertEqual(str(exc), expected)
        self.assertNotIn(self.private, str(exc))
        self.assertNotIn(str(self.root), str(exc))
        self.assertNotIn("PRIVATE MATERIAL", str(exc))
        self.assertTrue(exc.__suppress_context__)
        self.assert_unpublished()

    def adoption_fault(self, fault, expected_type, expected_message=None):
        fds = []
        real_mkstemp = tempfile.mkstemp

        def record(*args, **kwargs):
            fd, path = real_mkstemp(*args, **kwargs)
            fds.append(fd)
            return fd, path

        try:
            with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=record):
                with patch("fvs_suite.atomic_text.os.fdopen", side_effect=fault):
                    with self.assertRaises(expected_type) as context:
                        publish_text(self.destination, self.data)
            self.assertEqual(len(fds), 1)
            # Verify real OS FD ownership was released on every failure type.
            with self.assertRaises(OSError):
                os.fstat(fds[0])
            self.assert_unpublished()
            if expected_message is not None:
                self.assert_safe(context.exception, expected_message)
            return context.exception
        finally:
            for fd in fds:
                try:
                    os.close(fd)
                except OSError:
                    pass

    def creation_fault(self, fault, expected_type, expected_message=None):
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=fault):
            with self.assertRaises(expected_type) as context:
                publish_text(self.destination, self.data)
        self.assert_unpublished()
        if expected_message is not None:
            self.assert_safe(context.exception, expected_message)
        return context.exception

    def test_fdopen_runtimeerror_is_private_and_closes_real_fd(self):
        self.adoption_fault(RuntimeError("PRIVATE MATERIAL " + self.private),
                            ValueError, "Text report staging could not be opened")

    def test_fdopen_typeerror_is_private_and_closes_real_fd(self):
        self.adoption_fault(TypeError("PRIVATE MATERIAL " + self.private),
                            ValueError, "Text report staging could not be opened")

    def test_fdopen_valueerror_is_private_and_closes_real_fd(self):
        self.adoption_fault(ValueError("PRIVATE MATERIAL " + self.private),
                            ValueError, "Text report staging could not be opened")

    def test_fdopen_assertionerror_is_private_and_closes_real_fd(self):
        self.adoption_fault(AssertionError("PRIVATE MATERIAL " + self.private),
                            ValueError, "Text report staging could not be opened")

    def test_mkstemp_runtimeerror_is_private(self):
        self.creation_fault(RuntimeError("PRIVATE MATERIAL " + self.private),
                            ValueError, "Text report staging could not be created")

    def test_mkstemp_typeerror_is_private(self):
        self.creation_fault(TypeError("PRIVATE MATERIAL " + self.private),
                            ValueError, "Text report staging could not be created")

    def test_mkstemp_valueerror_is_private(self):
        self.creation_fault(ValueError("PRIVATE MATERIAL " + self.private),
                            ValueError, "Text report staging could not be created")

    def test_fdopen_oserror_preserves_native_redacted_errno_and_closes(self):
        fault = PermissionError(errno.EACCES, "PRIVATE MATERIAL", str(self.destination))
        exc = self.adoption_fault(fault, OSError, "[Errno 13] Text report publication failed")
        self.assertEqual(exc.errno, errno.EACCES)

    def test_mkstemp_oserror_preserves_native_redacted_errno(self):
        fault = OSError(errno.ENOSPC, "PRIVATE MATERIAL", str(self.destination))
        exc = self.creation_fault(fault, OSError, "[Errno 28] Text report publication failed")
        self.assertEqual(exc.errno, errno.ENOSPC)

    def test_fdopen_keyboard_interrupt_is_not_masked_and_closes(self):
        self.adoption_fault(KeyboardInterrupt(), KeyboardInterrupt)

    def test_fdopen_system_exit_is_not_masked_and_closes(self):
        self.adoption_fault(SystemExit("original"), SystemExit)

    def test_fdopen_memory_error_is_not_masked_and_closes(self):
        self.adoption_fault(MemoryError("original"), MemoryError)

    def test_mkstemp_keyboard_interrupt_is_not_masked(self):
        self.creation_fault(KeyboardInterrupt(), KeyboardInterrupt)

    def test_mkstemp_system_exit_is_not_masked(self):
        self.creation_fault(SystemExit("original"), SystemExit)

    def test_mkstemp_memory_error_is_not_masked(self):
        self.creation_fault(MemoryError("original"), MemoryError)

    def test_success_keeps_exact_utf8_line_endings(self):
        self.assertEqual(publish_text(self.destination, self.data), self.destination)
        self.assertEqual(self.destination.read_bytes(), self.data.encode("utf-8"))
        self.assertEqual(list(self.root.glob(".fvs-text-*.partial")), [])

    def test_existing_evidence_preserved_and_not_replaced(self):
        self.destination.write_bytes(b"original protected audit evidence")
        with self.assertRaises(FileExistsError) as context:
            publish_text(self.destination, self.data)
        self.assertEqual(str(context.exception), "Text report destination already exists")
        self.assertEqual(self.destination.read_bytes(), b"original protected audit evidence")
        self.assertEqual(list(self.root.glob(".fvs-text-*.partial")), [])

    def test_unavailable_output_folder_does_not_create_staging(self):
        with self.assertRaisesRegex(ValueError, "Choose an existing output folder"):
            publish_text(self.root / "nonexistent" / "report.txt", self.data)
        self.assert_unpublished()


if __name__ == "__main__":
    unittest.main()
