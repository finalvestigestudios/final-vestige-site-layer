import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('data_import_doctor.py')


class CLIIntegrationTests(unittest.TestCase):
    def run_app(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, timeout=15)

    def test_clean_csv_returns_zero(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'good.csv'
            csv.write_text('id,amount\na,12.00\n', encoding='utf-8')
            result = self.run_app(csv)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'PASS')

    def test_malformed_csv_returns_two(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'broken.csv'
            csv.write_text('id,value\na,"bad\n', encoding='utf-8')
            result = self.run_app(csv)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'INCOMPLETE')

    def test_issue_csv_returns_one(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'bad.csv'
            cfg = Path(d) / 'rules.json'
            csv.write_text('id,amount\na,invalid\n', encoding='utf-8')
            cfg.write_text('{"types":{"amount":"decimal"}}', encoding='utf-8')
            result = self.run_app(csv, '--schema', cfg)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('invalid_type', json.loads(result.stdout)['issue_counts'])

    def test_existing_report_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'good.csv'
            csv.write_text('id\na\n', encoding='utf-8')
            report = Path(d) / 'report.json'
            report.write_text('keep', encoding='utf-8')
            result = self.run_app(csv, '--report', report)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(report.read_text(), 'keep')

    def test_fresh_report_contains_source_digest(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'good.csv'
            csv.write_text('id\na\n', encoding='utf-8')
            report = Path(d) / 'report.json'
            result = self.run_app(csv, '--report', report)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(report.read_text())
            self.assertEqual(data['status'], 'PASS')
            self.assertEqual(len(data['source_sha256']), 64)


if __name__ == '__main__':
    unittest.main()
