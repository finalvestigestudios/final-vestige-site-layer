"""R235: local same-length corruption must never become audit evidence.

All documents are synthetic, ephemeral; no network, telemetry or paid artifacts.
Tests use a real mkstemp read/write FD and deterministic fault injection.
"""
import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.atomic_text import publish_text, _verify_staged_bytes


class ExactStagedBytesR235(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.private_name = "client-secret-grant-7419"
        self.target = self.root / (self.private_name + ".txt")
        self.content = "Source\t€52.41\r\nEvidence\tΔ\n"
        self.payload = self.content.encode("utf-8")

    def assert_private_failure(self, exc):
        self.assertIsInstance(exc, OSError)
        self.assertEqual(exc.errno, errno.EIO)
        self.assertEqual(str(exc), "[Errno 5] Text report publication failed")
        self.assertNotIn(self.private_name, str(exc))
        self.assertNotIn(str(self.root), str(exc))
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def mutate_same_length(self, new_bytes):
        self.assertEqual(len(new_bytes), len(self.payload))
        original_fstat = os.fstat
        calls = []
        def mutate_after_flush(fd):
            status = original_fstat(fd)
            calls.append(fd)
            os.lseek(fd, 0, os.SEEK_SET)
            self.assertEqual(os.write(fd, new_bytes), len(new_bytes))
            return status
        with patch("fvs_suite.atomic_text.os.fstat", side_effect=mutate_after_flush):
            with self.assertRaises(OSError) as ctx:
                publish_text(self.target, self.content)
        self.assertEqual(len(calls), 1)
        self.assert_private_failure(ctx.exception)

    def test_equal_length_first_byte_replacement_fails(self):
        self.mutate_same_length(b"X" + self.payload[1:])

    def test_equal_length_last_byte_replacement_fails(self):
        self.mutate_same_length(self.payload[:-1] + b"!")

    def test_equal_length_unicode_payload_replacement_fails(self):
        self.mutate_same_length(self.payload.replace("€".encode(), b"USD"))

    def test_equal_length_line_ending_replacement_fails(self):
        self.mutate_same_length(self.payload.replace(b"\r\n", b"!!"))

    def test_equal_length_internal_evidence_replacement_fails(self):
        self.mutate_same_length(self.payload.replace(b"52.41", b"99.99"))

    def test_unmodified_payload_publishes_exact_bytes(self):
        self.assertEqual(publish_text(self.target, self.content), self.target)
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def test_empty_payload_publishes_exact_empty_file(self):
        publish_text(self.target, "")
        self.assertEqual(self.target.read_bytes(), b"")

    def test_very_large_payload_spans_multiple_verification_reads(self):
        evidence = "A" * (256 * 1024 + 11) + "🧪"
        publish_text(self.target, evidence)
        self.assertEqual(self.target.read_bytes(), evidence.encode())

    def test_read_failure_redacts_paths_and_cleans_up(self):
        with patch("fvs_suite.atomic_text.os.read", side_effect=OSError(errno.EIO, "SENSITIVE", str(self.target))):
            with self.assertRaises(OSError) as ctx:
                publish_text(self.target, self.content)
        self.assert_private_failure(ctx.exception)

    def test_seek_failure_redacts_paths_and_cleans_up(self):
        with patch("fvs_suite.atomic_text.os.lseek", side_effect=OSError(errno.EIO, "SENSITIVE", str(self.target))):
            with self.assertRaises(OSError) as ctx:
                publish_text(self.target, self.content)
        self.assert_private_failure(ctx.exception)

    def test_early_eof_never_publishes(self):
        with patch("fvs_suite.atomic_text.os.read", return_value=b""):
            with self.assertRaises(OSError) as ctx:
                publish_text(self.target, self.content)
        self.assert_private_failure(ctx.exception)

    def test_substituted_read_bytes_never_publishes(self):
        with patch("fvs_suite.atomic_text.os.read", return_value=b"F" * len(self.payload)):
            with self.assertRaises(OSError) as ctx:
                publish_text(self.target, self.content)
        self.assert_private_failure(ctx.exception)

    def test_bad_read_never_fsyncs(self):
        with patch("fvs_suite.atomic_text.os.read", return_value=b"BAD"):
            with patch("fvs_suite.atomic_text.os.fsync", side_effect=AssertionError("unexpected fsync")):
                with self.assertRaises(OSError) as ctx:
                    publish_text(self.target, self.content)
        self.assert_private_failure(ctx.exception)

    def test_private_staged_descriptor_is_read_directly_not_reopened(self):
        original_read = os.read
        fd_reads = []
        def observe(fd, length):
            fd_reads.append((fd, length))
            return original_read(fd, length)
        with patch("fvs_suite.atomic_text.os.read", side_effect=observe):
            publish_text(self.target, self.content)
        self.assertGreaterEqual(len(fd_reads), 2)
        self.assertEqual(fd_reads[0][1], len(self.payload))
        self.assertEqual(fd_reads[-1][1], 1)
        self.assertEqual(self.target.read_bytes(), self.payload)

    def test_original_existing_report_cannot_be_replaced(self):
        self.target.write_bytes(b"official preserved evidence")
        with self.assertRaises(FileExistsError):
            publish_text(self.target, self.content)
        self.assertEqual(self.target.read_bytes(), b"official preserved evidence")

    def test_direct_verifier_checks_extra_bytes_even_empty_payload(self):
        fd, name = tempfile.mkstemp(dir=self.root)
        try:
            self.assertEqual(os.write(fd, b"secret"), 6)
            with self.assertRaises(OSError) as ctx:
                _verify_staged_bytes(fd, b"")
            self.assertEqual(ctx.exception.errno, errno.EIO)
        finally:
            os.close(fd)
            os.unlink(name)

    def test_verifier_accepts_exact_real_fd(self):
        fd, name = tempfile.mkstemp(dir=self.root)
        try:
            os.write(fd, self.payload)
            _verify_staged_bytes(fd, self.payload)
        finally:
            os.close(fd)
            os.unlink(name)


if __name__ == '__main__':
    unittest.main()
