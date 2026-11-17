"""R505 integration: PE image parser must use the bounded read-receipt helper."""
from __future__ import annotations

from io import BytesIO
import unittest
from unittest.mock import patch

import pe_image_guard as pe
from pe_header_receipt_r505 import PEHeaderReceiptError

_DATA = bytes(range(256)) * 4


class HeaderParserBindingR505(unittest.TestCase):
    def test_dos_nt_section_style_reads_use_helper(self):
        stream = BytesIO(_DATA)
        for offset, count in ((0, 64), (64, 24), (88, 240), (512, 40)):
            self.assertEqual(pe._read_at(stream, offset, count, len(_DATA)),
                             _DATA[offset:offset + count])

    def test_direct_parser_rejects_forged_seek_receipt(self):
        class WrongSeek(BytesIO):
            def seek(self, at, whence=0):
                super().seek(at, whence)
                return at + 1
        self.assert_private_failure(WrongSeek(_DATA))

    def test_direct_parser_rejects_disconnected_read_position(self):
        class Detached(BytesIO):
            def read(self, n=-1):
                at = super().tell()
                result = super().read(n)
                super().seek(at)
                return result
        self.assert_private_failure(Detached(_DATA))

    def test_direct_parser_rejects_mutable_bytearray_receipt(self):
        class Mutable(BytesIO):
            def read(self, n=-1):
                return bytearray(super().read(n))
        self.assert_private_failure(Mutable(_DATA))

    def test_direct_parser_redacts_private_stream_error_and_chain(self):
        class Private(BytesIO):
            def read(self, n=-1):
                raise OSError('C:/secret/ledger.csv')
        self.assert_private_failure(Private(_DATA))

    def test_direct_parser_preserves_bounds_diagnostic(self):
        with self.assertRaises(pe.PEFormatError) as cm:
            pe._read_at(BytesIO(_DATA), -1, 1, len(_DATA))
        self.assertEqual(str(cm.exception), 'PE header or section extends beyond file')
        self.assertIsNone(cm.exception.__cause__)
        self.assertIsNone(cm.exception.__context__)

    def test_parser_remaps_helper_error_without_chain(self):
        with patch.object(pe, 'read_exact_at', side_effect=PEHeaderReceiptError('PE file changed or was truncated during inspection')):
            self.assert_private_failure(BytesIO(_DATA))

    def test_keyboard_interrupt_still_propagates(self):
        class Interrupted(BytesIO):
            def tell(self):
                raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            pe._read_at(Interrupted(_DATA), 64, 24, len(_DATA))

    def assert_private_failure(self, stream):
        caught = None
        try:
            pe._read_at(stream, 64, 24, len(_DATA))
        except pe.PEFormatError as exc:
            caught = exc
        self.assertIsNotNone(caught)
        self.assertEqual(str(caught), 'PE file changed or was truncated during inspection')
        self.assertIsNone(caught.__cause__)
        self.assertIsNone(caught.__context__)


if __name__ == '__main__':
    unittest.main()
