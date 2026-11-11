"""R361 actual SpendMap input and CSV-output path tests; full checkout needed."""
from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fvs_suite.engine import dollars, key, money, parse_date, spend_map
from fvs_suite import spend_source_budget_r361 as limits
from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.spend_input import validated_spend_rows


def row(n: int, vendor='ACME', category='Supplies'):
    return {'row': str(n), 'vendor': vendor, 'date': '2026-11-01',
            'amount': '100.00', 'category': category}


def parse_rows(source, normalizer=key):
    return list(validated_spend_rows(source, normalize_vendor=normalizer,
                                    parse_date=parse_date, parse_money=money))


class SpendSourceBudgetEngineR361(unittest.TestCase):
    def test_oversized_vendor_rejected_before_callback(self):
        seen = []
        source = [row(2, vendor='V' * (1_048_576 + 1))]
        with self.assertRaisesRegex(ValueError, 'cell size limit'):
            parse_rows(source, lambda text: seen.append(text) or 'ACME')
        self.assertEqual(seen, [])

    def test_oversized_category_rejected_before_callback(self):
        with self.assertRaisesRegex(ValueError, 'cell size limit'):
            parse_rows([row(2, category='C' * (1_048_576 + 1))])

    def test_oversized_unused_column_rejected(self):
        source = row(2)
        source['unused'] = 'X' * (1_048_576 + 1)
        with self.assertRaisesRegex(ValueError, 'cell size limit'):
            parse_rows([source])

    def test_wide_direct_row_rejected_before_callback(self):
        source = row(2)
        source.update({f'EXTRA{n}': '' for n in range(60)})
        calls = []
        with self.assertRaisesRegex(ValueError, 'column limit'):
            parse_rows([source], lambda value: calls.append(value) or key(value))
        self.assertEqual(calls, [])

    def test_utf8_total_cap_rejected_before_callbacks(self):
        calls = []
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 80):
            with self.assertRaisesRegex(ValueError, 'text byte limit'):
                parse_rows([row(2, vendor='€' * 20)],
                           lambda value: calls.append(value) or key(value))
        self.assertEqual(calls, [])

    def test_late_budget_violation_rejects_before_first_callback(self):
        calls = []
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 140):
            with self.assertRaisesRegex(ValueError, 'text byte limit'):
                parse_rows([row(2), row(3), row(4)],
                           lambda value: calls.append(value) or key(value))
        self.assertEqual(calls, [])

    def test_surrogate_is_rejected_without_echo(self):
        with self.assertRaises(ValueError) as caught:
            parse_rows([row(2, category='SECRET\ud800')])
        self.assertNotIn('SECRET', str(caught.exception))

    def test_source_records_unchanged_when_rejected(self):
        source = [row(2), row(3, category='X' * (1_048_576 + 1))]
        before = [dict(item) for item in source]
        with self.assertRaises(ValueError):
            parse_rows(source)
        self.assertEqual(source, before)

    def test_normal_summary_still_exact_and_attested(self):
        source = [row(2), row(3)]
        report = summarize_spend(source, normalize_vendor=key, parse_date=parse_date,
                                 parse_money=money, format_money=dollars,
                                 source_sha256='f' * 64)
        self.assertEqual(report[0]['amount'], '200.00')
        self.assertEqual(report[0]['source_rows'], '2;3')

    def test_standard_csv_workflow_unchanged(self):
        with TemporaryDirectory() as dirname:
            root = Path(dirname)
            source = root / 'spend.csv'
            with source.open('w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['vendor', 'date', 'amount', 'category'])
                writer.writerow(['ACME', '2026-11-01', '100.00', 'Supplies'])
                writer.writerow(['ACME', '2026-11-01', '-25.00', 'Supplies'])
            before = source.read_bytes()
            out = root / 'out'
            out.mkdir()
            paths = spend_map(source, out)
            with Path(paths[0]).open('r', encoding='utf-8-sig', newline='') as f:
                result = list(csv.DictReader(f))
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['amount'], '75.00')
            self.assertEqual(source.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
