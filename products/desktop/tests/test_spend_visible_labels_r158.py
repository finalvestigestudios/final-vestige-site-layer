"""R158 synthetic SpendMap source-vendor display custody tests.

All data are invented and kept in TemporaryDirectory. The tests use the real
CSV importer, report writer and independently checking verifier.
"""
from __future__ import annotations

import contextlib
import csv
import io
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine
from fvs_suite.spend_evidence_verify import main, verify_membership
from fvs_suite.spend_label_verify import expected_vendor_labels


class SpendLabelR158(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r158-synthetic-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.source = self.folder / "source.csv"
        self.report = self.folder / "report.csv"

    @staticmethod
    def row(vendor="ACME", month=1, category="Parts", amount="10.00", note=""):
        return vendor, amount, f"2026-{month:02d}-01", category, note

    def write(self, rows):
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        self.report = Path(engine.spend_map(self.source, self.folder)[0])
        return verify_membership(self.source, self.report)

    def report_rows(self):
        with self.report.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            return list(reader.fieldnames), list(reader)

    def mutate(self, field, value, index=0, remove_header=False):
        fields, rows = self.report_rows()
        if remove_header:
            fields.remove(field)
        else:
            rows[index][field] = value
        with self.report.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def hold_on_mutation(self, field, value, index=0):
        self.mutate(field, value, index=index)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_plain_label_verified(self):
        receipt = self.write([self.row()])
        self.assertEqual((receipt.groups_verified, receipt.buckets_verified), (1, 1))
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "ACME")

    def test_identical_labels_deduplicated(self):
        self.write([self.row(), self.row()])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "ACME")

    def test_ascii_case_variants_remain_visible(self):
        self.write([self.row("ACME"), self.row("acme"), self.row("AcMe")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "ACME; AcMe; acme")

    def test_punctuation_collision_order(self):
        self.write([self.row("ACME"), self.row("A-CME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "A-CME; ACME")

    def test_labels_per_category_not_whole_month(self):
        self.write([self.row("ACME", category="Parts"),
                    self.row("A-CME", category="Service")])
        values = {r["category"]: r["source_vendor_labels"] for r in self.report_rows()[1]}
        self.assertEqual(values, {"Parts": "ACME", "Service": "A-CME"})

    def test_labels_per_month_not_all_vendor_history(self):
        self.write([self.row("ACME", month=1), self.row("A-CME", month=2)])
        values = {r["month"]: r["source_vendor_labels"] for r in self.report_rows()[1]}
        self.assertEqual(values, {"2026-01": "ACME", "2026-02": "A-CME"})

    def test_trimmed_outer_spaces_and_duplicates(self):
        self.write([self.row("  ACME  "), self.row("ACME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "ACME")

    def test_literal_semicolon_is_not_list_separator(self):
        self.write([self.row("AC;ME"), self.row("ACME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"],
                         r"AC\u003BME; ACME")

    def test_source_backslash_remains_distinguishable(self):
        self.write([self.row(r"A\CME"), self.row("ACME")])
        text = self.report_rows()[1][0]["source_vendor_labels"]
        self.assertIn(r"A\\CME", text)
        self.assertEqual(text.count("; "), 1)

    def test_actual_zero_width_vs_literal_escape_differ(self):
        self.write([self.row("A\u200BCME"), self.row(r"A\u200BCME")])
        labels = {row["source_vendor_labels"] for row in self.report_rows()[1]}
        self.assertIn(r"A\u200BCME", labels)
        self.assertIn(r"A\\u200BCME", labels)

    def test_directional_override_is_visible(self):
        self.write([self.row("A\u202ECME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"],
                         r"A\u202ECME")

    def test_nonbreaking_space_is_visible(self):
        self.write([self.row("A\u00A0CME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"],
                         r"A\u00A0CME")

    def test_variation_selector_is_visible(self):
        self.write([self.row("A\uFE0FCME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"],
                         r"A\uFE0FCME")

    def test_hangul_filler_is_visible(self):
        self.write([self.row("A\u3164CME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"],
                         r"A\u3164CME")

    def test_supplementary_variation_selector_is_visible(self):
        self.write([self.row("A\U000E0100CME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"],
                         r"A\U000E0100CME")

    def test_unicode_casefold_only_orders_does_not_merge(self):
        self.write([self.row("ASSCME"), self.row("AßCME")])
        labels = self.report_rows()[1][0]["source_vendor_labels"]
        self.assertIn("ASSCME", labels)
        self.assertIn("AßCME", labels)

    def test_formula_equals_prefix_is_neutralized(self):
        self.write([self.row("=ACME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "'=ACME")

    def test_formula_plus_prefix_is_neutralized(self):
        self.write([self.row("+ACME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "'+ACME")

    def test_formula_at_prefix_is_neutralized(self):
        self.write([self.row("@ACME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "'@ACME")

    def test_formula_minus_text_is_neutralized(self):
        self.write([self.row("-ACME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "'-ACME")

    def test_leading_combining_mark_is_neutralized(self):
        self.write([self.row("\u0301ACME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "'\u0301ACME")

    def test_quoted_multiline_source_preserves_snapshot(self):
        self.write([self.row("A-CME", note="private\nmultiline"), self.row("ACME")])
        self.assertEqual(self.report_rows()[1][0]["source_vendor_labels"], "A-CME; ACME")

    def test_tampered_label_suppression_holds(self):
        self.write([self.row("A-CME"), self.row("ACME")])
        self.hold_on_mutation("source_vendor_labels", "ACME")

    def test_tampered_label_reorder_holds(self):
        self.write([self.row("A-CME"), self.row("ACME")])
        self.hold_on_mutation("source_vendor_labels", "ACME; A-CME")

    def test_semicolon_injection_holds(self):
        self.write([self.row("AC;ME"), self.row("ACME")])
        self.hold_on_mutation("source_vendor_labels", "AC;ME; ACME")

    def test_unicode_escape_tamper_holds(self):
        self.write([self.row("A\u200BCME")])
        self.hold_on_mutation("source_vendor_labels", r"A\\u200BCME")

    def test_formula_quote_removed_holds(self):
        self.write([self.row("=ACME")])
        self.hold_on_mutation("source_vendor_labels", "=ACME")

    def test_wrong_category_label_holds(self):
        self.write([self.row("A-CME", category="Parts"),
                    self.row("ACME", category="Service")])
        self.hold_on_mutation("source_vendor_labels", "ACME", index=0)

    def test_missing_label_column_holds(self):
        self.write([self.row()])
        self.mutate("source_vendor_labels", "", remove_header=True)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_original_bytes_unchanged_after_verification(self):
        self.write([self.row("A\u202ECME", note="secret-synthetic")])
        originals = self.source.read_bytes(), self.report.read_bytes()
        verify_membership(self.source, self.report)
        self.assertEqual((self.source.read_bytes(), self.report.read_bytes()), originals)

    def test_private_cli_failure_does_not_expose_label(self):
        self.write([self.row("SECRETCLIENTACME")])
        self.mutate("source_vendor_labels", "REDACTED")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--source", str(self.source), "--report", str(self.report)])
        self.assertEqual(code, 1)
        self.assertNotIn("SECRETCLIENTACME", out.getvalue() + err.getvalue())
        self.assertIn("HOLD", err.getvalue())

    def test_helper_rejects_unsorted_lookalike_output(self):
        data = [("ACME", "2026-01", "Parts", "ACME"),
                ("ACME", "2026-01", "Parts", "A-CME")]
        expected = expected_vendor_labels(data)
        self.assertEqual(expected[("ACME", "2026-01", "Parts")], "A-CME; ACME")

    def test_no_network_or_report_generator_imports(self):
        import inspect
        from fvs_suite import spend_label_verify
        code = inspect.getsource(spend_label_verify)
        self.assertNotIn("import engine", code)
        self.assertNotIn("from .review", code)
        self.assertNotIn("from .audit_display", code)
        self.assertNotIn("requests.", code)


if __name__ == "__main__":
    unittest.main()
