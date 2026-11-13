"""R396 premium report/journal exception-chain confidentiality regressions.

Run against the real fvs_suite implementation on Ubuntu and native Windows.
All input is synthetic and remains on local temporary storage.  This suite
cannot assert that a caller inspecting traceback frames/locals sees no data;
it verifies that low-level decode, CSV, JSON and OS exceptions are NOT retained
as __cause__ / __context__ on translated customer-facing ValueErrors.
"""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite import exception_review as review


class PremiumSourceErrorPrivacyR396(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r396-private-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.report = self.root / "synthetic.csv"
        self.journal = self.root / "review.jsonl"

    def _write_valid_report(self, product):
        if product == "grants":
            self.report.write_bytes(b"id,status\nCLAIM-1,variance\n")
        else:
            self.report.write_bytes(b"po,line,status\nPO-1,1,unit_price_variance\n")
        batch = review.read_cases(self.report, product)
        self.assertEqual(len(batch.cases), 1)
        return batch

    def assert_private_failure(self, callback, expected):
        with self.assertRaises(ValueError) as caught:
            callback()
        error = caught.exception
        self.assertEqual(str(error), expected)
        self.assertIsNone(error.__cause__, "Private error retained in __cause__")
        self.assertIsNone(error.__context__, "Private error retained in __context__")

    def test_missing_source_path_has_no_nested_os_error(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                missing = self.root / "PRIVATE_ACCOUNT_NUMBER.csv"
                self.assert_private_failure(
                    lambda: review.read_cases(missing, product),
                    "Exception report must be an existing regular file, not a symlink",
                )

    def test_read_helper_translates_only_missing_file(self):
        with patch.object(review, "read_regular_bytes",
                          side_effect=FileNotFoundError("PRIVATE_LOCAL_ACCOUNT")):
            self.assert_private_failure(
                lambda: review._read_file(self.report, 100, "Review journal"),
                "Review journal must be an existing regular file, not a symlink",
            )

    def test_read_helper_does_not_convert_unrelated_failure(self):
        with patch.object(review, "read_regular_bytes",
                          side_effect=PermissionError("synthetic-denied")):
            with self.assertRaises(PermissionError):
                review._read_file(self.report, 100, "Exception report")

    def test_decode_error_does_not_retain_financial_input_buffer(self):
        raw = b"id,status\nPRIVATE-ACCOUNT-987,variance\n\xff\n"
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                self.report.write_bytes(raw)
                self.assert_private_failure(
                    lambda: review.read_cases(self.report, product),
                    "Exception report must be UTF-8 CSV",
                )

    def test_decode_error_does_not_modify_input(self):
        original = b"po,line,status\nPRIVATE-SUPPLIER-987,1,variance\n\xfe"
        self.report.write_bytes(original)
        self.assert_private_failure(
            lambda: review.read_cases(self.report, "procurement"),
            "Exception report must be UTF-8 CSV",
        )
        self.assertEqual(self.report.read_bytes(), original)

    def test_malformed_csv_header_has_no_nested_csv_exception(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                self.report.write_bytes(b'"PRIVATE-CLAIM,id,status\n')
                self.assert_private_failure(
                    lambda: review.read_cases(self.report, product),
                    "Exception report contains a malformed CSV header",
                )

    def test_malformed_body_preserves_safe_physical_line_number(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                header = b"id,status\n" if product == "grants" else b"po,line,status\n"
                self.report.write_bytes(header + b'"PRIVATE-RECORD,variance\n')
                self.assert_private_failure(
                    lambda: review.read_cases(self.report, product),
                    "Malformed CSV quoting near physical line 2",
                )

    def test_malformed_body_never_rewrites_source(self):
        original = b"id,status\n\"PRIVATE-ACCOUNT,variance\n"
        self.report.write_bytes(original)
        self.assert_private_failure(
            lambda: review.read_cases(self.report, "grants"),
            "Malformed CSV quoting near physical line 2",
        )
        self.assertEqual(self.report.read_bytes(), original)

    def test_invalid_journal_json_does_not_retain_raw_record(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._write_valid_report(product)
                raw = b'{"private":"PRIVATE-SUPPLIER-987",}\n'
                self.journal.write_bytes(raw)
                self.assert_private_failure(
                    lambda: review.read_journal(self.journal, batch),
                    "Malformed review journal record 1",
                )
                self.assertEqual(self.journal.read_bytes(), raw)
                self.journal.unlink()

    def test_invalid_journal_utf8_does_not_retain_raw_record(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._write_valid_report(product)
                raw = b'{"private":"PRIVATE-BANK-ACCOUNT-987-\xff"}\n'
                self.journal.write_bytes(raw)
                self.assert_private_failure(
                    lambda: review.read_journal(self.journal, batch),
                    "Malformed review journal record 1",
                )
                self.assertEqual(self.journal.read_bytes(), raw)
                self.journal.unlink()

    def test_json_error_line_number_remains_useful_but_path_free(self):
        batch = self._write_valid_report("grants")
        # First line is syntactically valid but not a valid event: read_journal
        # must reject it rather than silently skipping a hash-chain record.
        self.journal.write_bytes(b'{"private":"PRIVATE","malformed":}\n')
        self.assert_private_failure(
            lambda: review.read_journal(self.journal, batch),
            "Malformed review journal record 1",
        )

    def test_duplicate_keys_are_not_silently_accepted(self):
        batch = self._write_valid_report("procurement")
        self.journal.write_bytes(b'{"schema":1,"schema":2}\n')
        with self.assertRaisesRegex(ValueError, "Repeated JSON journal key"):
            review.read_journal(self.journal, batch)

    def test_valid_premium_reports_still_read(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._write_valid_report(product)
                self.assertEqual(batch.product, product)
                self.assertEqual(len(batch.cases), 1)
                self.assertEqual(review.read_journal(self.journal, batch), [])

    def test_valid_empty_journal_still_reads(self):
        batch = self._write_valid_report("grants")
        self.journal.write_bytes(b"")
        self.assertEqual(review.read_journal(self.journal, batch), [])

    def test_csv_quoted_newline_source_rows_are_still_physical(self):
        self.report.write_bytes(b'id,status\n"CLAIM\nONE",variance\n')
        batch = review.read_cases(self.report, "grants")
        self.assertEqual(batch.cases[0].report_row, 2)


if __name__ == "__main__":
    unittest.main()
