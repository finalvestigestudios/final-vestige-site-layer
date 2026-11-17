"""R504: exact position/byte custody for DOS, NT and section-table reads."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import tempfile
import unittest

from pe_header_receipt_r505 import PEHeaderReceiptError, read_exact_at

_DATA = bytes(range(256)) * 4
_REDACTED = "PE file changed or was truncated during inspection"


class HeaderReceiptR504(unittest.TestCase):
    def read(self, stream, start=64, count=24, length=len(_DATA)):
        return read_exact_at(stream, start, count, length)

    def assert_redacted(self, stream):
        caught = None
        try:
            self.read(stream)
        except PEHeaderReceiptError as exc:
            caught = exc
        self.assertIsNotNone(caught)
        self.assertEqual(str(caught), _REDACTED)
        self.assertIsNone(caught.__cause__)
        self.assertIsNone(caught.__context__)

    def test_memory_stream_reads_expected_span(self):
        self.assertEqual(self.read(BytesIO(_DATA)), _DATA[64:88])

    def test_real_unbuffered_file_reads_expected_span(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic-pe-bytes'
            path.write_bytes(_DATA)
            with path.open('rb', buffering=0) as stream:
                self.assertEqual(self.read(stream), _DATA[64:88])

    def test_zero_byte_read_preserves_position_receipt(self):
        self.assertEqual(self.read(BytesIO(_DATA), start=128, count=0), b'')

    def test_final_byte_inside_size_is_accepted(self):
        self.assertEqual(self.read(BytesIO(_DATA), start=1023, count=1), _DATA[-1:])

    def test_outside_file_size_is_rejected_before_touching_stream(self):
        class NeverRead:
            def seek(self, *_):
                raise AssertionError('stream must remain untouched')
        with self.assertRaisesRegex(PEHeaderReceiptError, 'beyond file'):
            self.read(NeverRead(), 1023, 2)

    def test_negative_start_rejected_before_stream_access(self):
        with self.assertRaisesRegex(PEHeaderReceiptError, 'beyond file'):
            self.read(None, -1, 1)

    def test_negative_count_rejected_before_stream_access(self):
        with self.assertRaisesRegex(PEHeaderReceiptError, 'beyond file'):
            self.read(None, 64, -1)

    def test_bool_and_int_subclass_input_envelopes_rejected(self):
        for values in ((True, 2, len(_DATA)), (64, False, len(_DATA)),
                       (64, 1, True), (int_subclass(64), 2, len(_DATA))):
            with self.subTest(values=values):
                with self.assertRaisesRegex(PEHeaderReceiptError, 'beyond file'):
                    self.read(None, *values)

    def test_wrong_seek_receipt_rejected(self):
        class WrongSeek(BytesIO):
            def seek(self, offset, whence=0):
                super().seek(offset, whence)
                return offset + 1
        self.assert_redacted(WrongSeek(_DATA))

    def test_none_seek_receipt_rejected(self):
        class NoneSeek(BytesIO):
            def seek(self, offset, whence=0):
                super().seek(offset, whence)
                return None
        self.assert_redacted(NoneSeek(_DATA))

    def test_bool_seek_receipt_rejected(self):
        class BoolSeek(BytesIO):
            def seek(self, offset, whence=0):
                super().seek(offset, whence)
                return True
        self.assert_redacted(BoolSeek(_DATA))

    def test_hostile_seek_int_subclass_never_compared(self):
        class HostileSeek(BytesIO):
            def seek(self, offset, whence=0):
                super().seek(offset, whence)
                return int_subclass(offset)
        self.assert_redacted(HostileSeek(_DATA))

    def test_right_bytes_without_position_advance_rejected(self):
        class DetachedRead(BytesIO):
            def read(self, n=-1):
                prior = super().tell()
                result = super().read(n)
                super().seek(prior)
                return result
        self.assert_redacted(DetachedRead(_DATA))

    def test_wrong_postread_position_rejected(self):
        class WrongTell(BytesIO):
            def tell(self):
                return super().tell() + 1
        self.assert_redacted(WrongTell(_DATA))

    def test_none_postread_position_rejected(self):
        class NoneTell(BytesIO):
            def tell(self):
                return None
        self.assert_redacted(NoneTell(_DATA))

    def test_bool_postread_position_rejected(self):
        class BoolTell(BytesIO):
            def tell(self):
                return True
        self.assert_redacted(BoolTell(_DATA))

    def test_hostile_postread_int_subclass_never_compared(self):
        class HostileTell(BytesIO):
            def tell(self):
                return int_subclass(super().tell())
        self.assert_redacted(HostileTell(_DATA))

    def test_bytearray_read_receipt_rejected(self):
        class BytearrayRead(BytesIO):
            def read(self, n=-1):
                return bytearray(super().read(n))
        self.assert_redacted(BytearrayRead(_DATA))

    def test_hostile_bytes_subclass_read_receipt_rejected(self):
        class HostileBytes(bytes):
            def __len__(self):
                raise AssertionError('unexpected subclass hook')
        class SubclassRead(BytesIO):
            def read(self, n=-1):
                return HostileBytes(super().read(n))
        self.assert_redacted(SubclassRead(_DATA))

    def test_short_read_rejected_even_with_consistent_position(self):
        self.assert_redacted(BytesIO(_DATA[:66]))

    def test_private_seek_read_and_tell_errors_are_unchained(self):
        for method in ('seek', 'read', 'tell'):
            with self.subTest(method=method):
                class PrivateFault(BytesIO):
                    def seek(self, offset, whence=0):
                        if method == 'seek':
                            raise OSError('C:/secret/claim.csv')
                        return super().seek(offset, whence)
                    def read(self, n=-1):
                        if method == 'read':
                            raise RuntimeError('C:/secret/client-data.csv')
                        return super().read(n)
                    def tell(self):
                        if method == 'tell':
                            raise ValueError('C:/secret/source.csv')
                        return super().tell()
                self.assert_redacted(PrivateFault(_DATA))

    def test_keyboard_interrupt_propagates_from_each_stream_call(self):
        for method in ('seek', 'read', 'tell'):
            with self.subTest(method=method):
                class Interrupted(BytesIO):
                    def seek(self, offset, whence=0):
                        if method == 'seek':
                            raise KeyboardInterrupt()
                        return super().seek(offset, whence)
                    def read(self, n=-1):
                        if method == 'read':
                            raise KeyboardInterrupt()
                        return super().read(n)
                    def tell(self):
                        if method == 'tell':
                            raise KeyboardInterrupt()
                        return super().tell()
                with self.assertRaises(KeyboardInterrupt):
                    self.read(Interrupted(_DATA))


def int_subclass(value):
    class HostileInt(int):
        def __eq__(self, other):
            raise AssertionError('comparison hook invoked')
        def __lt__(self, other):
            raise AssertionError('ordering hook invoked')
    return HostileInt(value)


if __name__ == '__main__':
    unittest.main()
