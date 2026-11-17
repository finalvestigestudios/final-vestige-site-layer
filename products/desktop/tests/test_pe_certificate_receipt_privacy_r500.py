"""R500: redacted WIN_CERTIFICATE source faults and native stream receipts.

Only inert BytesIO fixtures; no executable or financial source is opened.
"""
from __future__ import annotations

from io import BytesIO
import struct
import unittest

from pe_certificate_guard_r496 import PECertificateError, verify_certificate_table


_FIXED = "PE certificate table rejected"


def _optional(size: int) -> bytes:
    raw = bytearray(240)
    struct.pack_into("<I", raw, 108, 5)
    struct.pack_into("<II", raw, 144, 1024, size)
    return bytes(raw)


def _record(payload: bytes = b"X") -> bytes:
    size = 8 + len(payload)
    return struct.pack("<IHH", size, 0x0200, 2) + payload + bytes(-size % 8)


def _check(stream, length=16):
    verify_certificate_table(stream, _optional(length), file_size=1024 + length)


def _stream(table=None):
    return BytesIO(bytes(1024) + (_record() if table is None else table))


class CertificateReceiptPrivacyR500(unittest.TestCase):
    def assert_rejected(self, stream):
        with self.assertRaises(PECertificateError) as caught:
            _check(stream)
        self.assertEqual(str(caught.exception), _FIXED)
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)

    def test_valid_framing_retained(self):
        _check(_stream())
        table = _record(b"ABCDEFGH") + _record(b"X")
        _check(_stream(table), len(table))

    def test_each_seek_failure_type_is_redacted(self):
        for phase, offset in (("header", 1024), ("tail", 1039), ("padding", 1033)):
            for error_type in (OSError, RuntimeError, ValueError, UnicodeError):
                with self.subTest(phase=phase, kind=error_type.__name__):
                    class Fault(BytesIO):
                        def seek(self, where, *args):
                            if where == offset:
                                raise error_type("C:/financial/private/invoices-2026.csv")
                            return super().seek(where, *args)
                    self.assert_rejected(Fault(_stream().getvalue()))

    def test_each_read_failure_type_is_redacted(self):
        for request in (8, 1, 7):
            for error_type in (OSError, RuntimeError, ValueError, UnicodeError):
                with self.subTest(size=request, kind=error_type.__name__):
                    class Fault(BytesIO):
                        def read(self, size=-1):
                            if size == request:
                                raise error_type("bank account: private contents")
                            return super().read(size)
                    self.assert_rejected(Fault(_stream().getvalue()))

    def test_non_native_header_read_results_are_rejected_without_hooks(self):
        class Hostile(bytes):
            def __len__(self):
                raise RuntimeError("secret from a bytes subclass")
        for injected in (bytearray(8), memoryview(b"A" * 8), Hostile(b"A" * 8)):
            with self.subTest(kind=type(injected).__name__):
                class Fault(BytesIO):
                    def read(self, size=-1):
                        return injected if size == 8 else super().read(size)
                self.assert_rejected(Fault(_stream().getvalue()))

    def test_non_native_tail_read_results_are_rejected_without_hooks(self):
        class Hostile(bytes):
            def __len__(self):
                raise RuntimeError("secret from a bytes subclass")
        for injected in (bytearray(b"Z"), memoryview(b"Z"), Hostile(b"Z")):
            with self.subTest(kind=type(injected).__name__):
                class Fault(BytesIO):
                    def read(self, size=-1):
                        return injected if size == 1 else super().read(size)
                self.assert_rejected(Fault(_stream().getvalue()))

    def test_non_native_padding_read_results_are_rejected_without_hooks(self):
        class Hostile(bytes):
            def __eq__(self, other):
                raise RuntimeError("secret from a bytes subclass")
        for injected in (bytearray(7), memoryview(bytes(7)), Hostile(bytes(7))):
            with self.subTest(kind=type(injected).__name__):
                class Fault(BytesIO):
                    def read(self, size=-1):
                        return injected if size == 7 else super().read(size)
                self.assert_rejected(Fault(_stream().getvalue()))

    def test_plain_short_reads_rejected_at_all_three_phases(self):
        for size in (8, 1, 7):
            with self.subTest(size=size):
                class Short(BytesIO):
                    def read(self, count=-1):
                        if count == size:
                            return super().read(count-1)
                        return super().read(count)
                self.assert_rejected(Short(_stream().getvalue()))

    def test_zero_pad_and_eight_byte_alignment_remain_accepted(self):
        for n in range(8):
            with self.subTest(pad=n):
                payload = b"X" * (8 - n)
                record = _record(payload)
                _check(_stream(record), len(record))

    def test_nonzero_padding_still_rejected(self):
        corrupted = _record()[:-1] + b"Z"
        self.assert_rejected(_stream(corrupted))

    def test_system_exit_is_not_swallowed(self):
        class Stop(BytesIO):
            def read(self, size=-1):
                if size == 8:
                    raise SystemExit(17)
                return super().read(size)
        with self.assertRaises(SystemExit) as stopped:
            _check(Stop(_stream().getvalue()))
        self.assertEqual(stopped.exception.code, 17)

    def test_keyboard_interrupt_is_not_swallowed(self):
        class Stop(BytesIO):
            def seek(self, offset, *args):
                if offset == 1024:
                    raise KeyboardInterrupt()
                return super().seek(offset, *args)
        with self.assertRaises(KeyboardInterrupt):
            _check(Stop(_stream().getvalue()))


if __name__ == "__main__":
    unittest.main()
