"""R501: inherited certificate-tail tests and zero-padding policy agree.

Synthetic BytesIO only. Neither Authenticode verification nor EXE execution.
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


def _record(payload: bytes, *, padding: bytes | None = None) -> bytes:
    length = 8 + len(payload)
    required_padding = -length % 8
    if padding is None:
        padding = bytes(required_padding)
    if len(padding) != required_padding:
        raise ValueError("Invalid test fixture padding size")
    return struct.pack("<IHH", length, 0x0200, 2) + payload + padding


def _header(table_size: int) -> bytes:
    raw = bytearray(240)
    struct.pack_into("<I", raw, 108, 5)
    struct.pack_into("<II", raw, 144, _START, table_size)
    return bytes(raw)


def _check(table: bytes, *, stream_factory=BytesIO) -> None:
    verify_certificate_table(stream_factory(bytes(_START) + table),
                             _header(len(table)), file_size=_START + len(table))


class PECertificateInheritedContractR501(unittest.TestCase):
    def test_one_to_seven_zero_padding_bytes_are_accepted(self):
        for n in range(1, 8):
            with self.subTest(padding=n):
                _check(_record(b"A" * (8 - n)))

    def test_all_nonzero_padding_positions_are_rejected(self):
        for n in range(1, 8):
            for index in range(n):
                with self.subTest(padding=n, index=index):
                    padding = bytearray(n)
                    padding[index] = 0x7A
                    with self.assertRaisesRegex(PECertificateError, _ERROR):
                        _check(_record(b"A" * (8 - n), padding=bytes(padding)))

    def test_no_padding_framing_accepted(self):
        _check(_record(b"ABCDEFGH"))

    def test_second_record_dirty_padding_rejected(self):
        table = _record(b"ABCDEFGH") + _record(b"A", padding=b"z" * 7)
        with self.assertRaisesRegex(PECertificateError, _ERROR):
            _check(table)

    def test_multiple_clean_records_accepted(self):
        table = _record(b"A") + _record(b"12345678") + _record(b"BCD")
        _check(table)

    def test_clean_record_cap_still_applies(self):
        table = _record(b"A") * MAX_CERTIFICATE_RECORDS
        _check(table)
        with self.assertRaisesRegex(PECertificateError, _ERROR):
            _check(table + _record(b"A"))

    def test_private_padding_io_failure_does_not_leak_context(self):
        class FaultyStream(BytesIO):
            def read(self, count=-1):
                if count == 7:
                    raise RuntimeError("C:/private/bank-transactions.csv")
                return super().read(count)
        with self.assertRaises(PECertificateError) as caught:
            _check(_record(b"A"), stream_factory=FaultyStream)
        self.assertEqual(str(caught.exception), _ERROR)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)

    def test_short_tail_read_still_rejected(self):
        class ShortTail(BytesIO):
            def read(self, count=-1):
                return b"" if count == 1 else super().read(count)
        with self.assertRaisesRegex(PECertificateError, _ERROR):
            _check(_record(b"ABCDEFGH"), stream_factory=ShortTail)


if __name__ == "__main__":
    unittest.main()
