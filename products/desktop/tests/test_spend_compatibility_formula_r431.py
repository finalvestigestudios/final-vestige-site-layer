"""R431: independently verify SpendMap vendor evidence against real CSV formula grammar.

Synthetic strings only; no user files, accounts, network, Windows binaries or approvals.
Tests target the R430 source verifier; publisher behavior is checked against the
unchanged shared CSV formula-prefix predicate, not imported into the verifier.
"""
from __future__ import annotations

import inspect
import unittest
from fvs_suite.csv_formula_guard import has_unescaped_formula_prefix
from fvs_suite.spend_label_verify import expected_vendor_labels


def source_label(raw, *, month="2026-01", category="Parts"):
    return expected_vendor_labels([("ACME", month, category, raw)])["ACME", month, category]


class SpendCompatibilityFormulaR431(unittest.TestCase):
    def test_fullwidth_plus_is_quoted_as_producer_requires(self):
        self.assertEqual(source_label("＋ACME"), "'＋ACME")

    def test_fullwidth_equals_is_quoted(self):
        self.assertEqual(source_label("＝ACME"), "'＝ACME")

    def test_fullwidth_at_is_quoted(self):
        self.assertEqual(source_label("＠ACME"), "'＠ACME")

    def test_small_plus_form_is_quoted(self):
        self.assertEqual(source_label("﹢ACME"), "'﹢ACME")

    def test_small_equals_form_is_quoted(self):
        self.assertEqual(source_label("﹦ACME"), "'﹦ACME")

    def test_small_minus_form_is_quoted_even_before_digits(self):
        self.assertEqual(source_label("﹣12.30"), "'﹣12.30")

    def test_superscript_plus_quoted_but_unicode_minus_not_ascii_formula(self):
        self.assertEqual(source_label("⁺AMOUNT"), "'⁺AMOUNT")
        self.assertEqual(source_label("⁻12"), "⁻12")

    def test_standard_formula_operators_remain_quoted(self):
        for value in ("=ACME", "+ACME", "@ACME", "-ACME"):
            with self.subTest(value=value):
                self.assertEqual(source_label(value), "'" + value)

    def test_native_negative_decimal_remains_unquoted(self):
        for value in ("-123", "-123.45", "-0.00"):
            with self.subTest(value=value):
                self.assertEqual(source_label(value), value)

    def test_noncanonical_ascii_minus_is_quoted(self):
        for value in ("-ABC", "-1e5", "-1,000", "-"):
            with self.subTest(value=value):
                self.assertEqual(source_label(value), "'" + value)

    def test_already_explicitly_escaped_leading_quote_is_not_doubled(self):
        self.assertEqual(source_label("'＋ACME"), "'＋ACME")

    def test_operator_not_in_first_meaningful_position_is_data(self):
        self.assertEqual(source_label("A＋ACME"), "A＋ACME")
        self.assertEqual(source_label("A﹣5"), "A﹣5")

    def test_visible_nbsp_is_not_an_invisible_actual_formula_prefix(self):
        self.assertEqual(source_label("\u00a0＋ACME"), r"\u00A0＋ACME")

    def test_source_ascii_boundary_space_is_visible(self):
        self.assertEqual(source_label(" ＋ACME"), r"\u0020＋ACME")
        self.assertEqual(source_label("＋ACME "), "'" + r"＋ACME\u0020")

    def test_literal_backslash_cannot_be_interpreted_as_escape(self):
        self.assertEqual(source_label(r"\uFF0BACME"), r"\\uFF0BACME")

    def test_identical_vendor_wide_compatibility_evidence_repeats(self):
        values = expected_vendor_labels([
            ("ACME", "2026-01", "Parts", "＋ACME"),
            ("ACME", "2026-02", "Travel", "＋ACME"),
        ])
        self.assertEqual(set(values.values()), {"'＋ACME"})
        self.assertEqual(len(values), 2)

    def test_inherited_33_label_digest_is_preserved(self):
        values = expected_vendor_labels([
            ("ACME", "2026-01", "Parts", "＋ACME" + str(n).zfill(3))
            for n in range(33)
        ])
        value = next(iter(values.values()))
        self.assertTrue(value.startswith("'＋ACME000"))
        self.assertIn("PREVIEW_ONLY:shown=32:omitted=1:sha256=", value)
        self.assertLessEqual(len(value), 8192)

    def test_formula_predicate_matches_first_meaningful_compatibility_prefix(self):
        # Exact GitHub-matched production CSV prefix guard, independent of the verifier.
        for raw in ("＋ACME", "＝ACME", "＠ACME", "﹢ACME", "﹦ACME", "﹣12.30", "⁺ACME"):
            with self.subTest(raw=raw):
                self.assertTrue(has_unescaped_formula_prefix(raw))
                self.assertTrue(source_label(raw).startswith("'"))

    def test_publisher_predicate_keeps_native_negative_decimal(self):
        for raw in ("-1", "-12.30"):
            self.assertFalse(has_unescaped_formula_prefix(raw))
            self.assertEqual(source_label(raw), raw)

    def test_no_publisher_guard_import_inside_independent_verifier(self):
        import fvs_suite.spend_label_verify as mod
        body = inspect.getsource(mod)
        self.assertNotIn("from .csv_formula_guard", body)
        self.assertNotIn("from .engine", body)
        self.assertNotIn("from .spend_vendor_evidence", body)


if __name__ == "__main__":
    unittest.main()
