"""Fail-closed synthetic PE32+ directory regressions; no executable runs."""
from __future__ import annotations

import struct
import unittest

from pe_directory_guard_r494 import PEDataDirectoryError, validate_pe_directories


def header(entries=(), count=None, length=240):
    raw = bytearray(length)
    struct.pack_into("<I", raw, 108, len(entries) if count is None else count)
    for index, offset, size in entries:
        struct.pack_into("<II", raw, 112 + index * 8, offset, size)
    return bytes(raw)


class PEDataDirectoryR494(unittest.TestCase):
    def check(self, optional):
        validate_pe_directories(optional, header_size=512,
                                image_size=8192, file_size=2048,
                                virtual_ranges=[(4096, 4608), (5120, 5632)],
                                file_ranges=[(512, 1024), (1024, 1536)])

    def test_empty_table_passes(self):
        self.check(header())

    def test_valid_section_directory_passes(self):
        self.check(header([(0, 4096, 64)]))

    def test_valid_header_directory_passes(self):
        self.check(header([(0, 256, 64)]))

    def test_valid_certificate_overlay_passes(self):
        self.check(header([(4, 1536, 64)], count=5))

    def test_sixteen_entries_supported(self):
        self.check(header([(0, 4096, 48), (4, 1536, 80)], count=16))

    def test_oversized_count_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(header(count=17))

    def test_truncated_table_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(header(count=2, length=120))

    def test_partial_zero_pair_rejected(self):
        for a, b in ((4096, 0), (0, 16)):
            with self.subTest(a=a, b=b), self.assertRaises(PEDataDirectoryError):
                self.check(header([(0, a, b)]))

    def test_image_extent_overrun_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(header([(1, 8160, 128)], count=2))

    def test_directory_in_unmapped_gap_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(header([(0, 4672, 16)]))

    def test_cross_section_directory_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(header([(0, 4480, 800)]))

    def test_header_crossing_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(header([(0, 496, 32)]))

    def test_certificate_inside_section_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(header([(4, 512, 64)], count=5))

    def test_certificate_misalignment_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(header([(4, 1540, 64)], count=5))

    def test_certificate_past_eof_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(header([(4, 2040, 32)], count=5))

    def test_tiny_optional_header_rejected(self):
        with self.assertRaises(PEDataDirectoryError):
            self.check(b"\x00" * 110)


if __name__ == "__main__":
    unittest.main()
