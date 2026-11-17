"""R499 synthetic byte-only outer WIN_CERTIFICATE alignment checks.

This does NOT prove signature validity, signing trust or malware safety.
"""
from __future__ import annotations

from io import BytesIO
import struct
import unittest

from pe_certificate_guard_r496 import PECertificateError, verify_certificate_table


def certificate(payload=b"x", *, pad=None):
    length = len(payload) + 8
    n = (-length) % 8
    if pad is None:
        pad = b"\0" * n
    if len(pad) != n:
        raise ValueError("fixture padding length must match alignment")
    return struct.pack("<IHH", length, 0x0200, 2) + payload + pad


def optional(size, *, offset=1024):
    data = bytearray(240)
    struct.pack_into("<I", data, 108, 5)
    struct.pack_into("<II", data, 144, offset, size)
    return bytes(data)


def check(table, *, stream_cls=BytesIO):
    verify_certificate_table(stream_cls(bytes(1024) + table), optional(len(table)), file_size=1024 + len(table))


class OuterPaddingR499(unittest.TestCase):
    def test_unsigned_absence_still_passes(self):
        verify_certificate_table(BytesIO(b""), optional(0, offset=0), file_size=0)

    def test_no_padding_still_passes(self):
        check(certificate(b"A" * 8))

    def test_zero_padding_from_one_to_seven_bytes_passes(self):
        for n in range(1, 8):
            with self.subTest(padding_bytes=n):
                check(certificate(b"A" * (8 - n)))

    def test_any_nonzero_byte_in_padding_fails(self):
        for index in range(7):
            with self.subTest(index=index):
                pad = bytearray(7)
                pad[index] = 0x5a
                with self.assertRaises(PECertificateError):
                    check(certificate(b"A", pad=bytes(pad)))

    def test_second_record_dirty_padding_rejected(self):
        with self.assertRaises(PECertificateError):
            check(certificate(b"X" * 8) + certificate(b"Y", pad=b"\0" * 6 + b"1"))

    def test_middle_record_dirty_padding_rejected(self):
        with self.assertRaises(PECertificateError):
            check(certificate(b"X") + certificate(b"Y", pad=b"1" + b"\0" * 6) + certificate(b"Z"))

    def test_payload_not_conflated_with_outer_padding(self):
        # This is only a structural guard; payload may be any inert bytes.
        check(certificate(b"NONZERO!") + certificate(b"\xff"))

    def test_short_padding_read_fails_closed(self):
        class ShortPadding(BytesIO):
            def read(self, n=-1):
                return super().read(n - 1 if n == 7 else n)
        with self.assertRaises(PECertificateError):
            check(certificate(b"X"), stream_cls=ShortPadding)

    def test_private_padding_io_error_has_no_exception_chain(self):
        class ErrorOnPadding(BytesIO):
            def read(self, n=-1):
                if n == 7:
                    raise OSError("C:/private/financial/ledger.csv")
                return super().read(n)
        with self.assertRaises(PECertificateError) as caught:
            check(certificate(b"X"), stream_cls=ErrorOnPadding)
        self.assertEqual(str(caught.exception), "PE certificate table rejected")
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)

    def test_padding_read_never_exceeds_seven_bytes(self):
        sizes = []
        class Reader(BytesIO):
            def read(self, n=-1):
                sizes.append(n)
                return super().read(n)
        check(certificate(b"Z"), stream_cls=Reader)
        self.assertEqual(sizes, [8, 1, 7])

    def test_short_header_still_fails_closed(self):
        with self.assertRaises(PECertificateError):
            check(b"A" * 8)


if __name__ == "__main__":
    unittest.main()
