"""R399 SpendMap source-label and independent verifier parity regressions.

Synthetic records only. The report label is not identity or payment approval.
"""
from __future__ import annotations

from decimal import Decimal
import unittest

from fvs_suite.spend_vendor_evidence_r358 import spend_vendor_evidence
from fvs_suite.spend_label_verify import expected_vendor_labels
from fvs_suite.spend_review_verify import compute_expected_review_fields


def vendors(*labels):
    return [{"vendor": label} for label in labels]


class SpendVendorReportEvidenceR399(unittest.TestCase):
    def test_leading_space_is_review_collision(self):
        self.assertEqual(
            spend_vendor_evidence(vendors(" ACME", "ACME")),
            (True, 2, r"\u0020ACME; ACME"))

    def test_trailing_space_is_review_collision(self):
        self.assertEqual(
            spend_vendor_evidence(vendors("ACME ", "ACME")),
            (True, 2, r"ACME; ACME\u0020"))

    def test_multiple_boundary_spaces_visible(self):
        self.assertEqual(
            spend_vendor_evidence(vendors("  ACME  ")),
            (False, 1, r"\u0020\u0020ACME\u0020\u0020"))

    def test_boundary_tabs_not_silently_removed(self):
        result = spend_vendor_evidence(vendors("\tACME", "ACME"))
        self.assertEqual(result, (True, 2, r"\u0009ACME; ACME"))

    def test_unicode_space_preserves_raw_identity(self):
        self.assertEqual(
            spend_vendor_evidence(vendors("\u00a0ACME", "ACME")),
            (True, 2, r"ACME; \u00A0ACME"))

    def test_literal_backslash_escape_is_not_real_space(self):
        result = spend_vendor_evidence(vendors(" ACME", r"\u0020ACME"))
        self.assertTrue(result[0])
        self.assertIn(r"\u0020ACME", result[2])
        self.assertIn(r"\\u0020ACME", result[2])

    def test_separator_cannot_forge_labels(self):
        self.assertEqual(
            spend_vendor_evidence(vendors("A;B", "AB")),
            (True, 2, r"A\u003BB; AB"))

    def test_ascii_case_remains_equivalent(self):
        self.assertEqual(
            spend_vendor_evidence(vendors(" ACME", " acme")),
            (False, 1, r"\u0020ACME; \u0020acme"))

    def test_deterministic_permutation_and_immutability(self):
        source = vendors(" ACME", "ACME", "\u00a0ACME")
        snapshot = [dict(row) for row in source]
        self.assertEqual(spend_vendor_evidence(source), spend_vendor_evidence(reversed(source)))
        self.assertEqual(source, snapshot)

    def test_rejects_nonnative_vendor_without_conversion(self):
        class Nasty:
            def __str__(self):
                raise AssertionError("CONFIDENTIAL")
        with self.assertRaisesRegex(ValueError, "native source text") as caught:
            spend_vendor_evidence(vendors(Nasty()))
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)


class IndependentVendorReplayR399(unittest.TestCase):
    def test_expected_labels_keep_ascii_boundaries(self):
        result = expected_vendor_labels([
            ("ACME", "2026-01", "Parts", " ACME"),
            ("ACME", "2026-01", "Parts", "ACME")])
        self.assertEqual(result[("ACME", "2026-01", "Parts")],
                         r"\u0020ACME; ACME")

    def test_expected_labels_scope_to_category(self):
        result = expected_vendor_labels([
            ("ACME", "2026-01", "Parts", " ACME"),
            ("ACME", "2026-01", "Services", "ACME")])
        self.assertEqual(result, {
            ("ACME", "2026-01", "Parts"): r"\u0020ACME",
            ("ACME", "2026-01", "Services"): "ACME"})

    def test_expected_labels_scope_to_month(self):
        result = expected_vendor_labels([
            ("ACME", "2026-01", "Parts", " ACME"),
            ("ACME", "2026-02", "Parts", "ACME")])
        self.assertEqual(result, {
            ("ACME", "2026-01", "Parts"): r"\u0020ACME",
            ("ACME", "2026-02", "Parts"): "ACME"})

    def test_spreadsheet_prefix_retained_as_review_text(self):
        result = expected_vendor_labels([
            ("ACME", "2026-01", "Parts", "=unsafe")])
        self.assertEqual(result[("ACME", "2026-01", "Parts")], "'=unsafe")

    def test_verifier_escapes_backslash_and_semicolon(self):
        result = expected_vendor_labels([
            ("AB", "2026-01", "Parts", r"\u0020AB"),
            ("AB", "2026-01", "Parts", "A;B")])
        cell = result[("AB", "2026-01", "Parts")]
        self.assertIn(r"\\u0020AB", cell)
        self.assertIn(r"A\u003BB", cell)

    def test_history_flags_vendor_wide_collision_across_categories(self):
        observations = [
            ("ACME", "2026-01", "Parts", Decimal("10.00"), " ACME"),
            ("ACME", "2026-01", "Services", Decimal("-5.00"), "ACME")]
        fields = compute_expected_review_fields(observations)
        self.assertEqual(len(fields), 2)
        for item in fields.values():
            self.assertEqual(item["flag"], "normalized_vendor_collision_review")
            self.assertEqual(item["vendor_label_variants"], "2")

    def test_history_flags_vendor_wide_collision_across_months(self):
        observations = [
            ("ACME", "2026-01", "Parts", Decimal("10.00"), " ACME"),
            ("ACME", "2026-02", "Parts", Decimal("10.00"), "ACME")]
        fields = compute_expected_review_fields(observations)
        self.assertTrue(all("normalized_vendor_collision_review" in row["flag"]
                            for row in fields.values()))
        self.assertEqual(fields[("ACME", "2026-02", "Parts")]["history_months"], "1")

    def test_history_does_not_conflate_case_only_with_collision(self):
        observations = [
            ("ACME", "2026-01", "Parts", Decimal("10.00"), " ACME"),
            ("ACME", "2026-02", "Parts", Decimal("10.00"), " acme")]
        fields = compute_expected_review_fields(observations)
        self.assertTrue(all(row["flag"] == "" for row in fields.values()))
        self.assertTrue(all(row["vendor_label_variants"] == "1"
                            for row in fields.values()))


if __name__ == "__main__":
    unittest.main()
