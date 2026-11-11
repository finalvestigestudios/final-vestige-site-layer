"""R362 full SpendMap engine checks (requires full repository checkout)."""
from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fvs_suite import spend_source_budget_r361 as limits
from fvs_suite.engine import dollars, key, money, parse_date, spend_map
from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.spend_input import validated_spend_rows


def row(number, **extra):
    result = {'row': str(number), 'vendor': 'ACME', 'date': '2026-11-01',
              'amount': '100.00', 'category': 'Supplies'}
    result.update(extra)
    return result


def parsed(records, normalize_vendor=key):
    return list(validated_spend_rows(records, normalize_vendor=normalize_vendor,
                                    parse_date=parse_date, parse_money=money))


class SpendFieldCardinalityEngineR362(unittest.TestCase):
    def test_late_tiny_field_overflow_prevents_all_callbacks(self):
        called = []
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 9):
            with self.assertRaisesRegex(ValueError, 'field-count limit'):
                parsed([row(2), row(3)], lambda vendor: called.append(vendor) or key(vendor))
        self.assertEqual(called, [])

    def test_exact_ten_fields_across_two_rows_preserves_evidence(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 10):
            result = parsed([row(2), row(3)])
        self.assertEqual([record['row'] for record, *_ in result], ['2', '3'])
        self.assertEqual([str(parsed_amount) for *_, parsed_amount in result], ['100.00', '100.00'])

    def test_empty_extra_column_still_charged(self):
        called = []
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 5):
            with self.assertRaisesRegex(ValueError, 'field-count limit'):
                parsed([row(2, empty_extra='')], lambda vendor: called.append(vendor) or key(vendor))
        self.assertEqual(called, [])

    def test_failure_does_not_modify_caller_owned_rows(self):
        originals = [row(2), row(3, unused='')]
        before = [dict(item) for item in originals]
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 10):
            with self.assertRaisesRegex(ValueError, 'field-count limit'):
                parsed(originals)
        self.assertEqual(originals, before)

    def test_summary_money_and_source_rows_unmodified(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 10):
            report = summarize_spend([row(2), row(3)], normalize_vendor=key,
                                     parse_date=parse_date, parse_money=money,
                                     format_money=dollars, source_sha256='b' * 64)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]['amount'], '200.00')
        self.assertEqual(report[0]['source_rows'], '2;3')

    def test_standard_csv_ingestion_still_works(self):
        with TemporaryDirectory() as temp:
            source = Path(temp) / 'spend.csv'
            source.write_text('vendor,date,amount,category\nACME,2026-11-01,100.00,Supplies\n',
                              encoding='utf-8')
            initial = source.read_bytes()
            destination = Path(temp) / 'output'
            destination.mkdir()
            reports = spend_map(source, destination)
            with Path(reports[0]).open(encoding='utf-8-sig', newline='') as stream:
                imported = list(csv.DictReader(stream))
            self.assertEqual(imported[0]['amount'], '100.00')
            self.assertEqual(source.read_bytes(), initial)


if __name__ == '__main__':
    unittest.main()
