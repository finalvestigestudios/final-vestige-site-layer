"""Synthetic WIN_CERTIFICATE framing regressions; never execute image bytes."""
from __future__ import annotations

from io import BytesIO
import struct
import unittest

from pe_certificate_guard_r496 import (
    MAX_CERTIFICATE_RECORDS, PECertificateError, verify_certificate_table,
)


def optional_at(offset=0, size=0, *, count=5):
    raw = bytearray(240)
    struct.pack_into("<I", raw, 108, count)
    if count >= 5:
        struct.pack_into("<II", raw, 144, offset, size)
    return bytes(raw)


def certificate(payload=b"A" * 8, *, revision=0x0200, cert_type=2,
                declared_length=None):
    length = len(payload) + 8 if declared_length is None else declared_length
    raw = struct.pack("<IHH", length, revision, cert_type) + payload
    return raw + b"\0" * (-len(raw) % 8)


def verify(table=b"", *, offset=1024, declared_size=None, optional=None,
           file_size=None):
    image = bytes(offset) + table
    size = len(table) if declared_size is None else declared_size
    if optional is None:
        optional = optional_at(offset, size)
    verify_certificate_table(BytesIO(image), optional,
                             file_size=len(image) if file_size is None else file_size)


class PECertificateR496(unittest.TestCase):
    def test_unsigned_no_certificate_is_accepted(self):
        verify(optional=optional_at())

    def test_directory_count_below_five_is_accepted(self):
        verify(optional=optional_at(count=4))

    def test_single_framed_certificate_is_accepted(self):
        verify(certificate())

    def test_multiple_framed_certificates_are_accepted(self):
        verify(certificate(b"X") + certificate(b"Y" * 12))

    def test_non_multiple_of_eight_certificate_length_uses_padding(self):
        verify(certificate(b"P" * 9))

    def test_arbitrary_padding_is_not_misreported_as_signature_verification(self):
        verify(certificate(b"P")[:-7] + b"Z" * 7)

    def test_blob_that_is_not_win_certificate_is_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(b"Z" * 64)

    def test_empty_record_payload_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(certificate(b""))

    def test_record_overrunning_table_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(certificate(b"A" * 8, declared_length=100))

    def test_trailing_partial_header_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(certificate() + b"\0" * 8)

    def test_obsolete_revision_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(certificate(revision=0x0100))

    def test_non_pkcs_certificate_type_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(certificate(cert_type=1))

    def test_misaligned_table_length_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(certificate(), declared_size=15)

    def test_misaligned_file_offset_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(certificate(), offset=1025)

    def test_directory_past_file_end_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(certificate(), declared_size=32)

    def test_table_over_limit_rejected_without_allocating_large_buffer(self):
        with self.assertRaises(PECertificateError):
            verify(optional=optional_at(1024, 8 * 1024 * 1024 + 8),
                   file_size=16 * 1024 * 1024)

    def test_too_many_certificate_records_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(certificate(b"A") * (MAX_CERTIFICATE_RECORDS + 1))

    def test_directory_truncated_in_optional_header_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(optional=b"\0" * 110)

    def test_directory_count_exceeding_sixteen_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(optional=optional_at(count=17))

    def test_not_even_a_complete_header_rejected(self):
        with self.assertRaises(PECertificateError):
            verify(b"B" * 4, declared_size=8, file_size=1032)

    def test_short_read_fails_closed(self):
        class ShortReader(BytesIO):
            def read(self, n=-1):
                return super().read(4 if n == 8 else n)
        with self.assertRaises(PECertificateError):
            verify_certificate_table(
                ShortReader(bytes(1024) + certificate()),
                optional_at(1024, 16), file_size=1040)

    def test_private_io_error_is_redacted(self):
        class FailingReader:
            def seek(self, offset):
                raise OSError("private file/path/stays hidden")
        with self.assertRaisesRegex(PECertificateError, "PE certificate table rejected") as caught:
            verify_certificate_table(FailingReader(), optional_at(1024, 16),
                                     file_size=1040)
        self.assertNotIn("private", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)


if __name__ == "__main__":
    unittest.main()
