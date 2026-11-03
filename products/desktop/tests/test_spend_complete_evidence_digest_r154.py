"""R154: independently check complete vendor-month physical-line membership fingerprints.

Synthetic local CSVs only. No network, production data, premium file, or legal decision.
"""
from __future__ import annotations

import csv
import hashlib
import re
import tempfile
import unittest
from decimal import Decimal, getcontext, localcontext
from pathlib import Path

from fvs_suite import engine
from fvs_suite.spend_analysis import summarize_spend


def reference_digest(source_sha, vendor, month, physical_lines):
    """Independent, versioned ASCII wire-format reference implementation."""
    lines = sorted(physical_lines)
    fragments = ["FVS-SPEND-VENDOR-MONTH-LINES-v1", source_sha,
                 vendor, month, str(len(lines)), *(str(n) for n in lines)]
    return hashlib.sha256(("\n".join(fragments) + "\n").encode("ascii")).hexdigest()


class SpendCompleteDigestR154(unittest.TestCase):
    def setUp(self):
        ctx = tempfile.TemporaryDirectory(prefix="fvs-r154-synthetic-")
        self.addCleanup(ctx.cleanup)
        self.root = Path(ctx.name)
        self.source_path = self.root / "private-fixture.csv"

    @staticmethod
    def item(amount="1.00", vendor="ACME", month="01", category="Parts", note=""):
        return (vendor, amount, "2026-" + month + "-01", category, note)

    def write(self, rows):
        with self.source_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        return hashlib.sha256(self.source_path.read_bytes()).hexdigest()

    def report(self):
        result_path = engine.spend_map(self.source_path, self.root)[0]
        with result_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader), tuple(reader.fieldnames or [])

    def select(self, rows, vendor="ACME", month="2026-01", category="Parts"):
        selected = [r for r in rows if (r["vendor_key"], r["month"], r["category"])
                    == (vendor, month, category)]
        self.assertEqual(len(selected), 1)
        return selected[0]

    def direct(self, records, source_sha="a" * 64):
        return summarize_spend(
            records, normalize_vendor=engine.key, parse_date=engine.parse_date,
            parse_money=engine.money, format_money=engine.dollars,
            source_sha256=source_sha)

    def test_basic_digest_matches_independent_reference(self):
        sha = self.write([self.item("150"), self.item("-140", category="Services")])
        rows, _ = self.report()
        self.assertEqual(self.select(rows)["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-01", [2, 3]))

    def test_digest_contains_lowercase_hex_only(self):
        self.write([self.item()])
        digest = self.select(self.report()[0])["vendor_month_evidence_sha256"]
        self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_domain_separator_prevents_unqualified_line_hash(self):
        self.write([self.item()])
        row = self.select(self.report()[0])
        self.assertNotEqual(row["vendor_month_evidence_sha256"],
                            hashlib.sha256(b"2\n").hexdigest())

    def test_one_contributor(self):
        sha = self.write([self.item()])
        row = self.select(self.report()[0])
        self.assertEqual(row["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-01", [2]))
        self.assertEqual(row["vendor_month_evidence_count"], "1")

    def test_exact_thirty_two_are_all_in_digest(self):
        sha = self.write([self.item() for _ in range(32)])
        row = self.select(self.report()[0])
        self.assertEqual(row["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-01", range(2, 34)))
        self.assertEqual(row["vendor_month_evidence_omitted"], "0")

    def test_thirty_three_includes_first_omitted_line(self):
        sha = self.write([self.item() for _ in range(33)])
        row = self.select(self.report()[0])
        self.assertEqual(row["vendor_month_evidence_rows"].split(";")[-1], "33")
        self.assertEqual(row["vendor_month_evidence_omitted"], "1")
        self.assertEqual(row["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-01", range(2, 35)))

    def test_seventy_includes_all_hidden_line_references(self):
        sha = self.write([self.item() for _ in range(70)])
        row = self.select(self.report()[0])
        self.assertEqual(row["vendor_month_evidence_count"], "70")
        self.assertEqual(row["vendor_month_evidence_omitted"], "38")
        self.assertEqual(row["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-01", range(2, 72)))

    def test_many_categories_share_complete_group_digest(self):
        sha = self.write([self.item(category="C" + str(i % 7)) for i in range(80)])
        rows, _ = self.report()
        self.assertEqual(len(rows), 7)
        expected = reference_digest(sha, "ACME", "2026-01", range(2, 82))
        self.assertEqual({r["vendor_month_evidence_sha256"] for r in rows}, {expected})

    def test_category_local_source_rows_not_replaced(self):
        self.write([self.item(category="Parts"), self.item(category="Services")])
        rows, _ = self.report()
        self.assertEqual(self.select(rows)["source_rows"], "2")
        self.assertEqual(self.select(rows, category="Services")["source_rows"], "3")
        self.assertEqual(self.select(rows)["vendor_month_evidence_rows"], "2;3")

    def test_cross_category_credits_have_same_digest(self):
        self.write([self.item("150"), self.item("-140", category="Services")])
        rows, _ = self.report()
        a = self.select(rows)
        b = self.select(rows, category="Services")
        self.assertEqual(a["vendor_month_evidence_sha256"],
                         b["vendor_month_evidence_sha256"])
        self.assertEqual(a["vendor_month_offset_review"],
                         "review_vendor_month_mixed_sign_offset")

    def test_zeros_contribute_to_hash_even_without_gross_flows(self):
        sha = self.write([self.item("0"), self.item("-0", category="Services")])
        row = self.select(self.report()[0])
        self.assertEqual(row["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-01", [2, 3]))
        self.assertEqual(row["vendor_month_offset_review"], "")

    def test_multiline_csv_reference_uses_start_lines(self):
        sha = self.write([self.item(note="hello\nworld"), self.item(category="Services")])
        row = self.select(self.report()[0])
        self.assertEqual(row["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-01", [2, 4]))
        self.assertEqual(row["vendor_month_evidence_rows"], "2;4")

    def test_vendor_separation(self):
        sha = self.write([self.item(), self.item(vendor="OTHER")])
        rows, _ = self.report()
        self.assertEqual(self.select(rows)["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-01", [2]))
        self.assertEqual(self.select(rows, vendor="OTHER")["vendor_month_evidence_sha256"],
                         reference_digest(sha, "OTHER", "2026-01", [3]))

    def test_month_separation(self):
        sha = self.write([self.item(), self.item(month="02")])
        rows, _ = self.report()
        self.assertEqual(self.select(rows, month="2026-02")["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-02", [3]))

    def test_normalized_vendor_collision_still_uses_shared_group(self):
        sha = self.write([self.item(vendor="A-CME"), self.item(vendor="ACME")])
        row = self.select(self.report()[0])
        self.assertEqual(row["vendor_month_evidence_sha256"],
                         reference_digest(sha, "ACME", "2026-01", [2, 3]))
        self.assertIn("normalized_vendor_collision_review", row["flag"])

    def test_source_digest_changes_when_source_note_changes(self):
        self.write([self.item(note="a")])
        before = self.select(self.report()[0])["vendor_month_evidence_sha256"]
        self.write([self.item(note="b")])
        after = self.select(self.report()[0])["vendor_month_evidence_sha256"]
        self.assertNotEqual(before, after)

    def test_original_sha_is_not_replaced_by_group_digest(self):
        sha = self.write([self.item()])
        row = self.select(self.report()[0])
        self.assertEqual(row["source_sha256"], sha)
        self.assertNotEqual(row["vendor_month_evidence_sha256"], sha)

    def test_full_source_bytes_are_not_modified(self):
        self.write([self.item(note="private\nsource")])
        before = self.source_path.read_bytes()
        self.report()
        self.assertEqual(self.source_path.read_bytes(), before)

    def test_repeated_exports_are_deterministic(self):
        self.write([self.item("5"), self.item("-2", category="Services")])
        self.assertEqual(self.report(), self.report())

    def test_empty_source_has_new_schema_and_no_digest_rows(self):
        self.write([])
        rows, header = self.report()
        self.assertEqual(rows, [])
        self.assertEqual(header[header.index("vendor_month_evidence_rows"):
                                header.index("vendor_month_gross_charges")],
                         ("vendor_month_evidence_rows", "vendor_month_evidence_count",
                          "vendor_month_evidence_omitted", "vendor_month_evidence_sha256"))

    def test_digest_does_not_change_prior_terminal_export_columns(self):
        self.write([])
        _, header = self.report()
        self.assertEqual(header[-4:], ("source_rows", "source_vendor_labels",
                                       "vendor_label_variants", "source_sha256"))

    def test_direct_summarizer_ignores_record_iteration_order_for_hash(self):
        records = [{"row": str(i), "vendor": "ACME", "amount": "1.00",
                    "date": "2026-01-01", "category": "Parts"} for i in (10, 2, 7)]
        forward = self.direct(records)[0]["vendor_month_evidence_sha256"]
        reversed_order = self.direct(list(reversed(records)))[0]["vendor_month_evidence_sha256"]
        self.assertEqual(forward, reversed_order)
        self.assertEqual(forward, reference_digest("a" * 64, "ACME", "2026-01", [2, 7, 10]))

    def test_direct_summarizer_source_pin_changes_digest(self):
        rec = [{"row": "2", "vendor": "ACME", "amount": "1.00",
                "date": "2026-01-01", "category": "Parts"}]
        self.assertNotEqual(self.direct(rec, "a" * 64)[0]["vendor_month_evidence_sha256"],
                            self.direct(rec, "b" * 64)[0]["vendor_month_evidence_sha256"])

    def test_direct_summarizer_member_change_changes_digest(self):
        base = [{"row": "2", "vendor": "ACME", "amount": "1.00",
                 "date": "2026-01-01", "category": "Parts"}]
        extra = {"row": "500", "vendor": "ACME", "amount": "-1.00",
                 "date": "2026-01-01", "category": "Services"}
        a = self.direct(base)[0]["vendor_month_evidence_sha256"]
        b = self.direct(base + [extra])[0]["vendor_month_evidence_sha256"]
        self.assertNotEqual(a, b)
        self.assertEqual(b, reference_digest("a" * 64, "ACME", "2026-01", [2, 500]))

    def test_decimal_traps_do_not_change_digest_or_money(self):
        self.write([self.item("150"), self.item("-140", category="Services")])
        expected = self.select(self.report()[0])
        with localcontext() as context:
            context.prec = 2
            context.traps[__import__("decimal").Inexact] = True
            actual = self.select(self.report()[0])
        self.assertEqual(actual["vendor_month_evidence_sha256"],
                         expected["vendor_month_evidence_sha256"])
        self.assertEqual(actual["vendor_month_total"], "10.00")

    def test_invalid_private_amount_does_not_publish_digest(self):
        self.write([self.item("SENSITIVE-BAD-AMOUNT")])
        with self.assertRaises(ValueError) as result:
            engine.spend_map(self.source_path, self.root)
        self.assertNotIn("SENSITIVE-BAD-AMOUNT", str(result.exception))
        self.assertEqual(list(self.root.glob("spend-map-*.csv")), [])

    def test_source_pin_does_not_echo_source_labels(self):
        self.write([self.item(vendor="=SECRET")])
        row = self.select(self.report()[0], vendor="SECRET")
        self.assertRegex(row["vendor_month_evidence_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn("SECRET", row["vendor_month_evidence_sha256"])

    def test_five_hundred_records_include_all_without_long_preview(self):
        sha = self.write([self.item(category="C" + str(i % 9)) for i in range(500)])
        rows, _ = self.report()
        self.assertEqual(len(rows), 9)
        expected = reference_digest(sha, "ACME", "2026-01", range(2, 502))
        for row in rows:
            self.assertEqual(row["vendor_month_evidence_sha256"], expected)
            self.assertEqual(row["vendor_month_evidence_count"], "500")
            self.assertEqual(row["vendor_month_evidence_omitted"], "468")
            self.assertEqual(len(row["vendor_month_evidence_rows"].split(";")), 32)


if __name__ == "__main__":
    unittest.main()
