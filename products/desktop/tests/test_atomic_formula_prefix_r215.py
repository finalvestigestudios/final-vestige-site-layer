"""R215: detect spreadsheet formula prefixes without altering legitimate audit data."""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from fvs_suite import atomic_reports as reports
from fvs_suite.csv_formula_guard import has_unescaped_formula_prefix


class FormulaPrefixCustodyR215(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="fvs-r215-")
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "evidence.csv"

    def publish(self, rows=None, fields=("id", "amount"), cell=str):
        if rows is None:
            rows = [{"id": "A", "amount": Decimal("0.10")}]
        return reports.write_csv_report(self.path, fields, rows, cell)

    def assert_no_partial(self):
        self.assertFalse(self.path.exists())
        self.assertFalse(list(self.path.parent.glob("*.partial")))

    def test_guard_identifies_bare_formulas(self):
        for value in ("=2+2", "+SUM(1)", "@SUM(1)"):
            with self.subTest(value=value):
                self.assertTrue(has_unescaped_formula_prefix(value))

    def test_guard_identifies_whitespace_then_formula(self):
        for prefix in (" ", "\t", "\r", "\n", "\v", "\f", "\u00a0", "\u2003", "\u2028"):
            with self.subTest(prefix=repr(prefix)):
                self.assertTrue(has_unescaped_formula_prefix(prefix + "=1+1"))

    def test_guard_identifies_invisible_marks_then_formula(self):
        for prefix in ("\ufeff", "\u200b", "\u200c", "\u200d", "\u2060", "\u200e", "\u200f"):
            with self.subTest(prefix=repr(prefix)):
                self.assertTrue(has_unescaped_formula_prefix(prefix + "+1"))

    def test_guard_identifies_mixed_whitespace_and_format_chars(self):
        self.assertTrue(has_unescaped_formula_prefix("\t\u200b \ufeff\n@SUM(A1)"))

    def test_guard_allows_safe_numbers_and_negative_decimal_strings(self):
        for value in ("", "   ", "-123.45", "  -123.45", "0.10", "(123.45)"):
            with self.subTest(value=value):
                self.assertFalse(has_unescaped_formula_prefix(value))

    def test_guard_allows_intentional_apostrophe_escape(self):
        self.assertFalse(has_unescaped_formula_prefix("'\t=1+1"))
        self.assertFalse(has_unescaped_formula_prefix(" \u200b'=1+1"))

    def test_guard_allows_legitimate_multiline_and_whitespace(self):
        for value in (" first\n=next line", "a\n@SUM(1)", " hello", "\tlegitimate"):
            with self.subTest(value=value):
                self.assertFalse(has_unescaped_formula_prefix(value))

    def test_direct_callback_whitespace_formula_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text CSV report cell") as context:
            self.publish(rows=[{"id": "\t=1+1", "amount": "0.10"}])
        self.assertIsNone(context.exception.__context__)
        self.assert_no_partial()

    def test_nonbreaking_space_formula_fails_closed(self):
        with self.assertRaises(ValueError):
            self.publish(rows=[{"id": "\u00a0+SUM(1)", "amount": "1.00"}])
        self.assert_no_partial()

    def test_invisible_mark_formula_fails_closed(self):
        with self.assertRaises(ValueError):
            self.publish(rows=[{"id": "\u200b\ufeff@SUM(1)", "amount": "1.00"}])
        self.assert_no_partial()

    def test_formula_in_header_rejected_before_staging(self):
        with self.assertRaises(ValueError):
            self.publish(fields=("id", "\n=1+1"))
        self.assert_no_partial()

    def test_formula_in_ignored_extra_field_rejected(self):
        with self.assertRaises(ValueError):
            self.publish(rows=[{"id": "A", "amount": "1.00", "extra": "\u200b=2+2"}])
        self.assert_no_partial()

    def test_rollback_preserves_existing_evidence(self):
        self.path.write_bytes(b"PREVIOUS_AUDIT_EVIDENCE")
        with self.assertRaises(ValueError):
            self.publish(rows=[{"id": "A", "amount": "1.00"}, {"id": "\t=private", "amount": "2.00"}])
        self.assertEqual(self.path.read_bytes(), b"PREVIOUS_AUDIT_EVIDENCE")
        self.assertFalse(list(self.path.parent.glob("*.partial")))

    def test_dangerous_formula_rejection_does_not_read_later_row(self):
        seen = []
        def data():
            for value in ("\t=1+1", "DO_NOT_CONSUME"):
                seen.append(value)
                yield {"id": value, "amount": "0.10"}
        with self.assertRaises(ValueError):
            self.publish(rows=data())
        self.assertEqual(seen, ["\t=1+1"])
        self.assert_no_partial()

    def test_private_data_not_exposed_in_error_chain(self):
        private = "\t=PRIVATE_CLAIM_345"
        try:
            self.publish(rows=[{"id": private, "amount": "0.10"}])
        except ValueError as error:
            self.assertEqual(str(error), "Unsafe or non-text CSV report cell")
            self.assertIsNone(error.__context__)
            self.assertIsNone(error.__cause__)
            self.assertNotIn(private, repr(error))
        else:
            self.fail("financial formula-like value escaped CSV boundary")
        self.assert_no_partial()

    def test_explicit_sanitizer_apostrophe_escape_roundtrip(self):
        def safe(value):
            value = str(value)
            return "'" + value if has_unescaped_formula_prefix(value) else value
        self.publish(rows=[{"id": " \t=2+2", "amount": Decimal("0.10")}], cell=safe)
        with self.path.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [{"id": "' \t=2+2", "amount": "0.10"}])

    def test_negative_and_multiline_evidence_preserved(self):
        self.publish(rows=[{"id": "example\n=literal second line", "amount": Decimal("-23.10")}])
        with self.path.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [{"id": "example\n=literal second line", "amount": "-23.10"}])


if __name__ == "__main__":
    unittest.main()
