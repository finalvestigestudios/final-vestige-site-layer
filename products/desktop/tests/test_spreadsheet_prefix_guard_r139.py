"""R139: synthetic spreadsheet invisible-prefix safety and financial report regressions."""
from __future__ import annotations
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fvs_suite import engine


class SpreadsheetPrefixGuardR139(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r139-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.output = self.root / "out"
        self.output.mkdir()

    def csv_input(self, name, headers, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def read(self, path):
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    def test_formula_operator_boundaries(self):
        for value in ("=2+2", "+SUM(A1)", "@HYPERLINK(A1)", "+cmd|'/C calc'!A0"):
            with self.subTest(operator=value[0]):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_negative_expressions_escaped(self):
        for value in ("-SUM(A1)", "-1e4", "-3,000", "-+1"):
            with self.subTest(length=len(value)):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_negative_money_stays_numeric(self):
        for value in ("-0", "-0.01", "-12.3400", "   -5.25", " -0.00"):
            with self.subTest(length=len(value)):
                self.assertEqual(engine.safe_cell(value), value)

    def test_ascii_spaced_formula_escaped(self):
        for value in (" =2+2", " +SUM(A1)", "  @x", " -SUM(A1)"):
            with self.subTest(length=len(value)):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_leading_ascii_controls_escaped(self):
        for code in (1, 9, 10, 13, 31, 127, 133, 159):
            value = chr(code) + "=2+2"
            with self.subTest(code=code):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_bidi_control_prefixes_escaped(self):
        for code in (0x061C, 0x200E, 0x200F, 0x202A, 0x202E, 0x2066, 0x2069):
            value = " " + chr(code) + "@SUM(A1)"
            with self.subTest(code=code):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_zero_width_prefixes_escaped(self):
        for code in (0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF):
            value = chr(code) + "=2+2"
            with self.subTest(code=code):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_exotic_unicode_whitespace_prefixes_escaped(self):
        for code in (0x00A0, 0x1680, 0x2007, 0x202F, 0x205F, 0x3000):
            value = "  " + chr(code) + "-1"
            with self.subTest(code=code):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_variation_selector_prefixes_escaped(self):
        for code in (0x180B, 0xFE0F, 0xE0100, 0xE01EF):
            value = chr(code) + "Label"
            with self.subTest(code=code):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_combining_prefixes_escaped(self):
        for code in (0x0301, 0x034F, 0x20DD):
            value = chr(code) + "=cmd"
            with self.subTest(code=code):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_private_use_and_unassigned_prefixes_escaped(self):
        for code in (0xE000, 0x0378):
            value = chr(code) + "@x"
            with self.subTest(code=code):
                self.assertEqual(engine.safe_cell(value), "'" + value)

    def test_benign_multilingual_text_stays_visible(self):
        for value in ("", "Café", "東京", "مورد", "  vendor", "100.00", "'=2+2"):
            with self.subTest(length=len(value)):
                self.assertEqual(engine.safe_cell(value), value)

    def test_nonleading_hidden_text_not_rewritten(self):
        self.assertEqual(engine.safe_cell("Vendor\u200b=2+2"), "Vendor\u200b=2+2")
        self.assertEqual(engine.safe_cell("   "), "   ")

    def test_real_csv_roundtrip_including_exact_money(self):
        values = ("=2+2", "\u200b=2+2", " \u202e@x", "\tname", "-4.00", "Café")
        path = engine.save(self.output, "boundary", ("name", "amount"),
                           ({"name": v, "amount": "-0.01"} for v in values))
        rows = self.read(path)
        self.assertEqual([r["name"] for r in rows], [engine.safe_cell(v) for v in values])
        self.assertTrue(all(r["amount"] == "-0.01" for r in rows))
        self.assertFalse(list(self.output.glob(".*.partial")))

    def test_existing_report_never_overwritten(self):
        target = self.output / "fixed.csv"
        target.write_bytes(b"previous audit evidence")
        with patch("fvs_suite.engine.outpath", return_value=target):
            with self.assertRaises(FileExistsError):
                engine.save(self.output, "fixed", ("name",), [{"name": "\u200b=2+2"}])
        self.assertEqual(target.read_bytes(), b"previous audit evidence")

    def test_failed_conversion_keeps_no_partial_artifact(self):
        class BadCell:
            def __str__(self):
                raise ValueError("synthetic invalid field")
        with self.assertRaises(ValueError):
            engine.save(self.output, "invalid", ("name",),
                        [{"name": "safe"}, {"name": BadCell()}])
        self.assertEqual(list(self.output.iterdir()), [])

    def test_ledger_source_formula_label_still_traces_digests(self):
        left = self.csv_input("left.csv", ("id", "amount"), [("=A-1", "12.50")])
        right = self.csv_input("right.csv", ("id", "amount"), [("=A-1", "12.50")])
        source_bytes = (left.read_bytes(), right.read_bytes())
        row = self.read(engine.ledger_diff(str(left), str(right), self.output)[0])[0]
        self.assertEqual(row["left_ids"], "'=A-1")
        self.assertEqual(row["right_ids"], "'=A-1")
        self.assertEqual(row["difference"], "0.00")
        self.assertEqual(row["left_source_sha256"], hashlib.sha256(source_bytes[0]).hexdigest())
        self.assertEqual(row["right_source_sha256"], hashlib.sha256(source_bytes[1]).hexdigest())
        self.assertEqual((left.read_bytes(), right.read_bytes()), source_bytes)

    def test_invoice_vendor_hidden_prefix_is_escaped(self):
        label = "\u200b=ACME"
        source = self.csv_input("invoices.csv",
            ("vendor", "invoice_number", "amount", "date"),
            [(label, "A-1", "50.00", "2026-10-01"),
             (label, "A1", "50.00", "2026-10-02")])
        raw = source.read_bytes()
        rows = self.read(engine.invoice_twins(str(source), self.output)[0])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["vendor"], "'" + label)
        self.assertEqual(rows[0]["vendor_b"], "'" + label)
        self.assertEqual(rows[0]["amount_a"], "50.00")
        self.assertEqual(rows[0]["source_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(source.read_bytes(), raw)

    def test_spend_vendor_formula_label_is_escaped(self):
        source = self.csv_input("spend.csv",
            ("vendor", "amount", "date", "category"),
            [("=ACME", "10.00", "2026-10-01", "Parts")])
        raw = source.read_bytes()
        rows = self.read(engine.spend_map(str(source), self.output)[0])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_vendor_labels"], "'=ACME")
        self.assertEqual(rows[0]["amount"], "10.00")
        self.assertEqual(rows[0]["source_sha256"], hashlib.sha256(raw).hexdigest())

    def test_money_writer_safe_values_not_rounded_or_replaced(self):
        values = ("-0.01", "-1.20", "0.00", "125.35", "-1e3")
        path = engine.save(self.output, "amounts", ("amount",),
                           ({"amount": amount} for amount in values))
        self.assertEqual([r["amount"] for r in self.read(path)],
                         ["-0.01", "-1.20", "0.00", "125.35", "'-1e3"])


if __name__ == "__main__":
    unittest.main()
