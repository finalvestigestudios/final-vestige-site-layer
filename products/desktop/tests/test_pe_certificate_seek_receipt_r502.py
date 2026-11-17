"""R502 seek-position custody for synthetic WIN_CERTIFICATE tables.

No EXE or real PKCS#7 payload is executed; source-only preflight, not trust.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import struct
import tempfile
import unittest

from pe_certificate_guard_r496 import PECertificateError, verify_certificate_table

_START = 1024
_ERROR = "PE certificate table rejected"


def _record(payload: bytes) -> bytes:
    length = 8 + len(payload)
    return struct.pack("<IHH", length, 0x0200, 2) + payload + bytes(-length % 8)


def _optional(size: int) -> bytes:
    header = bytearray(240)
    struct.pack_into("<I", header, 108, 5)
    struct.pack_into("<II", header, 144, _START, size)
    return bytes(header)


def _check(stream, table: bytes):
    verify_certificate_table(stream, _optional(len(table)), file_size=_START + len(table))


class CertificateSeekReceiptR502(unittest.TestCase):
    def setUp(self):
        self.table = _record(b"A") + _record(b"ABCDEFGH")
        self.bytes = bytes(_START) + self.table

    def test_native_memory_stream_accepts_two_records(self):
        _check(BytesIO(self.bytes), self.table)

    def test_native_unbuffered_file_descriptor_accepts_two_records(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "inert-structural-candidate"
            path.write_bytes(self.bytes)
            with path.open("rb", buffering=0) as stream:
                _check(stream, self.table)

    def test_header_wrong_seek_receipt_fails_closed(self):
        self._reject_bad_seek(_START)

    def test_tail_wrong_seek_receipt_fails_closed(self):
        self._reject_bad_seek(_START + len(_record(b"A")) - 1)

    def test_padding_wrong_seek_receipt_fails_closed(self):
        self._reject_bad_seek(_START + 9)

    def test_second_record_header_wrong_seek_receipt_fails_closed(self):
        self._reject_bad_seek(_START + len(_record(b"A")))

    def _reject_bad_seek(self, target):
        class WrongSeek(BytesIO):
            def seek(self, offset, whence=0):
                super().seek(offset, whence)
                return offset + 1 if offset == target else offset
        self.assert_private_failure(WrongSeek(self.bytes))

    def test_boolean_seek_receipt_rejected_not_treated_as_int(self):
        class BooleanSeek(BytesIO):
            def seek(self, offset, whence=0):
                super().seek(offset, whence)
                return True
        self.assert_private_failure(BooleanSeek(self.bytes))

    def test_int_subclass_receipt_never_invokes_custom_comparison(self):
        class HostileInt(int):
            def __eq__(self, other):
                raise AssertionError("private comparison hook executed")
        class SubclassSeek(BytesIO):
            def seek(self, offset, whence=0):
                super().seek(offset, whence)
                return HostileInt(offset)
        self.assert_private_failure(SubclassSeek(self.bytes))

    def test_none_seek_receipt_rejected(self):
        class NoneSeek(BytesIO):
            def seek(self, offset, whence=0):
                super().seek(offset, whence)
                return None
        self.assert_private_failure(NoneSeek(self.bytes))

    def test_private_seek_exception_redacted_without_chain(self):
        class PrivateSeek(BytesIO):
            def seek(self, offset, whence=0):
                raise OSError("C:/private/client-ledger.csv")
        self.assert_private_failure(PrivateSeek(self.bytes))

    def test_private_read_exception_redacted_without_chain(self):
        class PrivateRead(BytesIO):
            def read(self, n=-1):
                raise RuntimeError("C:/private/account-numbers.csv")
        self.assert_private_failure(PrivateRead(self.bytes))

    def test_keyboard_interrupt_propagates(self):
        class Interrupted(BytesIO):
            def seek(self, offset, whence=0):
                raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            _check(Interrupted(self.bytes), self.table)

    def test_unsigned_candidate_does_not_seek(self):
        class Unreadable:
            def seek(self, *_):
                raise AssertionError("must not seek unsigned candidate")
        optional = bytearray(240)
        struct.pack_into("<I", optional, 108, 0)
        verify_certificate_table(Unreadable(), bytes(optional), file_size=0)

    def assert_private_failure(self, stream):
        caught = None
        try:
            _check(stream, self.table)
        except PECertificateError as exc:
            caught = exc
        self.assertIsNotNone(caught)
        self.assertEqual(str(caught), _ERROR)
        self.assertIsNone(caught.__cause__)
        self.assertIsNone(caught.__context__)


if __name__ == "__main__":
    unittest.main()
