"""R72: no private source names or values in reusable CSV diagnostics."""
from __future__ import annotations

import unittest

from fvs_suite.csv_diagnostics import csv_input_error

PRIVATE = "CLIENT_462_PRIVATE_PAYROLL_DO_NOT_LOG"


class CsvErrorPrivacyR72(unittest.TestCase):
    def test_fixed_header_and_selection_diagnostics(self):
        cases = {
            "select_file": "Select an existing CSV input",
            "bad_header": "CSV input: invalid CSV header",
            "missing_headers": "CSV input: Missing headers",
            "nul_header": "CSV input: CSV header contains a NUL character",
            "duplicate_header": "CSV input: blank or duplicate normalized CSV header",
        }
        for code, text in cases.items():
            with self.subTest(code=code):
                self.assertEqual(str(csv_input_error(code)), text)

    def test_safe_line_number_provenance(self):
        for code in ("bad_record", "nul_record", "blank_ledger_id"):
            with self.subTest(code=code):
                self.assertIn("physical", str(csv_input_error(code, line=432)))
                self.assertTrue(str(csv_input_error(code, line=432)).endswith("432"))

    def test_bad_row_shape_keeps_safe_column_counts(self):
        self.assertEqual(
            str(csv_input_error("bad_row_shape", line=51, expected=3, actual=2)),
            "CSV input: malformed CSV record at physical line 51 "
            "(expected 3 columns, got 2)",
        )

    def test_schema_field_is_only_from_explicit_allowlist(self):
        for field in ("id", "amount", "claim_type", "related_document", "unit_price"):
            with self.subTest(field=field):
                self.assertIn("'" + field + "'", str(csv_input_error("column_missing", field=field)))
                self.assertIn("'" + field + "'", str(csv_input_error("alias_ambiguous", field=field)))

    def test_untrusted_fields_and_aliases_never_echo(self):
        for field in (PRIVATE, PRIVATE + "\nX", 101, None, b"a", object(), "secret_field"):
            with self.subTest(kind=type(field).__name__):
                for code in ("column_missing", "alias_ambiguous"):
                    message = str(csv_input_error(code, field=field))
                    self.assertNotIn(PRIVATE, message)
                    self.assertIn("'required'", message)

    def test_reject_bogus_error_codes_without_stringifying(self):
        for code in (PRIVATE, "", "../../client.csv", None, object()):
            with self.subTest(code=type(code).__name__):
                self.assertEqual(str(csv_input_error(code)), "CSV input: invalid CSV")

    def test_malformed_physical_rows_cannot_leak_data(self):
        for invalid in (PRIVATE, -1, 0, True, 1.5, 1_000_000_001, None, object()):
            with self.subTest(kind=type(invalid).__name__):
                for code in ("bad_record", "nul_record", "blank_ledger_id"):
                    msg = str(csv_input_error(code, line=invalid))
                    self.assertTrue(msg.endswith("unknown"))
                    self.assertNotIn(PRIVATE, msg)

    def test_malformed_counts_cannot_leak_data(self):
        for invalid in (PRIVATE, -1, True, 2.0, None, object(), 10_001):
            with self.subTest(kind=type(invalid).__name__):
                result = str(csv_input_error("bad_row_shape", line=2, expected=invalid, actual=invalid))
                self.assertIn("expected unknown columns, got unknown", result)
                self.assertNotIn(PRIVATE, result)

    def test_very_large_private_string_is_never_interpolated(self):
        payload = PRIVATE * 500_000
        for code in ("column_missing", "bad_record", "bad_row_shape"):
            with self.subTest(code=code):
                msg = str(csv_input_error(code, field=payload, line=payload,
                                           expected=payload, actual=payload))
                self.assertLess(len(msg), 128)
                self.assertNotIn(PRIVATE, msg)

    def test_repeatable_and_different_inputs_same_error(self):
        a = csv_input_error("column_missing", field=PRIVATE)
        b = csv_input_error("column_missing", field="OTHER_SECRET_VALUE")
        self.assertEqual(str(a), str(b))
        self.assertEqual(str(a), str(csv_input_error("column_missing", field=PRIVATE)))

    def test_all_codes_produce_plain_value_error(self):
        for code in ("select_file", "bad_header", "missing_headers", "nul_header",
                     "duplicate_header", "bad_record", "nul_record", "bad_row_shape",
                     "blank_ledger_id", "alias_ambiguous", "column_missing"):
            with self.subTest(code=code):
                error = csv_input_error(code, field="amount", line=2, expected=2, actual=1)
                self.assertIs(type(error), ValueError)
                self.assertNotIn(PRIVATE, str(error))


if __name__ == "__main__":
    unittest.main()
