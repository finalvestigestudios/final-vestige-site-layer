"""R153 synthetic end-to-end audit provenance for SpendMap's vendor-month gross totals."""
from __future__ import annotations
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from fvs_suite import engine

class SpendEvidenceCustodyR153(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r153-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.input = self.root / "synthetic-spend.csv"

    @staticmethod
    def item(amount="1.00", vendor="ACME", month="01", category="Parts", note=""):
        return (vendor, amount, f"2026-{month}-01", category, note)

    def source(self, rows):
        with self.input.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        return self.input

    def report(self):
        path = engine.spend_map(self.input, self.root)[0]
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return list(reader), tuple(reader.fieldnames)

    def pick(self, rows, category="Parts", vendor="ACME", month="2026-01"):
        found = [r for r in rows if
                 (r["vendor_key"], r["month"], r["category"]) ==
                 (vendor, month, category)]
        self.assertEqual(len(found), 1)
        return found[0]

    @staticmethod
    def evidence(row):
        return (row["vendor_month_evidence_rows"],
                row["vendor_month_evidence_count"],
                row["vendor_month_evidence_omitted"])

    def test_cross_category_cites_both_sources(self):
        self.source([self.item("150"), self.item("-140", category="Services")])
        rows, _ = self.report()
        for cat in ("Parts", "Services"):
            self.assertEqual(self.evidence(self.pick(rows, cat)), ("2;3", "2", "0"))

    def test_category_only_source_rows_remain_distinct(self):
        self.source([self.item("150"), self.item("-140", category="Services")])
        rows, _ = self.report()
        self.assertEqual(self.pick(rows)["source_rows"], "2")
        self.assertEqual(self.pick(rows, "Services")["source_rows"], "3")
        self.assertEqual(self.evidence(self.pick(rows))[0], "2;3")

    def test_same_category_two_lines(self):
        self.source([self.item("5"), self.item("-1")])
        self.assertEqual(self.evidence(self.pick(self.report()[0])), ("2;3", "2", "0"))

    def test_multiline_csv_records_reference_physical_start(self):
        self.source([self.item("5", note="line\nbreak"), self.item("-3", category="Services")])
        self.assertEqual(self.evidence(self.pick(self.report()[0])), ("2;4", "2", "0"))

    def test_numeric_line_order_beyond_nine(self):
        self.source([self.item(category=f"C{i%3}") for i in range(12)])
        self.assertEqual(self.evidence(self.pick(self.report()[0], "C0")),
                         (";".join(str(i) for i in range(2, 14)), "12", "0"))

    def test_one_record_count(self):
        self.source([self.item("7")])
        self.assertEqual(self.evidence(self.pick(self.report()[0])), ("2", "1", "0"))

    def test_exact_32_limit_has_no_omission(self):
        self.source([self.item() for _ in range(32)])
        self.assertEqual(self.evidence(self.pick(self.report()[0])),
                         (";".join(str(i) for i in range(2, 34)), "32", "0"))

    def test_35_records_report_three_omissions(self):
        self.source([self.item() for _ in range(35)])
        self.assertEqual(self.evidence(self.pick(self.report()[0])),
                         (";".join(str(i) for i in range(2, 34)), "35", "3"))

    def test_70_records_keep_earliest_32(self):
        self.source([self.item() for _ in range(70)])
        refs, count, omitted = self.evidence(self.pick(self.report()[0]))
        self.assertEqual((count, omitted), ("70", "38"))
        self.assertEqual(refs.split(";")[-1], "33")

    def test_31_records_are_not_truncated(self):
        self.source([self.item() for _ in range(31)])
        self.assertEqual(self.evidence(self.pick(self.report()[0]))[1:], ("31", "0"))

    def test_month_count_not_multiplied_by_categories(self):
        self.source([self.item(category=f"C{i%8}") for i in range(40)])
        for row in self.report()[0]:
            self.assertEqual(self.evidence(row)[1:], ("40", "8"))

    def test_month_isolation(self):
        self.source([self.item("5"), self.item("-3", month="02")])
        rows, _ = self.report()
        self.assertEqual(self.evidence(self.pick(rows)), ("2", "1", "0"))
        self.assertEqual(self.evidence(self.pick(rows, month="2026-02")), ("3", "1", "0"))

    def test_vendor_isolation(self):
        self.source([self.item("5"), self.item("-3", vendor="OTHER")])
        rows, _ = self.report()
        self.assertEqual(self.evidence(self.pick(rows)), ("2", "1", "0"))
        self.assertEqual(self.evidence(self.pick(rows, vendor="OTHER")), ("3", "1", "0"))

    def test_colliding_normalized_vendors_cited_and_flagged(self):
        self.source([self.item("5", vendor="A-CME"),
                     self.item("-3", vendor="ACME", category="Services")])
        row = self.pick(self.report()[0])
        self.assertEqual(self.evidence(row), ("2;3", "2", "0"))
        self.assertIn("normalized_vendor_collision_review", row["flag"])

    def test_uncategorized_credit_is_cited(self):
        self.source([self.item("5"), self.item("-3", category="")])
        self.assertEqual(self.evidence(self.pick(self.report()[0], "Uncategorized")),
                         ("2;3", "2", "0"))

    def test_zero_amounts_still_contribute_source_evidence(self):
        self.source([self.item("0"), self.item("-0", category="Services")])
        row = self.pick(self.report()[0])
        self.assertEqual(self.evidence(row), ("2;3", "2", "0"))
        self.assertEqual(row["vendor_month_offset_review"], "")

    def test_existing_exact_gross_net_totals_unchanged(self):
        self.source([self.item("150"), self.item("-140", category="Services")])
        row = self.pick(self.report()[0])
        self.assertEqual((row["vendor_month_total"],
                          row["vendor_month_gross_charges"],
                          row["vendor_month_gross_credits"],
                          row["vendor_month_offset_review"]),
                         ("10.00", "150.00", "140.00",
                          "review_vendor_month_mixed_sign_offset"))

    def test_original_sha256_preserved(self):
        self.source([self.item("5"), self.item("-3", category="Services")])
        before = self.input.read_bytes()
        self.assertEqual(self.pick(self.report()[0])["source_sha256"],
                         hashlib.sha256(before).hexdigest())

    def test_original_source_never_mutated(self):
        self.source([self.item("5"), self.item("-3", category="Services")])
        before = self.input.read_bytes()
        self.report()
        self.assertEqual(self.input.read_bytes(), before)

    def test_formula_like_vendor_labels_still_escaped(self):
        self.source([self.item("5", vendor="=ACME"),
                     self.item("-3", vendor="=ACME", category="Services")])
        row = self.pick(self.report()[0])
        self.assertEqual(self.evidence(row), ("2;3", "2", "0"))
        self.assertTrue(row["source_vendor_labels"].startswith("'"))

    def test_invalid_money_fails_closed_without_report(self):
        self.source([self.item("5"), self.item("PRIVATE-INVALID")])
        with self.assertRaises(ValueError) as caught:
            engine.spend_map(self.input, self.root)
        self.assertNotIn("PRIVATE-INVALID", str(caught.exception))
        self.assertEqual(list(self.root.glob("spend-map-*.csv")), [])

    def test_repeated_reports_deterministic(self):
        self.source([self.item("5"), self.item("-3", category="Services")])
        self.assertEqual(self.report(), self.report())

    def test_schema_precedes_existing_gross_columns(self):
        self.source([])
        rows, cols = self.report()
        self.assertEqual(rows, [])
        i = cols.index("vendor_month_evidence_rows")
        self.assertEqual(cols[i:i+6], (
            "vendor_month_evidence_rows",
            "vendor_month_evidence_count",
            "vendor_month_evidence_omitted",
            "vendor_month_gross_charges",
            "vendor_month_gross_credits",
            "vendor_month_offset_review"))

    def test_legacy_last_seven_columns_unmodified(self):
        self.source([])
        _, cols = self.report()
        self.assertEqual(cols[-7:-4],
                         ("vendor_month_gross_charges", "vendor_month_gross_credits",
                          "vendor_month_offset_review"))

    def test_many_categories_keep_bounded_references(self):
        self.source([self.item(category=f"C{i%40}") for i in range(400)])
        rows, _ = self.report()
        self.assertEqual(len(rows), 40)
        for row in rows:
            refs, count, omitted = self.evidence(row)
            self.assertEqual((count, omitted), ("400", "368"))
            self.assertLessEqual(len(refs.split(";")), 32)

if __name__ == "__main__":
    unittest.main()
