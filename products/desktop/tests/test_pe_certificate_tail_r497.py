"""R497: certificate record tails must physically exist on the held stream.

Synthetic inert data only: no Windows executable or signature is executed.
"""
from __future__ import annotations

from io import BytesIO
import struct
import unittest

from pe_certificate_guard_r496 import (
    MAX_CERTIFICATE_RECORDS, PECertificateError, verify_certificate_table,
)


_START = 1024
_ERROR = "PE certificate table rejected"


def _optional(size: int, start: int = _START) -> bytes:
    value = bytearray(240)
    struct.pack_into("<I", value, 108, 5)
    struct.pack_into("<II", value, 144, start, size)
    return bytes(value)


def _record(payload: bytes = b"DATA", *, padding: bytes | None = None) -> bytes:
    raw = struct.pack("<IHH", len(payload) + 8, 0x0200, 2) + payload
    pad_length = -len(raw) % 8
    return raw + (bytes(pad_length) if padding is None else padding)


def _verify(physical_table: bytes, *, declared_size: int | None = None,
            declared_file_size: int | None = None) -> None:
    size = len(physical_table) if declared_size is None else declared_size
    stream = BytesIO(bytes(_START) + physical_table)
    verify_certificate_table(
        stream, _optional(size),
        file_size=_START + len(physical_table)
        if declared_file_size is None else declared_file_size,
    )


class R497CertificateTailCustody(unittest.TestCase):
    def test_valid_complete_record_remains_accepted(self):
        _verify(_record(b"ABCDEFGH"))

    def test_valid_zero_padding_remains_accepted(self):
        # R499 tightened PE/COFF semantics: only zero-filled outer padding
        # is accepted. Retain this inherited R497 tail-custody test under
        # the current contract instead of expecting a known-bad image to pass.
        _verify(_record(b"A", padding=b"\x00" * 7))

    def test_nonzero_outer_padding_rejected_after_r499(self):
        # The former positive fixture used seven 'z' bytes. That should now
        # fail closed, while remaining separate from the tail-truncation checks.
        with self.assertRaisesRegex(PECertificateError, _ERROR):
            _verify(_record(b"A", padding=b"z" * 7))

    def test_two_complete_records_remain_accepted(self):
        _verify(_record(b"A") + _record(b"BCD"))

    def test_maximum_number_of_complete_records_remains_accepted(self):
        _verify(_record(b"X") * MAX_CERTIFICATE_RECORDS)

    def test_header_without_payload_rejected_even_if_claimed_file_size_fits(self):
        header = struct.pack("<IHH", 16, 0x0200, 2)
        with self.assertRaisesRegex(PECertificateError, _ERROR):
            _verify(header, declared_size=16, declared_file_size=_START + 16)

    def test_partial_payload_rejected_even_if_claimed_file_size_fits(self):
        header = struct.pack("<IHH", 16, 0x0200, 2)
        with self.assertRaisesRegex(PECertificateError, _ERROR):
            _verify(header + b"ABCD", declared_size=16,
                    declared_file_size=_START + 16)

    def test_missing_one_byte_of_payload_rejected(self):
        header = struct.pack("<IHH", 16, 0x0200, 2)
        with self.assertRaisesRegex(PECertificateError, _ERROR):
            _verify(header + b"A" * 7, declared_size=16,
                    declared_file_size=_START + 16)

    def test_missing_only_alignment_padding_rejected(self):
        full = _record(b"a")
        with self.assertRaisesRegex(PECertificateError, _ERROR):
            _verify(full[:-1], declared_size=len(full),
                    declared_file_size=_START + len(full))

    def test_second_record_missing_tail_rejected(self):
        good = _record(b"12345678")
        bad_header = struct.pack("<IHH", 16, 0x0200, 2)
        with self.assertRaisesRegex(PECertificateError, _ERROR):
            _verify(good + bad_header + b"ABCD", declared_size=32,
                    declared_file_size=_START + 32)

    def test_tail_short_read_rejected(self):
        class VanishingTail(BytesIO):
            def read(self, n=-1):
                if n == 1:
                    return b""
                return super().read(n)

        with self.assertRaisesRegex(PECertificateError, _ERROR):
            verify_certificate_table(
                VanishingTail(bytes(_START) + _record(b"ABCDEFGH")),
                _optional(16), file_size=_START + 16)

    def test_tail_read_io_error_redacted_without_exception_chain(self):
        class PrivateTail(BytesIO):
            def read(self, n=-1):
                if n == 1:
                    raise OSError("SECRET customer directory")
                return super().read(n)

        caught = None
        try:
            verify_certificate_table(
                PrivateTail(bytes(_START) + _record(b"ABCDEFGH")),
                _optional(16), file_size=_START + 16)
        except PECertificateError as exc:
            caught = exc
        self.assertIsNotNone(caught)
        self.assertEqual(str(caught), _ERROR)
        self.assertIsNone(caught.__cause__)
        self.assertIsNone(caught.__context__)

    def test_unsigned_table_does_not_touch_stream(self):
        class NotReadable:
            def seek(self, *_):
                raise AssertionError("unsigned file must not be read")
        verify_certificate_table(NotReadable(), _optional(0, start=0), file_size=0)


if __name__ == "__main__":
    unittest.main()
