"""R152 source-owned synthetic CSV tests: vendor-month gross charge/credit review."""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from decimal import Inexact, Rounded, localcontext
from pathlib import Path
from fvs_suite import engine


class SpendVendorMonthR152(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-spend-r152-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.input = self.root / "synthetic-spend.csv"

    @staticmethod
    def item(amount, month="01", category="Parts", vendor="ACME", note=""):
        return (vendor, amount, f"2026-{month}-01", category, note)

    def source(self, rows):
        with self.input.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        return self.input

    def report(self):
        path = engine.spend_map(self.input, self.root)[0]
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return list(reader), tuple(reader.fieldnames)

    def pick(self, rows, month="2026-01", category="Parts", vendor="ACME"):
        matches = [row for row in rows if
                   (row["vendor_key"], row["month"], row["category"]) ==
                   (vendor, month, category)]
        self.assertEqual(len(matches), 1)
        return matches[0]

    @staticmethod
    def flow(row):
        return (row["vendor_month_gross_charges"],
                row["vendor_month_gross_credits"],
                row["vendor_month_offset_review"])

    def test_cross_category_offset_now_visible_both_rows(self):
        self.source([self.item("150", category="Parts"),
                     self.item("-140", category="Services")])
        rows, _ = self.report()
        for category in ("Parts", "Services"):
            row = self.pick(rows, category=category)
            self.assertEqual(self.flow(row),
                             ("150.00", "140.00", "review_vendor_month_mixed_sign_offset"))
            self.assertEqual(row["credit_offset_review"], "")

    def test_matching_net_and_hidden_cross_category_gross(self):
        self.source([self.item("100", category="Parts"),
                     self.item("-100", category="Services")])
        rows, _ = self.report()
        self.assertEqual(self.pick(rows)["vendor_month_total"], "0.00")
        self.assertEqual(self.flow(self.pick(rows))[:2], ("100.00", "100.00"))

    def test_single_category_mixed_sign_keeps_existing_flag(self):
        self.source([self.item("50"), self.item("-20")])
        row = self.pick(self.report()[0])
        self.assertEqual(row["credit_offset_review"], "review_mixed_sign_offset")
        self.assertEqual(self.flow(row),
                         ("50.00", "20.00", "review_vendor_month_mixed_sign_offset"))

    def test_positive_only_has_no_monthly_offset(self):
        self.source([self.item("20", category="Parts"),
                     self.item("30", category="Services")])
        self.assertEqual(self.flow(self.pick(self.report()[0])),
                         ("50.00", "0.00", ""))

    def test_credit_only_has_no_monthly_offset(self):
        self.source([self.item("-20"), self.item("-10", category="Services")])
        self.assertEqual(self.flow(self.pick(self.report()[0])),
                         ("0.00", "30.00", ""))

    def test_zero_only_has_no_monthly_offset(self):
        self.source([self.item("0"), self.item("-0", category="Services")])
        self.assertEqual(self.flow(self.pick(self.report()[0])),
                         ("0.00", "0.00", ""))

    def test_negative_zero_not_a_credit(self):
        self.source([self.item("5"), self.item("-0.00", category="Services")])
        self.assertEqual(self.flow(self.pick(self.report()[0])),
                         ("5.00", "0.00", ""))

    def test_multiple_categories_sum_exactly(self):
        self.source([self.item("11.11"), self.item("0.09", category="Services"),
                     self.item("-1.20", category="Office"),
                     self.item("-0.01", category="Travel")])
        for row in self.report()[0]:
            self.assertEqual(self.flow(row)[:2], ("11.20", "1.21"))

    def test_vendor_isolation(self):
        self.source([self.item("9"), self.item("-7", vendor="OTHER")])
        rows, _ = self.report()
        self.assertEqual(self.flow(self.pick(rows)), ("9.00", "0.00", ""))
        self.assertEqual(self.flow(self.pick(rows, vendor="OTHER")),
                         ("0.00", "7.00", ""))

    def test_month_isolation(self):
        self.source([self.item("9"), self.item("-7", month="02")])
        rows, _ = self.report()
        self.assertEqual(self.flow(self.pick(rows)), ("9.00", "0.00", ""))
        self.assertEqual(self.flow(self.pick(rows, month="2026-02")),
                         ("0.00", "7.00", ""))

    def test_category_month_offset_does_not_create_bucket_offset(self):
        self.source([self.item("100"), self.item("-50", category="Office")])
        rows, _ = self.report()
        self.assertEqual(self.pick(rows)["credit_offset_review"], "")
        self.assertEqual(self.pick(rows, category="Office")["credit_offset_review"], "")
        self.assertEqual(self.pick(rows)["vendor_month_offset_review"],
                         "review_vendor_month_mixed_sign_offset")

    def test_normalized_vendor_rows_are_reviewable(self):
        self.source([self.item("10", vendor="A-CME"),
                     self.item("-9", vendor="ACME", category="Office")])
        row = self.pick(self.report()[0])
        self.assertIn("normalized_vendor_collision_review", row["flag"])
        self.assertEqual(self.flow(row),
                         ("10.00", "9.00", "review_vendor_month_mixed_sign_offset"))

    def test_uncategorized_credit_is_included(self):
        self.source([self.item("9"), self.item("-2", category="")])
        rows, _ = self.report()
        self.assertEqual(self.flow(self.pick(rows, category="Uncategorized")),
                         ("9.00", "2.00", "review_vendor_month_mixed_sign_offset"))

    def test_vendor_net_baseline_preserved(self):
        self.source([self.item("10", m) for m in ("01", "02", "03")] +
                    [self.item("50", "04", category="Parts"),
                     self.item("-20", "04", category="Office")])
        row = self.pick(self.report()[0], month="2026-04")
        self.assertEqual(row["baseline_median"], "10.00")
        self.assertEqual(row["vendor_month_total"], "30.00")
        self.assertEqual(row["flag"], "review_spike")
        self.assertEqual(self.flow(row)[:2], ("50.00", "20.00"))

    def test_category_spike_logic_preserved(self):
        self.source([self.item("10", m) for m in ("01", "02", "03")] +
                    [self.item("50", "04"), self.item("-20", "04", category="Office")])
        row = self.pick(self.report()[0], month="2026-04")
        self.assertEqual(row["category_review_flag"], "review_category_spike")
        self.assertEqual(row["credit_offset_review"], "")

    def test_sha256_matches_original_import(self):
        self.source([self.item("9"), self.item("-2", category="Office")])
        original = self.input.read_bytes()
        self.assertEqual(self.pick(self.report()[0])["source_sha256"],
                         hashlib.sha256(original).hexdigest())

    def test_import_is_not_modified(self):
        self.source([self.item("9"), self.item("-2", category="Office")])
        original = self.input.read_bytes()
        self.report()
        self.assertEqual(self.input.read_bytes(), original)

    def test_physical_csv_lines_with_multiline_field(self):
        self.source([self.item("9", note="line\nbreak"),
                     self.item("-2", category="Office")])
        rows, _ = self.report()
        self.assertEqual(self.pick(rows)["source_rows"], "2")
        self.assertEqual(self.pick(rows, category="Office")["source_rows"], "4")

    def test_large_decimal_money_exact_and_signed(self):
        self.source([self.item("1000000000000.00"),
                     self.item("-999999999999.99", category="Office")])
        self.assertEqual(self.flow(self.pick(self.report()[0])),
                         ("1000000000000.00", "999999999999.99",
                          "review_vendor_month_mixed_sign_offset"))

    def test_hostile_decimal_context_does_not_round(self):
        self.source([self.item("1000000000000.00"),
                     self.item("-999999999999.99", category="Office")])
        with localcontext() as ctx:
            ctx.prec = 2
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            row = self.pick(self.report()[0])
            self.assertEqual(ctx.prec, 2)
        self.assertEqual(self.flow(row)[:2],
                         ("1000000000000.00", "999999999999.99"))

    def test_deterministic_report_content(self):
        self.source([self.item("7"), self.item("-3", category="Office")])
        self.assertEqual(self.report(), self.report())

    def test_invalid_amount_fails_without_report(self):
        self.source([self.item("7"), self.item("privatebad$-garbage")])
        with self.assertRaises(ValueError) as err:
            engine.spend_map(self.input, self.root)
        self.assertNotIn("privatebad", str(err.exception))
        self.assertEqual(list(self.root.glob("spend-map-*.csv")), [])

    def test_formula_like_vendor_label_is_escaped(self):
        self.source([self.item("7", vendor="=ACME"),
                     self.item("-3", category="Office", vendor="=ACME")])
        row = self.pick(self.report()[0], vendor="ACME")
        self.assertEqual(row["source_vendor_labels"], "'=ACME")
        self.assertEqual(row["vendor_month_offset_review"],
                         "review_vendor_month_mixed_sign_offset")

    def test_schema_includes_three_explicit_monthly_evidence_fields(self):
        self.source([])
        rows, cols = self.report()
        self.assertEqual(rows, [])
        self.assertEqual(cols[-7:-4],
                         ("vendor_month_gross_charges", "vendor_month_gross_credits",
                          "vendor_month_offset_review"))

    def test_no_premium_approval_or_fraud_claim_in_signal(self):
        self.source([self.item("7"), self.item("-3", category="Office")])
        flag = self.pick(self.report()[0])["vendor_month_offset_review"]
        self.assertNotIn("approved", flag)
        self.assertNotIn("fraud", flag)
        self.assertIn("review", flag)


if __name__ == "__main__":
    unittest.main()
