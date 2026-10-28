"""R18: reject forged PE entry points and overlapping on-disk/mapped sections."""
import tempfile
import unittest
from pathlib import Path

from pe_image_guard import PEFormatError, verify_amd64_pe
from pe_fixture_r17 import synthetic_pe64


def change(raw, offset, size, value):
    data = bytearray(raw)
    data[offset:offset + size] = value.to_bytes(size, "little")
    return bytes(data)


def two_sections(*, second_rva=0x2000, second_file_offset=0x400,
                 second_flags=0x40000040):
    data = bytearray(synthetic_pe64())
    data.extend(b"\0" * 512)
    data[134:136] = (2).to_bytes(2, "little")
    data[208:212] = (0x3000).to_bytes(4, "little")
    section = 392 + 40
    data[section:section + 8] = b".data\0\0\0"
    for relative, number in ((8, 0x180), (12, second_rva),
                             (16, 0x200), (20, second_file_offset),
                             (36, second_flags)):
        data[section + relative:section + relative + 4] = number.to_bytes(4, "little")
    return bytes(data)


class PEImageMappingR18(unittest.TestCase):
    def setUp(self):
        location = tempfile.TemporaryDirectory(prefix="fvs-pe-r18-")
        self.addCleanup(location.cleanup)
        self.path = Path(location.name) / "LedgerDiffLite.exe"

    def check(self, raw, accepted):
        self.path.write_bytes(raw)
        if accepted:
            verify_amd64_pe(self.path)
        else:
            with self.assertRaises(PEFormatError):
                verify_amd64_pe(self.path)

    def test_original_fixture_and_backed_offset_pass(self):
        self.check(synthetic_pe64(), True)
        self.check(change(synthetic_pe64(), 168, 4, 0x117F), True)

    def test_pyinstaller_style_overlay_remains_permitted(self):
        # A one-file Python packager may append data beyond the PE sections.
        self.check(synthetic_pe64() + b"OVERLAY" * 100, True)

    def test_rejects_entry_in_headers_or_unmapped_address(self):
        for entry in (1, 0x100, 0x1200, 0x1800, 0x3000, 0xFFFFFFFF):
            with self.subTest(entry=hex(entry)):
                self.check(change(synthetic_pe64(), 168, 4, entry), False)

    def test_rejects_entry_in_raw_padding_beyond_virtual_code(self):
        for entry in (0x1180, 0x1190, 0x11FF):
            with self.subTest(entry=hex(entry)):
                self.check(change(synthetic_pe64(), 168, 4, entry), False)

    def test_rejects_entry_in_zero_fill_without_backing(self):
        raw = change(synthetic_pe64(), 392 + 8, 4, 0x500)
        self.check(change(raw, 168, 4, 0x1300), False)

    def test_two_disjoint_sections_are_accepted(self):
        self.check(two_sections(), True)
        self.check(change(two_sections(), 168, 4, 0x1001), True)

    def test_rejects_entry_in_non_executable_second_section(self):
        self.check(change(two_sections(), 168, 4, 0x2000), False)

    def test_rejects_overlapping_virtual_section_ranges(self):
        self.check(two_sections(second_rva=0x1000), False)
        self.check(two_sections(second_rva=0x0000), False)

    def test_rejects_overlapping_on_disk_section_ranges(self):
        self.check(two_sections(second_file_offset=0x200), False)

    def test_rejects_misaligned_section_coordinates(self):
        for offset, value in ((392 + 12, 0x1100), (392 + 20, 0x201),
                              (392 + 16, 0x201)):
            with self.subTest(offset=offset, value=value):
                self.check(change(synthetic_pe64(), offset, 4, value), False)

    def test_rejects_image_size_not_covering_last_section(self):
        for image_size in (0x1000, 0x1001, 0x2001):
            with self.subTest(image_size=image_size):
                self.check(change(synthetic_pe64(), 208, 4, image_size), False)

    def test_rejects_unaligned_header_size(self):
        self.check(change(synthetic_pe64(), 212, 4, 0x201), False)

    def test_zero_length_mapped_section_is_not_accepted(self):
        raw = change(synthetic_pe64(), 392 + 8, 4, 0)
        self.check(change(raw, 392 + 16, 4, 0), False)


if __name__ == "__main__":
    unittest.main()
