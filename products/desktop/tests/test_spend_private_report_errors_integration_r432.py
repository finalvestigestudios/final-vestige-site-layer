"""R432 full-engine private SpendMap verifier exception-chain regressions.

Requires the genuine fvs_suite source parser, exporter and independent verifier.
Synthetic financial CSVs only; no customer inputs, network or release artifacts.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fvs_suite import engine
from fvs_suite.spend_evidence_verify import verify_membership


class SpendPrivateReportErrorsIntegrationR432(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory(prefix="fvs-r432-private-errors-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "synthetic.csv"
        self.source.write_text(
            "vendor,amount,date,category\n"
            "ACME,12.30,2026-01-10,Parts\n",
            encoding="utf-8", newline="")
        self.report = Path(engine.spend_map(self.source, self.root)[0])

    def assert_closed_without_private_chain(self):
        with self.assertRaises(ValueError) as failed:
            verify_membership(self.source, self.report)
        exc = failed.exception
        self.assertIsNone(exc.__cause__)
        self.assertIsNone(exc.__context__)
        self.assertEqual(str(exc), "Malformed local SpendMap evidence")

    def test_unmodified_canonical_export_is_verified(self):
        source_bytes = self.source.read_bytes()
        report_bytes = self.report.read_bytes()
        receipt = verify_membership(self.source, self.report)
        self.assertEqual(receipt.buckets_verified, 1)
        self.assertEqual(receipt.groups_verified, 1)
        self.assertEqual(source_bytes, self.source.read_bytes())
        self.assertEqual(report_bytes, self.report.read_bytes())

    def test_invalid_utf8_report_byte_retains_no_private_exception(self):
        # Before R432, UnicodeDecodeError.object retained every report byte.
        self.report.write_bytes(self.report.read_bytes() + b"PRIVATE_ACCOUNT\xff")
        self.assert_closed_without_private_chain()

    def test_unpaired_surrogate_utf8_report_retains_no_private_exception(self):
        self.report.write_bytes(self.report.read_bytes() + b"PRIVATE_ACCOUNT\xed\xa0\x80")
        self.assert_closed_without_private_chain()

    def test_unexpected_continuation_byte_retains_no_private_exception(self):
        self.report.write_bytes(self.report.read_bytes() + b"PRIVATE_ACCOUNT\x80")
        self.assert_closed_without_private_chain()

    def test_unterminated_quoted_row_retains_no_private_csv_exception(self):
        self.report.write_bytes(self.report.read_bytes() + b'"PRIVATE_ACCOUNT')
        self.assert_closed_without_private_chain()


if __name__ == "__main__":
    unittest.main()
