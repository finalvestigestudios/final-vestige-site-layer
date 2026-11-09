"""R297: CSV header/row parser errors must have no hidden private exception.

Uses real in-memory CSV parser failures and deterministic injected exceptions;
no customer financial files, network calls or platform-specific operations.
"""
from __future__ import annotations

import csv
import io
import traceback
import unittest

from fvs_suite.csv_parser_privacy import safe_csv_header, safe_csv_rows

SENSITIVE = "PRIVATE_ACCOUNT_NUMBER_83071942"


class CorruptReader:
    def __init__(self, error, line=7):
        self.error = error
        self.line_num = line
        self.calls = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.calls += 1
        raise self.error


class CsvParserPrivacyR297(unittest.TestCase):
    def assert_clean(self, run, message):
        try:
            run()
        except ValueError as error:
            self.assertEqual(str(error), message)
            self.assertIsNone(error.__context__)
            self.assertIsNone(error.__cause__)
            trace = "".join(traceback.format_exception(error))
            self.assertNotIn(SENSITIVE, trace)
        else:
            self.fail("Parser error unexpectedly accepted")

    def test_read_bom_header_and_multiline_records_exactly(self):
        payload = '\ufeffid,amount\r\n"A\nB",1.20\r\nC,-0.02\r\n'
        text = io.StringIO(payload, newline='')
        reader = csv.reader(text, strict=True)
        self.assertEqual(safe_csv_header(reader), ['\ufeffid', 'amount'])
        self.assertEqual(reader.line_num, 1)
        stream = safe_csv_rows(reader)
        self.assertEqual(next(stream), ['A\nB', '1.20'])
        self.assertEqual(reader.line_num, 3)
        self.assertEqual(next(stream), ['C', '-0.02'])
        self.assertEqual(reader.line_num, 4)
        self.assertEqual(list(stream), [])

    def test_header_empty_source_is_none(self):
        reader = csv.reader(io.StringIO(''), strict=True)
        self.assertIsNone(safe_csv_header(reader))
        self.assertEqual(list(safe_csv_rows(reader)), [])

    def test_header_real_invalid_utf8_private_bytes_not_chained(self):
        data = io.TextIOWrapper(io.BytesIO(b'account,amount\xff\n'), encoding='utf-8')
        self.assert_clean(lambda: safe_csv_header(csv.reader(data, strict=True)),
                          'CSV input: invalid CSV header')

    def test_record_real_invalid_utf8_private_bytes_not_chained(self):
        data = io.BytesIO(b'id,amount\nA,1.20\nB,\xff\n')
        reader = csv.reader((line.decode('utf-8') for line in data), strict=True)
        self.assertEqual(safe_csv_header(reader), ['id','amount'])
        self.assert_clean(lambda: list(safe_csv_rows(reader)),
                          'CSV input: invalid CSV near physical line 2')

    def test_header_csv_error_message_never_retained(self):
        reader = CorruptReader(csv.Error(SENSITIVE))
        self.assert_clean(lambda: safe_csv_header(reader), 'CSV input: invalid CSV header')
        self.assertEqual(reader.calls, 1)

    def test_record_csv_error_message_never_retained(self):
        reader = CorruptReader(csv.Error(SENSITIVE), 13)
        self.assert_clean(lambda: list(safe_csv_rows(reader)),
                          'CSV input: invalid CSV near physical line 13')
        self.assertEqual(reader.calls, 1)

    def test_header_unicode_error_message_never_retained(self):
        reader = CorruptReader(UnicodeError(SENSITIVE))
        self.assert_clean(lambda: safe_csv_header(reader), 'CSV input: invalid CSV header')

    def test_record_unicode_error_message_never_retained(self):
        reader = CorruptReader(UnicodeError(SENSITIVE))
        self.assert_clean(lambda: list(safe_csv_rows(reader)),
                          'CSV input: invalid CSV near physical line 7')

    def test_record_invalid_line_never_stringifies_untrusted_object(self):
        class DangerousLine:
            def __str__(self):
                raise AssertionError('unexpected private line conversion')
        reader = CorruptReader(csv.Error(SENSITIVE), DangerousLine())
        self.assert_clean(lambda: list(safe_csv_rows(reader)),
                          'CSV input: invalid CSV near physical line unknown')

    def test_record_line_subclass_ignored(self):
        reader = CorruptReader(csv.Error(SENSITIVE), type('HiddenInt', (int,), {})(4))
        self.assert_clean(lambda: list(safe_csv_rows(reader)),
                          'CSV input: invalid CSV near physical line unknown')

    def test_header_propagates_keyboard_interrupt(self):
        with self.assertRaises(KeyboardInterrupt):
            safe_csv_header(CorruptReader(KeyboardInterrupt()))

    def test_rows_propagate_system_exit(self):
        with self.assertRaises(SystemExit) as cm:
            list(safe_csv_rows(CorruptReader(SystemExit(3))))
        self.assertEqual(cm.exception.code, 3)

    def test_rows_propagate_memory_error(self):
        with self.assertRaises(MemoryError):
            list(safe_csv_rows(CorruptReader(MemoryError())))

    def test_header_does_not_silence_non_parser_failure(self):
        with self.assertRaisesRegex(RuntimeError, SENSITIVE):
            safe_csv_header(CorruptReader(RuntimeError(SENSITIVE)))

    def test_rows_does_not_silence_non_parser_failure(self):
        with self.assertRaisesRegex(RuntimeError, SENSITIVE):
            list(safe_csv_rows(CorruptReader(RuntimeError(SENSITIVE))))

    def test_actual_strict_malformed_csv_record_is_private(self):
        reader = csv.reader(io.StringIO('id,amount\n"open,12\n'), strict=True)
        self.assertEqual(safe_csv_header(reader), ['id','amount'])
        self.assert_clean(lambda: list(safe_csv_rows(reader)),
                          'CSV input: invalid CSV near physical line 2')

    def test_actual_strict_malformed_csv_header_is_private(self):
        reader = csv.reader(io.StringIO('"open,12\n'), strict=True)
        self.assert_clean(lambda: safe_csv_header(reader),
                          'CSV input: invalid CSV header')

    def test_rows_are_lazy(self):
        reader = CorruptReader(csv.Error(SENSITIVE))
        rows = safe_csv_rows(reader)
        self.assertEqual(reader.calls, 0)
        self.assert_clean(lambda: next(rows),
                          'CSV input: invalid CSV near physical line 7')


if __name__ == '__main__':
    unittest.main()
