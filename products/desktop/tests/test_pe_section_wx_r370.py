"""R370: reject writable+executable sections in six-app Windows candidates.

All files below are inert synthetic PE header fixtures, never actual programs.
The original candidates are neither built, run, scanned nor distributed here.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import tempfile
import unittest

from pe_image_guard import PEFormatError, verify_amd64_pe

TEXT_RX = 0x60000020  # CODE, EXECUTE, READ
DATA_RW = 0xC0000040  # INITIALIZED_DATA, READ, WRITE
READONLY = 0x40000040
TEXT_RWX = 0xE0000020
DATA_RWX = 0xE0000040


def make_pe(flags=(TEXT_RX,), *, raw_sections=None) -> bytes:
    """PE32+ with individually aligned sections; physically inert bytes."""
    if raw_sections is None:
        raw_sections = (True,) * len(flags)
    if len(flags) != len(raw_sections) or not 1 <= len(flags) <= 4:
        raise ValueError("Bad test fixture")
    header_size = ((0x98 + 0xF0 + 40 * len(flags) + 0x1FF) // 0x200) * 0x200
    header = bytearray(header_size + 0x200 * sum(raw_sections))
    header[:2] = b"MZ"
    struct.pack_into("<I", header, 0x3C, 0x80)
    header[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", header, 0x84,
                     0x8664, len(flags), 0, 0, 0, 0xF0, 0x22)
    opt = 0x98
    struct.pack_into("<H", header, opt, 0x20B)
    struct.pack_into("<I", header, opt+16, 0x1000)  # RX entry point
    struct.pack_into("<II", header, opt+32, 0x1000, 0x200)
    struct.pack_into("<II", header, opt+56, (len(flags)+1)*0x1000, header_size)
    struct.pack_into("<H", header, opt+68, 2)  # GUI
    struct.pack_into("<I", header, opt+108, 16)
    raw_at = header_size
    for i, (section_flags, backed) in enumerate(zip(flags, raw_sections)):
        offset = opt + 0xF0 + i*40
        header[offset:offset+8] = (b'.text' if i == 0 else b'.data' if i == 1 else b'.rdata')[:8].ljust(8,b'\0')
        struct.pack_into("<IIII", header, offset+8,
                         0x100, (i+1)*0x1000, 0x200 if backed else 0,
                         raw_at if backed else 0)
        struct.pack_into("<I", header, offset+36, section_flags)
        if backed:
            raw_at += 0x200
    return bytes(header)


class WritableExecutableSectionsR370(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r370-synthetic-pe-")
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "inert-test-fixture.exe"

    def check(self, flags, *, raw_sections=None, reject=False):
        body = make_pe(flags, raw_sections=raw_sections)
        self.file.write_bytes(body)
        before = hashlib.sha256(body).hexdigest()
        if reject:
            with self.assertRaisesRegex(PEFormatError, "writable executable") as caught:
                verify_amd64_pe(self.file)
            self.assertNotIn(str(self.file), str(caught.exception))
        else:
            self.assertIsNone(verify_amd64_pe(self.file))
        self.assertEqual(hashlib.sha256(self.file.read_bytes()).hexdigest(), before)

    def test_single_rx_entry_allowed(self): self.check((TEXT_RX,))
    def test_rx_code_and_rw_data_allowed(self): self.check((TEXT_RX, DATA_RW))
    def test_rx_code_and_readonly_data_allowed(self): self.check((TEXT_RX, READONLY))
    def test_rx_and_rw_and_ro_allowed(self): self.check((TEXT_RX, DATA_RW, READONLY))
    def test_unbacked_rw_data_allowed(self): self.check((TEXT_RX, DATA_RW), raw_sections=(True,False))
    def test_wx_in_entry_text_rejected(self): self.check((TEXT_RWX,), reject=True)
    def test_wx_second_nonentry_section_rejected(self): self.check((TEXT_RX,DATA_RWX),reject=True)
    def test_wx_third_nonentry_section_rejected(self): self.check((TEXT_RX,DATA_RW,DATA_RWX),reject=True)
    def test_wx_fourth_nonentry_section_rejected(self): self.check((TEXT_RX,READONLY,DATA_RW,DATA_RWX),reject=True)
    def test_unbacked_wx_section_rejected(self): self.check((TEXT_RX,DATA_RWX),raw_sections=(True,False),reject=True)
    def test_unbacked_wx_third_section_rejected(self): self.check((TEXT_RX,DATA_RW,DATA_RWX),raw_sections=(True,True,False),reject=True)
    def test_wx_without_code_bit_rejected(self): self.check((TEXT_RX,0xE0000000),reject=True)
    def test_wx_without_read_bit_rejected(self): self.check((TEXT_RX,0xA0000040),reject=True)
    def test_wx_with_discardable_bit_rejected(self): self.check((TEXT_RX,0xE2000040),reject=True)
    def test_read_and_write_without_exec_remains_allowed(self): self.check((TEXT_RX,0xC0000000))
    def test_exec_and_read_without_write_remains_allowed(self): self.check((TEXT_RX,0x60000000))
    def test_exec_only_without_write_remains_allowed(self): self.check((TEXT_RX,0x20000000))

    def test_non_amd64_still_rejected(self):
        body=bytearray(make_pe((TEXT_RX,)))
        struct.pack_into("<H",body,0x84,0x14C)
        self.file.write_bytes(body)
        with self.assertRaises(PEFormatError): verify_amd64_pe(self.file)

    def test_missing_executable_entry_still_rejected(self):
        body=bytearray(make_pe((DATA_RW,)))
        self.file.write_bytes(body)
        with self.assertRaises(PEFormatError): verify_amd64_pe(self.file)

    def test_multiple_candidate_sections_still_bounded(self):
        body=bytearray(make_pe((TEXT_RX,DATA_RW,READONLY,TEXT_RX)))
        self.file.write_bytes(body)
        self.assertIsNone(verify_amd64_pe(self.file))


if __name__ == "__main__":
    unittest.main()
