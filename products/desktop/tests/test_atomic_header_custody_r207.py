"""R207: shared six-app CSV headers must receive formula protection and stay distinct."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from fvs_suite.atomic_reports import write_csv_report


def _escape_formula(value: object) -> str:
    """Synthetic conservative sanitizer; live suite calls engine.safe_cell."""
    text = str(value)
    return "'" + text if text.startswith(("=", "+", "@")) or text.startswith("\u200b=") else text


class AuditHeaderCustodyR207(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fv-r207-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "output.csv"

    def save(self, columns, data=(), sanitizer=_escape_formula):
        return write_csv_report(self.target, columns, data, sanitizer)

    def rows(self):
        with self.target.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.reader(f))

    def no_output(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.iterdir()), [])

    def test_header_formula_neutralized_not_just_values(self):
        self.save(("=HYPERLINK(1)", "amount"), [{"=HYPERLINK(1)": "ok", "amount": "=2+3"}])
        self.assertEqual(self.rows(), [["'=HYPERLINK(1)", "amount"], ["ok", "'=2+3"]])
        self.assertTrue(self.target.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_unicode_prefix_header_is_sanitized_by_policy(self):
        self.save(("\u200b=cmd",), [{"\u200b=cmd": "safe"}])
        self.assertEqual(self.rows(), [["'\u200b=cmd"], ["safe"]])

    def test_two_source_fields_cannot_collapse_after_formula_escaping(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or ambiguous"):
            self.save(("=SUM(1)", "'=SUM(1)"), [{"=SUM(1)": "1", "'=SUM(1)": "2"}])
        self.no_output()

    def test_duplicate_unsanitized_columns_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid or duplicate"):
            self.save(("total", "total"))
        self.no_output()

    def test_empty_column_name_is_rejected(self):
        with self.assertRaises(ValueError):
            self.save(("total", ""))
        self.no_output()

    def test_empty_field_collection_is_rejected(self):
        with self.assertRaises(ValueError):
            self.save(())
        self.no_output()

    def test_non_plain_string_field_name_is_rejected(self):
        class ForgedStr(str):
            def __str__(self):
                raise AssertionError("should not invoke caller supplied __str__")
        with self.assertRaises(ValueError):
            self.save((ForgedStr("amount"),))
        self.no_output()

    def test_unexpected_non_string_rendered_header_rejected(self):
        with self.assertRaises(ValueError):
            self.save(("amount",), sanitizer=lambda _: None)
        self.no_output()

    def test_sanitizer_cannot_introduce_nul_or_newline_header(self):
        for bad in ("amount\x00bad", "amount\nbad", "amount\rbad"):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ValueError):
                    self.save(("amount",), sanitizer=lambda _: bad)
                self.no_output()

    def test_same_rendered_header_from_distinct_safe_fields_rejected(self):
        with self.assertRaises(ValueError):
            self.save(("description", "value"), sanitizer=lambda _: "same")
        self.no_output()

    def test_standard_headers_preserved_and_extra_rows_still_sanitized(self):
        visited = []
        def convert(value):
            visited.append(value)
            return str(value)
        self.save(("id", "amount"), [{"id": "a", "amount": "1.20", "ignored": "ignored"}], convert)
        self.assertEqual(self.rows(), [["id", "amount"], ["a", "1.20"]])
        self.assertEqual(visited, ["id", "amount", "a", "1.20", "ignored"])

    def test_lazy_header_generator_is_materialized_once(self):
        seen = []
        def fields():
            for col in ("id", "amount"):
                seen.append(col)
                yield col
        self.save(fields(), [{"id": "a", "amount": "1"}])
        self.assertEqual(seen, ["id", "amount"])
        self.assertEqual(self.rows(), [["id", "amount"], ["a", "1"]])

    def test_prior_evidence_is_never_overwritten(self):
        self.target.write_bytes(b"prior evidence")
        with self.assertRaises(FileExistsError):
            self.save(("id",), [{"id": "new"}])
        self.assertEqual(self.target.read_bytes(), b"prior evidence")
        self.assertEqual(list(self.root.iterdir()), [self.target])

    def test_row_error_leaves_no_partial_or_report(self):
        def rows():
            yield {"id": "one"}
            raise RuntimeError("PRIVATE SYNTHETIC EXCEPTION")
        with self.assertRaises(RuntimeError):
            self.save(("id",), rows())
        self.no_output()


if __name__ == "__main__":
    unittest.main()
