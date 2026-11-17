"""R503: read-position receipts for synthetic WIN_CERTIFICATE tables.

Only inert bytes/temporary files are used; this is structural, not Authenticode.
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
    optional = bytearray(240)
    struct.pack_into("<I", optional, 108, 5)
    struct.pack_into("<II", optional, 144, _START, size)
    return bytes(optional)


class CertificateReadPositionR503(unittest.TestCase):
    def setUp(self):
        self.table = _record(b"A") + _record(b"ABCDEFGH")
        self.image = bytes(_START) + self.table
        self.optional = _optional(len(self.table))

    def verify(self, stream):
        verify_certificate_table(stream, self.optional, file_size=len(self.image))

    def assert_redacted(self, stream):
        caught = None
        try:
            self.verify(stream)
        except PECertificateError as exc:
            caught = exc
        self.assertIsNotNone(caught)
        self.assertEqual(str(caught), _ERROR)
        self.assertIsNone(caught.__cause__)
        self.assertIsNone(caught.__context__)

    def test_memory_file_advances_exactly_and_accepts(self):
        self.verify(BytesIO(self.image))

    def test_unbuffered_native_file_advances_exactly_and_accepts(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "inert-pe-data"
            path.write_bytes(self.image)
            with path.open("rb", buffering=0) as stream:
                self.verify(stream)

    def _bad_tell_at(self, target, mode):
        class FalseTell(BytesIO):
            def tell(self):
                offset = super().tell()
                if offset == target:
                    return (offset + 1) if mode == "wrong" else None
                return offset
        self.assert_redacted(FalseTell(self.image))

    def test_header_wrong_postread_position_rejected(self):
        self._bad_tell_at(_START + 8, "wrong")

    def _bad_tell_call(self, invocation):
        class WrongCall(BytesIO):
            calls = 0
            def tell(self):
                self.calls += 1
                offset = super().tell()
                return offset + 1 if self.calls == invocation else offset
        self.assert_redacted(WrongCall(self.image))

    def test_tail_wrong_postread_position_rejected(self):
        self._bad_tell_call(2)

    def test_padding_wrong_postread_position_rejected(self):
        self._bad_tell_call(3)

    def test_second_record_header_wrong_postread_position_rejected(self):
        self._bad_tell_call(4)

    def test_none_postread_position_rejected(self):
        self._bad_tell_at(_START + 8, "none")

    def test_boolean_position_rejected_even_when_equal_to_one(self):
        class BooleanTell(BytesIO):
            def tell(self):
                return True
        self.assert_redacted(BooleanTell(self.image))

    def test_subclass_position_rejected_without_invoking_comparison(self):
        class HostileInt(int):
            def __eq__(self, other):
                raise AssertionError("unsafe comparison")
        class SubclassTell(BytesIO):
            def tell(self):
                return HostileInt(super().tell())
        self.assert_redacted(SubclassTell(self.image))

    def test_private_position_error_redacted_without_chain(self):
        class PrivateTell(BytesIO):
            def tell(self):
                raise RuntimeError("C:/private/client-claim.csv")
        self.assert_redacted(PrivateTell(self.image))

    def test_read_returns_right_bytes_without_advancing_is_rejected(self):
        class DetachedRead(BytesIO):
            def read(self, n=-1):
                position = super().tell()
                content = super().read(n)
                super().seek(position)
                return content
        self.assert_redacted(DetachedRead(self.image))

    def test_false_position_on_second_record_rejected(self):
        self._bad_tell_at(_START + len(_record(b"A")) + 8, "none")

    def test_keyboard_interrupt_from_tell_propagates(self):
        class Interrupted(BytesIO):
            def tell(self):
                raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            self.verify(Interrupted(self.image))

    def test_unsigned_candidate_does_not_touch_stream(self):
        class Unreadable:
            def seek(self, *_):
                raise AssertionError("must not seek")
            def tell(self):
                raise AssertionError("must not tell")
        optional = bytearray(240)
        struct.pack_into("<I", optional, 108, 0)
        verify_certificate_table(Unreadable(), bytes(optional), file_size=0)


if __name__ == "__main__":
    unittest.main()
