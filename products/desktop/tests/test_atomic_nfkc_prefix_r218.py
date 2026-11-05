"""R218: spreadsheet compatibility-form formula prefixes fail closed.

All data is synthetic, offline and non-sensitive. No premium binaries are used.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import traceback
import unittest

from fvs_suite.atomic_reports import write_csv_report
from fvs_suite.csv_formula_guard import has_unescaped_formula_prefix


SECRET = "PRIVATE_R218_FINANCIAL_REFERENCE_799"
ERROR = "Unsafe or non-text CSV report cell"


class NFKCFormulaPrefixR218(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory(prefix="fvs-r218-")
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        self.target = self.root / "evidence.csv"
        self.fields = ("id", "amount")

    def publish(self, rows=None, fields=None, sanitizer=str, target=None):
        return write_csv_report(
            target or self.target, fields or self.fields,
            rows if rows is not None else [{"id": "INV-001", "amount": Decimal("-12.30")}],
            sanitizer,
        )

    def assert_not_published(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob("*.partial")), [])

    def read(self, target=None):
        with (target or self.target).open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_equal_sign_compatibility_forms_are_formulas(self):
        for prefix in ("＝", "﹦"):
            with self.subTest(prefix=prefix):
                self.assertTrue(has_unescaped_formula_prefix(prefix + "SUM(A1)"))

    def test_plus_sign_compatibility_forms_are_formulas(self):
        for prefix in ("＋", "﹢"):
            with self.subTest(prefix=prefix):
                self.assertTrue(has_unescaped_formula_prefix(prefix + "1+2"))

    def test_at_sign_compatibility_forms_are_formulas(self):
        for prefix in ("＠", "﹫"):
            with self.subTest(prefix=prefix):
                self.assertTrue(has_unescaped_formula_prefix(prefix + "SUM(A1)"))

    def test_minus_compatibility_forms_fail_even_with_numeric_tail(self):
        for prefix in ("－", "﹣"):
            with self.subTest(prefix=prefix):
                self.assertTrue(has_unescaped_formula_prefix(prefix + "12.30"))
                self.assertTrue(has_unescaped_formula_prefix(prefix + "SUM(A1)"))

    def test_format_and_combining_marks_before_compatibility_operator(self):
        for lead in ("\u200b", "\u034f", "\u2066", "\ufeff", "\u20dd"):
            with self.subTest(lead=repr(lead)):
                self.assertTrue(has_unescaped_formula_prefix(lead + "＝2+2"))

    def test_whitespace_before_compatibility_operator(self):
        for lead in (" ", "\t", "\n", "\u3000", "\u00a0"):
            with self.subTest(lead=repr(lead)):
                self.assertTrue(has_unescaped_formula_prefix(lead + "﹢2+2"))

    def test_mixed_ignored_marks_and_compatibility_operator(self):
        self.assertTrue(has_unescaped_formula_prefix("\t\u034f\u2060﹫SUM(1)"))
        self.assertTrue(has_unescaped_formula_prefix("\u2069 \u200b－1"))

    def test_canonical_negative_decimal_still_allowed(self):
        for value in ("-12.30", "-0", "-0.00", " -123.45", "\t-1"):
            with self.subTest(value=value):
                self.assertFalse(has_unescaped_formula_prefix(value))

    def test_apostrophe_escape_still_allowed(self):
        for value in ("'＝2+2", " '﹢2", "\u200b'＠SUM(A1)", "'－SUM(1)"):
            with self.subTest(value=value):
                self.assertFalse(has_unescaped_formula_prefix(value))

    def test_benign_unicode_prose_unmodified(self):
        for value in ("©2026", "レビューが必要", "INVOICE＝A", "\uff21BC", "middle﹦ internally"):
            with self.subTest(value=value):
                self.assertFalse(has_unescaped_formula_prefix(value))

    def test_row_value_compatibility_prefix_rejected(self):
        with self.assertRaisesRegex(ValueError, ERROR):
            self.publish(rows=[{"id": "＝HYPERLINK(A1)", "amount": "1.00"}])
        self.assert_not_published()

    def test_schema_header_compatibility_prefix_rejected_before_stage(self):
        with self.assertRaisesRegex(ValueError, ERROR):
            self.publish(fields=("id", "﹢1+1"))
        self.assert_not_published()

    def test_ignored_extra_field_is_still_sanitized(self):
        with self.assertRaisesRegex(ValueError, ERROR):
            self.publish(rows=[{"id": "A", "amount": "1.00", "unused": "＠SUM(A1)"}])
        self.assert_not_published()

    def test_late_failure_does_not_publish_partial_report(self):
        rows = [{"id": str(i), "amount": "1.00"} for i in range(30)]
        rows.append({"id": "﹦SECRET", "amount": "2.00"})
        with self.assertRaisesRegex(ValueError, ERROR):
            self.publish(rows=rows)
        self.assert_not_published()

    def test_existing_evidence_not_overwritten_on_failure(self):
        self.target.write_bytes(b"SIGNED_EVIDENCE_KEEP")
        with self.assertRaisesRegex(ValueError, ERROR):
            self.publish(rows=[{"id": "﹫DANGEROUS", "amount": "1.00"}])
        self.assertEqual(self.target.read_bytes(), b"SIGNED_EVIDENCE_KEEP")
        self.assertEqual(list(self.root.glob("*.partial")), [])

    def test_manual_safe_cell_escape_and_decimal_roundtrip(self):
        def safe(value):
            text = str(value)
            return "'" + text if has_unescaped_formula_prefix(text) else text
        self.publish(rows=[{"id": "＝SUM(A1)", "amount": Decimal("-12.30")}], sanitizer=safe)
        self.assertEqual(self.read(), [{"id": "'＝SUM(A1)", "amount": "-12.30"}])

    def test_no_later_rows_consumed_after_bad_prefix(self):
        visited = []
        def rows():
            for label in ("﹦1+1", SECRET):
                visited.append(label)
                yield {"id": label, "amount": "1.00"}
        with self.assertRaisesRegex(ValueError, ERROR):
            self.publish(rows=rows())
        self.assertEqual(visited, ["﹦1+1"])
        self.assert_not_published()

    def test_error_has_no_sensitive_exception_context(self):
        try:
            self.publish(rows=[{"id": "＝" + SECRET, "amount": "5.00"}])
        except ValueError as error:
            self.assertEqual(str(error), ERROR)
            self.assertIsNone(error.__context__)
            self.assertIsNone(error.__cause__)
            self.assertNotIn(SECRET, "".join(traceback.format_exception(error)))
        else:
            self.fail("Compatibility-form formula bypassed safe publication")
        self.assert_not_published()

    def test_successful_report_remains_byte_deterministic_and_bom(self):
        self.publish()
        first = self.target.read_bytes()
        other = self.root / "repeat.csv"
        self.publish(target=other)
        self.assertTrue(first.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(first, other.read_bytes())
        self.assertEqual(self.read(), [{"id": "INV-001", "amount": "-12.30"}])

    def test_non_ascii_minus_preserves_original_if_explicitly_escaped(self):
        def safe(value):
            text = str(value)
            return "'" + text if has_unescaped_formula_prefix(text) else text
        self.publish(rows=[{"id": "－review", "amount": "1.00"}], sanitizer=safe)
        self.assertEqual(self.read()[0]["id"], "'－review")


if __name__ == "__main__":
    unittest.main()
