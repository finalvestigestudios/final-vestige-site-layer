"""R216: negative formula and Unicode-prefix checks at shared CSV publication boundary.

All values are synthetic; no customer or financial account records are used.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from fvs_suite.atomic_reports import write_csv_report
from fvs_suite.csv_formula_guard import has_unescaped_formula_prefix


class NegativeFormulaCustodyR216(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r216-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.path = self.folder / "evidence.csv"

    def save(self, rows=None, fields=("id", "amount"), sanitizer=str, path=None):
        if rows is None:
            rows = [{"id": "INV-001", "amount": Decimal("-23.10")}]
        return write_csv_report(path or self.path, fields, rows, sanitizer)

    def assert_no_partial(self):
        self.assertFalse(self.path.exists())
        self.assertEqual(list(self.folder.glob("*.partial")), [])

    def read(self, path=None):
        with (path or self.path).open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_detect_non_numeric_minus_formula_payloads(self):
        for value in ("-SUM(1)", "-HYPERLINK(\"https://invalid.test\",\"x\")",
                      "-cmd|' /C calc'!A0", "-A1", "-2+2", "--1", "-@SUM(A1)"):
            with self.subTest(value=value):
                self.assertTrue(has_unescaped_formula_prefix(value))

    def test_detect_minus_after_whitespace_or_invisible_prefix(self):
        for value in (" -SUM(A1)", "\t-2+2", "\u200b\ufeff-HYPERLINK(1)",
                      "\u2060\n-A1", "\u00a0--1"):
            with self.subTest(value=value):
                self.assertTrue(has_unescaped_formula_prefix(value))

    def test_detect_formula_after_format_combining_control_prefix(self):
        for prefix in ("\u034f", "\u2066", "\u2069", "\u00ad", "\u061c", "\u20dd", "\x1b"):
            with self.subTest(prefix=repr(prefix)):
                self.assertTrue(has_unescaped_formula_prefix(prefix + "=1+1"))
                self.assertTrue(has_unescaped_formula_prefix(prefix + "-SUM(A1)"))

    def test_guard_allows_canonical_negative_decimal_amounts(self):
        for value in ("-23.10", "-0", "-0.000", "-12", "-00012.75", " -23.10", "\t-23.10"):
            with self.subTest(value=value):
                self.assertFalse(has_unescaped_formula_prefix(value))

    def test_guard_rejects_noncanonical_negative_strings(self):
        for value in ("-", "-1E+2", "-.50", "-1.2.3", "-12 USD", "-$45.10", "-１", "-0;=1"):
            with self.subTest(value=value):
                self.assertTrue(has_unescaped_formula_prefix(value))

    def test_guard_preserves_apostrophe_escaped_cells(self):
        for value in ("'-SUM(A1)", " \u200b'-2+2", "'-A1", "'\u034f=1+1"):
            with self.subTest(value=value):
                self.assertFalse(has_unescaped_formula_prefix(value))

    def test_guard_preserves_plain_and_internal_hyphen_evidence(self):
        for value in ("", "AB-123", "due-date", "text\n-SUM(A1)", " -23.10", "(23.10)"):
            with self.subTest(value=value):
                self.assertFalse(has_unescaped_formula_prefix(value))

    def test_direct_minus_formula_value_rejected_before_publish(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text CSV report cell"):
            self.save(rows=[{"id": "-SUM(A1)", "amount": "0.10"}])
        self.assert_no_partial()

    def test_direct_minus_formula_header_rejected_before_staging(self):
        with self.assertRaises(ValueError):
            self.save(fields=("id", " -HYPERLINK(A1)"))
        self.assert_no_partial()

    def test_ignored_extra_minus_formula_is_still_rejected(self):
        with self.assertRaises(ValueError):
            self.save(rows=[{"id": "A", "amount": "0.10", "extra": "-A1"}])
        self.assert_no_partial()

    def test_new_combining_prefix_guarded_in_row(self):
        with self.assertRaises(ValueError):
            self.save(rows=[{"id": "\u034f=2+2", "amount": "0.10"}])
        self.assert_no_partial()

    def test_new_bidi_prefix_guarded_in_header(self):
        with self.assertRaises(ValueError):
            self.save(fields=("id", "\u2066+2"))
        self.assert_no_partial()

    def test_static_error_does_not_expose_payload_or_exception_context(self):
        secret = "-HYPERLINK(PRIVATE_ACCOUNT_786)"
        try:
            self.save(rows=[{"id": secret, "amount": "1.00"}])
        except ValueError as error:
            self.assertEqual(str(error), "Unsafe or non-text CSV report cell")
            self.assertIsNone(error.__cause__)
            self.assertIsNone(error.__context__)
            self.assertNotIn(secret, repr(error))
        else:
            self.fail("formula-like financial payload escaped validation")
        self.assert_no_partial()

    def test_existing_evidence_is_not_overwritten(self):
        self.path.write_bytes(b"ORIGINAL_SIGNED_EVIDENCE")
        with self.assertRaises(ValueError):
            self.save(rows=[{"id": "A", "amount": "1.00"},
                            {"id": "-A1", "amount": "2.00"}])
        self.assertEqual(self.path.read_bytes(), b"ORIGINAL_SIGNED_EVIDENCE")
        self.assertEqual(list(self.folder.glob("*.partial")), [])

    def test_rejected_minus_does_not_consume_later_rows(self):
        visited = []
        def source():
            for label in ("-SUM(1)", "SENSITIVE_UNREAD_ROW"):
                visited.append(label)
                yield {"id": label, "amount": "1.00"}
        with self.assertRaises(ValueError):
            self.save(rows=source())
        self.assertEqual(visited, ["-SUM(1)"])
        self.assert_no_partial()

    def test_decimal_negative_roundtrip_exact(self):
        self.save()
        self.assertEqual(self.read(), [{"id": "INV-001", "amount": "-23.10"}])
        self.assertEqual(self.path.read_bytes()[:3], b"\xef\xbb\xbf")

    def test_apostrophe_sanitizer_handles_formula_and_hyphen_text(self):
        def safe(value):
            value = str(value)
            return "'" + value if has_unescaped_formula_prefix(value) else value
        self.save(rows=[{"id": "-SUM(A1)", "amount": Decimal("-0.10")}], sanitizer=safe)
        self.assertEqual(self.read(), [{"id": "'-SUM(A1)", "amount": "-0.10"}])

    def test_apostrophe_sanitizer_can_preserve_hyphen_label(self):
        def safe(value):
            value = str(value)
            return "'" + value if has_unescaped_formula_prefix(value) else value
        self.save(rows=[{"id": "-review required", "amount": Decimal("0.00")}], sanitizer=safe)
        self.assertEqual(self.read(), [{"id": "'-review required", "amount": "0.00"}])

    def test_bytes_deterministic_for_identical_inputs(self):
        self.save()
        other = self.folder / "evidence-two.csv"
        self.save(path=other)
        self.assertEqual(self.path.read_bytes(), other.read_bytes())

    def test_existing_r215_whitespace_guard_still_applies(self):
        with self.assertRaises(ValueError):
            self.save(rows=[{"id": "\u200b=2+2", "amount": "1.00"}])
        self.assert_no_partial()

    def test_existing_capacity_limit_still_applies(self):
        with self.assertRaisesRegex(ValueError, "cell size limit"):
            self.save(rows=[{"id": "x" * 1_048_577, "amount": "1.00"}])
        self.assert_no_partial()


if __name__ == "__main__":
    unittest.main()
