"""R359 genuine source-row, engine, and CSV date custody; synthetic fixtures.

Requires the full private desktop repository, not the isolated helper harness.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fvs_suite.engine import dollars, key, money, parse_date, spend_map
from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.spend_input import validated_spend_rows


def source_rows(*dates: str) -> list[dict[str, str]]:
    return [dict(row=str(i + 2), vendor='ACME', date=value,
                 amount='100.00', category='Supplies')
            for i, value in enumerate(dates)]


def parse_rows(rows, parser=parse_date):
    return list(validated_spend_rows(rows, normalize_vendor=key,
                                     parse_date=parser, parse_money=money))


class SpendDateEngineIntegrationR359(unittest.TestCase):
    def test_normal_native_date_is_unchanged(self):
        result = parse_rows(source_rows('2026-11-01'))
        self.assertEqual(result[0][2], '2026-11')
        self.assertEqual(result[0][4], money('100.00'))

    def test_reformatted_same_calendar_day_is_allowed(self):
        result = parse_rows(source_rows('11/01/26'), lambda raw: date(2026, 11, 1))
        self.assertEqual(result[0][2], '2026-11')

    def test_callback_cannot_shift_month(self):
        with self.assertRaisesRegex(ValueError, 'parser changed original date'):
            parse_rows(source_rows('2026-11-01'), lambda _: date(2026, 12, 1))

    def test_callback_cannot_shift_day_in_same_month(self):
        with self.assertRaisesRegex(ValueError, 'parser changed original date'):
            parse_rows(source_rows('2026-11-01'), lambda _: date(2026, 11, 2))

    def test_ambiguous_us_source_cannot_be_reinterpreted(self):
        with self.assertRaisesRegex(ValueError, 'parser changed original date'):
            parse_rows(source_rows('11/12/2026'), lambda _: date(2026, 12, 11))

    def test_invalid_future_date_rejected_before_any_callback(self):
        calls = []
        def callback(raw):
            calls.append(raw)
            return date(2026, 11, 1)
        with self.assertRaisesRegex(ValueError, 'Invalid original spend date'):
            parse_rows(source_rows('2026-11-01', '2026-02-30'), callback)
        self.assertEqual(calls, [])

    def test_parser_cannot_launder_unsupported_format(self):
        with self.assertRaisesRegex(ValueError, 'Invalid original spend date'):
            parse_rows(source_rows('2026.11.01'), lambda _: date(2026, 11, 1))

    def test_input_subclass_cannot_call_custom_strip(self):
        class Hostile(str):
            def strip(self, *args):
                raise AssertionError('source method executed')
        with self.assertRaisesRegex(ValueError, 'plain text'):
            parse_rows(source_rows(Hostile('2026-11-01')))

    def test_date_subclass_callback_rejected(self):
        class HostileDate(date):
            def __eq__(self, other):
                raise AssertionError('date method executed')
        with self.assertRaisesRegex(ValueError, 'calendar date'):
            parse_rows(source_rows('2026-11-01'), lambda _: HostileDate(2026, 11, 1))

    def test_full_summarizer_rejects_period_rewrite(self):
        with self.assertRaisesRegex(ValueError, 'parser changed original date'):
            summarize_spend(source_rows('2026-11-01'), normalize_vendor=key,
                            parse_date=lambda _: date(2026, 12, 1),
                            parse_money=money, format_money=dollars,
                            source_sha256='f' * 64)

    def test_full_summarizer_preserves_true_period_and_total(self):
        report = summarize_spend(source_rows('11/01/26'), normalize_vendor=key,
                                 parse_date=parse_date, parse_money=money,
                                 format_money=dollars, source_sha256='f' * 64)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]['month'], '2026-11')
        self.assertEqual(report[0]['amount'], '100.00')
        self.assertEqual(report[0]['source_rows'], '2')

    def test_csv_spendmap_preserves_original_source(self):
        with TemporaryDirectory() as dirname:
            root = Path(dirname)
            path = root / 'spend.csv'
            with path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(['vendor', 'date', 'amount', 'category'])
                writer.writerow(['ACME', '11/01/26', '100.00', 'Supplies'])
            source_bytes = path.read_bytes()
            out = root / 'out'
            out.mkdir()
            files = spend_map(path, out)
            with Path(files[0]).open('r', encoding='utf-8-sig', newline='') as stream:
                report = list(csv.DictReader(stream))
            self.assertEqual(report[0]['month'], '2026-11')
            self.assertEqual(report[0]['amount'], '100.00')
            self.assertEqual(path.read_bytes(), source_bytes)


if __name__ == '__main__':
    unittest.main()
