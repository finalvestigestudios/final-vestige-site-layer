"""R17: adversarial PE32+ structure rejection using inert synthetic bytes."""
import os
import tempfile
import unittest
from pathlib import Path

from pe_image_guard import PEFormatError, verify_amd64_pe
from pe_fixture_r17 import synthetic_pe64


class PEImageGuardR17(unittest.TestCase):
    def setUp(self):
        context = tempfile.TemporaryDirectory(prefix="fvs-pe-r17-")
        self.addCleanup(context.cleanup)
        self.target = Path(context.name) / "LedgerDiffLite.exe"

    def validate(self, raw):
        self.target.write_bytes(raw)
        verify_amd64_pe(self.target)

    def reject(self, raw):
        self.target.write_bytes(raw)
        with self.assertRaises(PEFormatError):
            verify_amd64_pe(self.target)

    def mutate(self, start, size, value, *, raw=None):
        buf = bytearray(synthetic_pe64() if raw is None else raw)
        buf[start:start + size] = value.to_bytes(size, "little")
        return bytes(buf)

    def test_structurally_complete_mock_passes_without_execution(self):
        self.validate(synthetic_pe64())

    def test_amd64_gui_and_console_only(self):
        self.validate(self.mutate(220, 2, 3))
        for machine in (0x014C, 0xAA64, 0):
            with self.subTest(machine=machine):
                self.reject(synthetic_pe64(machine=machine))

    def test_rejects_truncated_and_missing_signatures(self):
        for raw in (b"", b"MZ", synthetic_pe64()[:200],
                    b"XX" + synthetic_pe64()[2:],
                    synthetic_pe64(signature=b"FAIL")):
            with self.subTest(length=len(raw)):
                self.reject(raw)

    def test_rejects_bad_e_lfanew(self):
        for offset in (0, 32, 65537, 0xffffffff):
            with self.subTest(offset=offset):
                self.reject(self.mutate(0x3C, 4, offset))

    def test_rejects_empty_or_unreasonably_many_sections(self):
        for count in (0, 97, 65535):
            with self.subTest(count=count):
                self.reject(self.mutate(134, 2, count))
        self.reject(self.mutate(134, 2, 32))

    def test_rejects_non_executable_dll_and_driver_images(self):
        for flags in (0, 0x0020, 0x2022, 0x1022):
            with self.subTest(flags=flags):
                self.reject(self.mutate(150, 2, flags))

    def test_rejects_optional_header_bounds_and_magic(self):
        for size in (0, 111, 4097, 65535):
            with self.subTest(size=size):
                self.reject(self.mutate(148, 2, size))
        self.reject(synthetic_pe64(opt=0x10B))

    def test_rejects_no_entrypoint(self):
        self.reject(self.mutate(168, 4, 0))

    def test_rejects_bad_file_and_section_alignments(self):
        for start, value in ((184, 0), (188, 0), (188, 513),
                             (184, 128), (188, 8192)):
            with self.subTest(offset=start, value=value):
                self.reject(self.mutate(start, 4, value))

    def test_rejects_bad_headers_and_image_sizes(self):
        for start, value in ((212, 100), (212, 4096),
                             (208, 128), (208, 0)):
            with self.subTest(offset=start, value=value):
                self.reject(self.mutate(start, 4, value))

    def test_rejects_kernel_or_unknown_subsystems(self):
        for subsystem in (0, 1, 9, 10, 65535):
            with self.subTest(subsystem=subsystem):
                self.reject(self.mutate(220, 2, subsystem))

    def test_rejects_section_raw_bounds_and_missing_code(self):
        section = 392
        for start, value in ((section + 20, 0), (section + 20, 0xffffff00),
                             (section + 16, 0xffffff00),
                             (section + 36, 0x40000040),
                             (section + 16, 0)):
            with self.subTest(offset=start, value=value):
                self.reject(self.mutate(start, 4, value))

    def test_rejects_non_regular_file_and_symlink_if_supported(self):
        with self.assertRaises(PEFormatError):
            verify_amd64_pe(self.target.parent)
        outside = self.target.parent / "real.exe"
        outside.write_bytes(synthetic_pe64())
        try:
            self.target.symlink_to(outside)
        except (NotImplementedError, OSError):
            self.skipTest("Symlink creation unavailable")
        if hasattr(os, "O_NOFOLLOW"):
            with self.assertRaises(PEFormatError):
                verify_amd64_pe(self.target)


if __name__ == "__main__":
    unittest.main()
