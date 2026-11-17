"""R498: PE inspection must use raw FileIO, never a readahead buffer.

All files are inert synthetic bytes; tests neither execute nor publish EXEs.
Only a real unbuffered descriptor can reliably observe external truncation
between reading a WIN_CERTIFICATE header and probing its declared tail.
"""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


class RawDescriptorBehaviorR498(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r498-raw-")
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "inert-image.bin"
        self.path.write_bytes(b"A" * 8192)

    def raw(self):
        fd = os.open(self.path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
        return os.fdopen(fd, "rb", buffering=0)

    def test_descriptor_is_raw_fileio_not_readahead_buffer(self):
        with self.raw() as stream:
            self.assertIsInstance(stream, io.FileIO)
            self.assertNotIsInstance(stream, io.BufferedReader)

    def test_tail_after_truncation_is_not_served_from_old_buffer(self):
        with self.raw() as stream:
            self.assertEqual(stream.read(8), b"A" * 8)
            with self.path.open("r+b") as writer:
                writer.truncate(8)
            stream.seek(4095)
            self.assertEqual(stream.read(1), b"")

    def test_multiple_records_do_not_reuse_prefetched_tail(self):
        with self.raw() as stream:
            self.assertEqual(stream.read(8), b"A" * 8)
            stream.seek(2048)
            self.assertEqual(stream.read(8), b"A" * 8)
            with self.path.open("r+b") as writer:
                writer.truncate(2056)
            stream.seek(4095)
            self.assertEqual(stream.read(1), b"")

    def test_held_descriptor_reads_actual_in_place_change(self):
        with self.raw() as stream:
            self.assertEqual(stream.read(8), b"A" * 8)
            with self.path.open("r+b") as writer:
                writer.seek(4095)
                writer.write(b"Z")
            stream.seek(4095)
            self.assertEqual(stream.read(1), b"Z")

    def test_held_descriptor_not_retargeted_by_path_replacement(self):
        with self.raw() as stream:
            self.assertEqual(stream.read(8), b"A" * 8)
            replacement = self.path.with_suffix(".replacement")
            replacement.write_bytes(b"Z" * 8192)
            os.replace(replacement, self.path)
            stream.seek(4095)
            self.assertEqual(stream.read(1), b"A")
            self.assertEqual(self.path.read_bytes()[4095:4096], b"Z")

    def test_owner_closes_raw_descriptor(self):
        stream = self.raw()
        self.assertFalse(stream.closed)
        with stream:
            self.assertEqual(stream.read(1), b"A")
        self.assertTrue(stream.closed)


class RealPEParserBindingR498(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r498-pe-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_parser_requests_unbuffered_fileio_even_when_image_invalid(self):
        import pe_image_guard
        path = self.root / "invalid.exe"
        path.write_bytes(b"MZ" + b"\x00" * 510)
        actual_fdopen = os.fdopen
        calls = []

        def witness(fd, mode="r", buffering=-1, *args, **kwargs):
            calls.append((mode, buffering))
            return actual_fdopen(fd, mode, buffering, *args, **kwargs)

        with mock.patch.object(pe_image_guard.os, "fdopen", side_effect=witness):
            with self.assertRaises(pe_image_guard.PEFormatError):
                pe_image_guard.verify_amd64_pe(path)
        self.assertEqual(calls, [("rb", 0)])

    def test_real_pe_parser_gives_certificate_guard_raw_fileio(self):
        import pe_image_guard
        from pe_fixture_r17 import synthetic_pe64
        raw = synthetic_pe64()
        path = self.root / "LedgerDiffLite.exe"
        path.write_bytes(raw)
        real_guard = pe_image_guard.verify_certificate_table
        witnessed = []

        def witness(stream, optional, *, file_size):
            witnessed.append(type(stream))
            self.assertIsInstance(stream, io.FileIO)
            return real_guard(stream, optional, file_size=file_size)

        with mock.patch.object(pe_image_guard, "verify_certificate_table", side_effect=witness):
            pe_image_guard.verify_amd64_pe(path, expected_sha256=hashlib.sha256(raw).hexdigest())
        self.assertEqual(witnessed, [io.FileIO])

    def test_all_six_inert_candidates_have_raw_descriptor_and_digest(self):
        from build_inventory import EXPECTED
        from pe_fixture_r17 import synthetic_pe64
        from pe_image_guard import verify_amd64_pe
        self.assertEqual(len(EXPECTED), 6)
        raw = synthetic_pe64()
        digest = hashlib.sha256(raw).hexdigest()
        for name in EXPECTED:
            with self.subTest(candidate=name):
                path = self.root / name
                path.write_bytes(raw)
                verify_amd64_pe(path, expected_sha256=digest)


if __name__ == "__main__":
    unittest.main()
