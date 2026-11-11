"""R360 true SpendMap input and report integration tests (full checkout required)."""
from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fvs_suite.engine import dollars, key, money, parse_date, spend_map
from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.spend_input import validated_spend_rows


def rows(*vendors: str) -> list[dict[str, str]]:
    return [dict(row=str(i + 2), vendor=vendor, date='2026-11-01',
                 amount='100.00', category='Supplies')
            for i, vendor in enumerate(vendors)]


def parse_rows(source, normalizer=key):
    return list(validated_spend_rows(source, normalize_vendor=normalizer,
                                     parse_date=parse_date, parse_money=money))


def summary(source, normalizer=key):
    return summarize_spend(source, normalize_vendor=normalizer,
                           parse_date=parse_date, parse_money=money,
                           format_money=dollars, source_sha256='f' * 64)


class SpendVendorSessionEngineR360(unittest.TestCase):
    def test_native_same_vendor_aggregates(self):
        report = summary(rows('ACME', 'ACME'))
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]['amount'], '200.00')
        self.assertEqual(report[0]['source_rows'], '2;3')

    def test_changed_same_source_is_rejected(self):
        calls = iter(['ACME', 'OTHER'])
        with self.assertRaisesRegex(ValueError, 'Inconsistent vendor normalization'):
            parse_rows(rows('ACME', 'ACME'), lambda _: next(calls))

    def test_changed_source_separated_by_other_vendor_is_rejected(self):
        calls = iter(['ACME', 'BETA', 'OTHER'])
        with self.assertRaisesRegex(ValueError, 'physical row 4'):
            parse_rows(rows('ACME', 'BETA', 'ACME'), lambda _: next(calls))

    def test_ascii_case_source_equivalence_is_rejected(self):
        calls = iter(['ACME', 'OTHER'])
        with self.assertRaisesRegex(ValueError, 'Inconsistent vendor normalization'):
            parse_rows(rows('Acme', 'ACME'), lambda _: next(calls))

    def test_ascii_boundary_space_source_equivalence_is_rejected(self):
        calls = iter(['ACME', 'OTHER'])
        with self.assertRaises(ValueError):
            parse_rows(rows(' ACME ', '\tacme\r'), lambda _: next(calls))

    def test_unicode_nbsp_is_distinct_source_evidence(self):
        result = parse_rows(rows('ACME', '\u00a0ACME'),
                            lambda raw: 'ACME' if raw == 'ACME' else 'OTHER')
        self.assertEqual([item[1] for item in result], ['ACME', 'OTHER'])

    def test_distinct_source_variants_still_get_collision_flag(self):
        report = summary(rows('ACME INC', 'ACME, INC'))
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]['vendor_label_variants'], '2')
        self.assertIn('normalized_vendor_collision_review', report[0]['flag'])

    def test_no_partial_iterator_rows_after_last_callback_changes_vendor(self):
        calls = iter(['ACME', 'ACME', 'OTHER'])
        iterator = validated_spend_rows(rows('ACME', 'ACME', 'ACME'),
                                        normalize_vendor=lambda _: next(calls),
                                        parse_date=parse_date, parse_money=money)
        with self.assertRaises(ValueError):
            next(iterator)

    def test_summarizer_rejects_inconsistent_vendor_before_reporting(self):
        calls = iter(['ACME', 'OTHER'])
        with self.assertRaises(ValueError):
            summary(rows('ACME', 'ACME'), lambda _: next(calls))

    def test_report_is_deterministic_for_native_normalizer(self):
        source = rows('ACME', 'Acme', 'BETA')
        self.assertEqual(summary(source), summary(source))

    def test_original_rows_are_not_mutated_on_failure(self):
        source = rows('ACME', 'ACME')
        before = [dict(item) for item in source]
        calls = iter(['ACME', 'OTHER'])
        with self.assertRaises(ValueError):
            parse_rows(source, lambda _: next(calls))
        self.assertEqual(source, before)

    def test_secret_vendor_is_not_in_error(self):
        private = 'PRIVATE-ACCOUNT-998877'
        calls = iter(['A', 'B'])
        with self.assertRaises(ValueError) as error:
            parse_rows(rows(private, private), lambda _: next(calls))
        self.assertNotIn(private, str(error.exception))

    def test_standard_csv_engine_workflow_preserves_totals(self):
        with TemporaryDirectory() as dirname:
            root = Path(dirname)
            path = root / 'spend.csv'
            with path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(['vendor', 'date', 'amount', 'category'])
                writer.writerow(['ACME', '2026-11-01', '100.00', 'Supplies'])
                writer.writerow(['Acme', '2026-11-02', '100.00', 'Supplies'])
            before = path.read_bytes()
            output_dir = root / 'out'
            output_dir.mkdir()
            paths = spend_map(path, output_dir)
            with Path(paths[0]).open('r', encoding='utf-8-sig', newline='') as stream:
                report = list(csv.DictReader(stream))
            self.assertEqual(len(report), 1)
            self.assertEqual(report[0]['amount'], '200.00')
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
