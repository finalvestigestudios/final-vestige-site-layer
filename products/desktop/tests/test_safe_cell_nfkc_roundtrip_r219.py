"""R219: shared export sanitizer must agree with the R218 CSV formula gate.

Synthetic local fixtures only; no network requests, customer values or premium
download paths. All findings are for human review, never auto-approval.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine
from fvs_suite.atomic_reports import write_csv_report
from fvs_suite.csv_formula_guard import has_unescaped_formula_prefix


COMPATIBILITY = (
    ("＝", "SUM(A1)"), ("﹦", "2+2"),
    ("＋", "1+2"), ("﹢", "SUM(A1)"),
    ("＠", "SUM(A1)"), ("﹫", "HYPERLINK(A1)"),
    ("－", "SUM(A1)"), ("﹣", "12.30"),
)


class CompatibilitySanitizerR219(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r219-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.out = self.root / "out"
        self.out.mkdir()

    def csv_input(self, name, headers, values):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(values)
        return path

    def read(self, path):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_sanitizer_neutralizes_all_nfkc_operator_forms(self):
        for op, rest in COMPATIBILITY:
            with self.subTest(op=op):
                raw = op + rest
                self.assertTrue(has_unescaped_formula_prefix(raw))
                self.assertEqual(engine.safe_cell(raw), "'" + raw)

    def test_compatible_minus_numeric_text_escapes_not_rewritten(self):
        for raw in ("－12.30", "﹣12.30", "－0"):
            with self.subTest(raw=raw):
                self.assertEqual(engine.safe_cell(raw), "'" + raw)

    def test_canonical_negative_money_remains_numeric(self):
        for money in ("-12.30", "-0", "-0.00", " -12.30", Decimal("-125.03")):
            with self.subTest(money=money):
                self.assertEqual(engine.safe_cell(money), str(money))

    def test_existing_ascii_formula_policy_unaffected(self):
        for raw in ("=2+2", "+SUM(A1)", "@x", "-SUM(A1)", "-1e4"):
            with self.subTest(raw=raw):
                self.assertEqual(engine.safe_cell(raw), "'" + raw)

    def test_existing_apostrophe_escape_is_idempotent(self):
        for raw in ("'=2+2", "'＝SUM(A1)", "'－1"):
            with self.subTest(raw=raw):
                self.assertEqual(engine.safe_cell(raw), raw)
                self.assertEqual(engine.safe_cell(engine.safe_cell(raw)), raw)

    def test_nonleading_compatibility_and_unicode_prose_unchanged(self):
        for raw in ("Vendor＝ABC", "Acct﹢2", "Invoice－1", "東京", "Café", "   vendor"):
            with self.subTest(raw=raw):
                self.assertEqual(engine.safe_cell(raw), raw)

    def test_ignored_marks_before_compatible_operator_are_escaped(self):
        for raw in ("\u200b＝2+2", "\u2066﹢SUM(A1)", " \u034f﹫SUM(A1)"):
            with self.subTest(raw=repr(raw)):
                self.assertEqual(engine.safe_cell(raw), "'" + raw)

    def test_no_nfkc_canonicalization_of_evidence(self):
        for op, rest in COMPATIBILITY:
            raw = op + rest
            self.assertEqual(engine.safe_cell(raw)[1:], raw)

    def test_shared_save_publishes_safely_escaped_exact_values(self):
        values = [op + rest for op, rest in COMPATIBILITY]
        report = engine.save(self.out, "evidence", ("id", "amount"),
                             ({"id": value, "amount": Decimal("-12.30")}
                              for value in values))
        actual = self.read(report)
        self.assertEqual([row["id"] for row in actual], ["'" + val for val in values])
        self.assertEqual([row["amount"] for row in actual], ["-12.30"] * len(values))
        self.assertTrue(report.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertFalse(list(self.out.glob(".*.partial")))

    def test_writer_direct_path_sanitizes_compatibility_header(self):
        path = self.out / "header.csv"
        write_csv_report(path, ("＝source", "amount"),
                         [{"＝source": "row-1", "amount": "-1.00"}],
                         engine.safe_cell)
        self.assertEqual(self.read(path), [{"'＝source": "row-1", "amount": "-1.00"}])

    def test_writer_direct_path_sanitizes_ignored_extra_value(self):
        path = self.out / "extra.csv"
        write_csv_report(path, ("id", "amount"),
                         [{"id": "R-1", "amount": "-1.00", "ignored": "＠HYPERLINK(A1)"}],
                         engine.safe_cell)
        self.assertEqual(self.read(path), [{"id": "R-1", "amount": "-1.00"}])

    def test_equivalent_publishes_byte_deterministically(self):
        rows = [{"id": "＝1+1", "amount": Decimal("-0.01")}]
        a, b = self.out / "a.csv", self.out / "b.csv"
        write_csv_report(a, ("id", "amount"), rows, engine.safe_cell)
        write_csv_report(b, ("id", "amount"), rows, engine.safe_cell)
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_existing_report_never_overwritten(self):
        existing = self.out / "immutable.csv"
        existing.write_bytes(b"PRIVATE_EXISTING_EVIDENCE")
        with patch("fvs_suite.engine.outpath", return_value=existing):
            with self.assertRaises(FileExistsError):
                engine.save(self.out, "immutable", ("id",), [{"id": "＝2+2"}])
        self.assertEqual(existing.read_bytes(), b"PRIVATE_EXISTING_EVIDENCE")
        self.assertFalse(list(self.out.glob(".*.partial")))

    def test_ledgerdiff_real_csv_source_identity(self):
        left = self.csv_input("left.csv", ("id", "amount"),
                              [("＝LEDGER-1", "12.50")])
        right = self.csv_input("right.csv", ("id", "amount"),
                               [("＝LEDGER-1", "12.50")])
        lraw, rraw = left.read_bytes(), right.read_bytes()
        report = engine.ledger_diff(str(left), str(right), self.out)[0]
        row = self.read(report)[0]
        self.assertEqual(row["left_ids"], "'＝LEDGER-1")
        self.assertEqual(row["right_ids"], "'＝LEDGER-1")
        self.assertEqual(row["difference"], "0.00")
        self.assertEqual(row["left_source_sha256"], hashlib.sha256(lraw).hexdigest())
        self.assertEqual(row["right_source_sha256"], hashlib.sha256(rraw).hexdigest())
        self.assertEqual((left.read_bytes(), right.read_bytes()), (lraw, rraw))

    def test_invoice_twin_real_csv_vendor_identity(self):
        input_path = self.csv_input("invoice.csv",
                ("vendor", "invoice_number", "amount", "date"),
                [("＠ACME", "A-1", "50.00", "2026-10-01"),
                 ("＠ACME", "A1", "50.00", "2026-10-02")])
        source = input_path.read_bytes()
        row = self.read(engine.invoice_twins(str(input_path), self.out)[0])[0]
        self.assertEqual(row["vendor"], "'＠ACME")
        self.assertEqual(row["vendor_b"], "'＠ACME")
        self.assertEqual(row["source_sha256"], hashlib.sha256(source).hexdigest())
        self.assertEqual(input_path.read_bytes(), source)

    def test_spendmap_real_csv_vendor_identity(self):
        input_path = self.csv_input("spend.csv",
                ("vendor", "amount", "date", "category"),
                [("＋ACME", "10.00", "2026-10-01", "Parts")])
        source = input_path.read_bytes()
        row = self.read(engine.spend_map(str(input_path), self.out)[0])[0]
        self.assertEqual(row["source_vendor_labels"], "'＋ACME")
        self.assertEqual(row["amount"], "10.00")
        self.assertEqual(row["source_sha256"], hashlib.sha256(source).hexdigest())
        self.assertEqual(input_path.read_bytes(), source)

    def test_no_silent_amount_renormalization(self):
        values = [Decimal("-0.01"), Decimal("12345.6700"), "0.00"]
        report = engine.save(self.out, "numbers", ("id", "amount"),
                             ({"id": str(i), "amount": value}
                              for i, value in enumerate(values)))
        self.assertEqual([r["amount"] for r in self.read(report)],
                         ["-0.01", "12345.6700", "0.00"])


if __name__ == "__main__":
    unittest.main()
