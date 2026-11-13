"""R358 genuine SpendMap CSV, report and reviewed vendor-identity integration.

Requires full private desktop checkout; synthetic source bytes only.
"""
from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fvs_suite.engine import spend_map, table
from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.engine import key, money, dollars, parse_date


def fixture(root: Path, *vendors: str) -> Path:
    path = root / 'spend-source.csv'
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['vendor', 'date', 'amount', 'category'])
        for vendor in vendors:
            writer.writerow([vendor, '2026-11-01', '100.00', 'Supplies'])
    return path


def rows_from_spend(root: Path, *vendors: str):
    source = fixture(root, *vendors)
    report_dir = root / 'report'
    report_dir.mkdir()
    paths = spend_map(source, report_dir)
    with Path(paths[0]).open('r', encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


class SpendVendorIntegrationR358(unittest.TestCase):
    def test_actual_csv_import_preserves_nbsp_for_spendmap(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            source = fixture(root, '\u00a0ACME')
            rows = table(source, ('vendor', 'amount', 'date'), ('category',),
                         preserve_spend_vendor_source=True)
            self.assertEqual(rows[0]['vendor'], '\u00a0ACME')

    def test_default_csv_import_retains_exact_vendor_source(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            source = fixture(root, '\u00a0ACME')
            rows = table(source, ('vendor', 'amount', 'date'), ('category',))
            self.assertEqual(rows[0]['vendor'], '\u00a0ACME')

    def test_spendmap_flags_normalized_only_nbsp_collision(self):
        with TemporaryDirectory() as folder:
            row = rows_from_spend(Path(folder), 'ACME', '\u00a0ACME')[0]
            self.assertEqual(row['amount'], '200.00')
            self.assertIn('normalized_vendor_collision_review', row['flag'])
            self.assertEqual(row['vendor_label_variants'], '2')
            self.assertIn(r'\u00A0ACME', row['source_vendor_labels'])
            self.assertEqual(row['source_rows'], '2;3')
            self.assertEqual(len(row['source_sha256']), 64)

    def test_figure_space_collision_and_provenance(self):
        with TemporaryDirectory() as folder:
            row = rows_from_spend(Path(folder), 'ACME', 'ACME\u2007')[0]
            self.assertIn('normalized_vendor_collision_review', row['flag'])
            self.assertIn(r'ACME\u2007', row['source_vendor_labels'])

    def test_narrow_nbsp_collision_and_provenance(self):
        with TemporaryDirectory() as folder:
            row = rows_from_spend(Path(folder), 'ACME', '\u202fACME')[0]
            self.assertIn('normalized_vendor_collision_review', row['flag'])
            self.assertIn(r'\u202FACME', row['source_vendor_labels'])

    def test_case_only_remains_no_review(self):
        with TemporaryDirectory() as folder:
            row = rows_from_spend(Path(folder), 'ACME', 'acme')[0]
            self.assertNotIn('normalized_vendor_collision_review', row['flag'])
            self.assertEqual(row['vendor_label_variants'], '1')

    def test_ascii_whitespace_is_visible_and_requires_review(self):
        with TemporaryDirectory() as folder:
            row = rows_from_spend(Path(folder), ' ACME ', 'ACME')[0]
            self.assertIn('normalized_vendor_collision_review', row['flag'])
            self.assertEqual(row['vendor_label_variants'], '2')
            self.assertEqual(row['source_vendor_labels'], r'\u0020ACME\u0020; ACME')

    def test_genuine_direct_summarizer_flags_unicode_source(self):
        rows = [dict(row='2', vendor='ACME', amount='100.00', date='2026-11-01'),
                dict(row='3', vendor='\u00a0ACME', amount='100.00', date='2026-11-01')]
        output = summarize_spend(rows, normalize_vendor=key, parse_date=parse_date,
                                 parse_money=money, format_money=dollars,
                                 source_sha256='f'*64)
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]['vendor_label_variants'], '2')
        self.assertIn('normalized_vendor_collision_review', output[0]['flag'])
        self.assertEqual(output[0]['gross_charges'], '200.00')

    def test_report_does_not_mutate_original_vendor_cells(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            source = fixture(root, 'ACME', '\u00a0ACME')
            original = source.read_bytes()
            report_dir = root / 'out'
            report_dir.mkdir()
            spend_map(source, report_dir)
            self.assertEqual(source.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
