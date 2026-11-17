"""R494 integration: PE parser and six-candidate gate reject malformed directories.

All fixtures are inert synthetic PE-shaped bytes; no executable is launched.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import tempfile
import unittest

from build_inventory import EXPECTED, build_inventory
from pe_fixture_r17 import synthetic_pe64
from pe_image_guard import PEFormatError, verify_amd64_pe
import release_gate


OPTIONAL_START = 128 + 24
DIRECTORIES_START = OPTIONAL_START + 112


def candidate(*, entry: int, address: int, size: int, count: int,
              overlay: bytes = b"") -> bytes:
    raw = bytearray(synthetic_pe64())
    struct.pack_into("<I", raw, OPTIONAL_START + 108, count)
    struct.pack_into("<II", raw, DIRECTORIES_START + 8 * entry, address, size)
    return bytes(raw) + overlay


class PEDataDirectoryIntegrationR494(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r494-int-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.exe = self.root / EXPECTED[0]

    def inspect(self, raw: bytes) -> None:
        self.exe.write_bytes(raw)
        verify_amd64_pe(self.exe,
                        expected_sha256=hashlib.sha256(raw).hexdigest())

    def test_mapped_import_table_passes(self):
        self.inspect(candidate(entry=1, address=4096, size=32, count=2))

    def test_certificate_overlay_passes(self):
        self.inspect(candidate(entry=4, address=1024, size=64,
                               count=5, overlay=b"Z" * 64))

    def test_unmapped_table_rejected(self):
        with self.assertRaises(PEFormatError):
            self.inspect(candidate(entry=1, address=6144, size=32, count=2))

    def test_certificate_overlapping_code_rejected(self):
        with self.assertRaises(PEFormatError):
            self.inspect(candidate(entry=4, address=512, size=64, count=5))

    def test_excessive_directory_count_rejected(self):
        with self.assertRaises(PEFormatError):
            self.inspect(candidate(entry=0, address=4096, size=32, count=17))

    def test_six_candidate_gate_rejects_malformed_directory(self):
        for name in EXPECTED:
            (self.root / name).write_bytes(synthetic_pe64())
        (self.root / EXPECTED[-1]).write_bytes(
            candidate(entry=1, address=6144, size=32, count=2))
        self.assertEqual(build_inventory(self.root), "SHA256SUMS.txt")
        with self.assertRaises(release_gate.GateFailure):
            release_gate.verify(self.root, smoke=False)


if __name__ == "__main__":
    unittest.main()
