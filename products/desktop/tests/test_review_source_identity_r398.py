"""R398: source identity and printable evidence custody, synthetic/local only.

No customer files, payments, network, or automatic compliance decisions.
"""
from __future__ import annotations

from collections import UserDict
from decimal import Decimal
import unittest

from fvs_suite.review import raw_values, labels_for_report, normalized_collision, reconciliation_status


class ExactSourceIdentityR398(unittest.TestCase):
    def test_preserves_ascii_leading_space(self):
        self.assertEqual(raw_values([{"id": " A"}], "id"), (" A",))

    def test_preserves_ascii_trailing_space(self):
        self.assertEqual(raw_values([{"id": "A "}], "id"), ("A ",))

    def test_preserves_multiple_spaces(self):
        self.assertEqual(raw_values([{"id": "  A  "}], "id"), ("  A  ",))

    def test_keeps_spacing_variants_separately(self):
        found = raw_values([{"id": "A"}, {"id": " A"}, {"id": "A "}], "id")
        self.assertEqual(set(found), {"A", " A", "A "})

    def test_omitted_and_empty_are_not_phantom_labels(self):
        self.assertEqual(raw_values([{}, {"id": ""}], "id"), ())

    def test_whitespace_only_is_not_lost(self):
        self.assertEqual(raw_values([{"id": "  "}], "id"), ("  ",))

    def test_unicode_space_is_not_lost(self):
        self.assertEqual(raw_values([{"id": "\u00a0"}], "id"), ("\u00a0",))

    def test_ascii_case_only_is_still_same_identity(self):
        self.assertFalse(normalized_collision([{"id": "Acme"}, {"id": "ACME"}], "id"))

    def test_leading_space_requires_review(self):
        self.assertTrue(normalized_collision([{"id": "Acme"}, {"id": " Acme"}], "id"))

    def test_trailing_space_requires_review(self):
        self.assertTrue(normalized_collision([{"id": "Acme"}, {"id": "Acme "}], "id"))

    def test_boundary_unicode_space_requires_review(self):
        self.assertTrue(normalized_collision([{"id": "Acme"}, {"id": "Acme\u00a0"}], "id"))

    def test_zero_width_boundary_requires_review(self):
        self.assertTrue(normalized_collision([{"id": "Acme"}, {"id": "\u200bAcme"}], "id"))

    def test_same_whitespace_identity_can_match(self):
        self.assertFalse(normalized_collision([{"id": " A"}, {"id": " a"}], "id"))

    def test_equal_money_requires_review_for_trimmed_aliases(self):
        self.assertEqual(reconciliation_status(
            [{"id": " PO-1"}], [{"id": "PO-1"}], Decimal("10.00"), Decimal("10.00"),
            missing_left="missing_claim", missing_right="missing_ledger"), "normalized_id_review")

    def test_money_variance_and_identity_review_both_remain(self):
        self.assertEqual(reconciliation_status(
            [{"id": " PO-1"}], [{"id": "PO-1"}], Decimal("10.01"), Decimal("10.00"),
            missing_left="missing_claim", missing_right="missing_ledger"),
            "normalized_id_review;variance")

    def test_normal_identity_and_amount_unchanged(self):
        self.assertEqual(reconciliation_status(
            [{"id": "ABC"}], [{"id": "abc"}], Decimal("2.00"), Decimal("2.00"),
            missing_left="left", missing_right="right"), "matched")

    def test_visible_boundary_spaces(self):
        self.assertEqual(labels_for_report([{"id": " A "}], "id"), r"\u0020A\u0020")

    def test_all_space_label_unambiguous(self):
        self.assertEqual(labels_for_report([{"id": "   "}], "id"), r"\u0020\u0020\u0020")

    def test_interior_spaces_stay_readable(self):
        self.assertEqual(labels_for_report([{"id": "A B"}], "id"), "A B")

    def test_literal_escape_not_confused_with_actual_space(self):
        output = labels_for_report([{"id": " A"}, {"id": r"\u0020A"}], "id")
        self.assertIn(r"\u0020A", output)
        self.assertIn(r"\\u0020A", output)

    def test_semicolon_escaped(self):
        self.assertEqual(labels_for_report([{"id": "A;B"}], "id"), r"A\u003BB")

    def test_hidden_unicode_control_is_escaped(self):
        self.assertIn(r"\u0009", labels_for_report([{"id": "A\tB"}], "id"))

    def test_native_string_only(self):
        class Dangerous:
            def __str__(self):
                raise AssertionError("PRIVATE-CUSTOMER-NUMBER")
        for value in (None, False, 1, 3.25, b"ID", Dangerous()):
            with self.subTest(type=type(value).__name__):
                with self.assertRaisesRegex(ValueError, "label must be text") as caught:
                    raw_values([{"id": value}], "id")
                self.assertIsNone(caught.exception.__context__)
                self.assertIsNone(caught.exception.__cause__)

    def test_string_subclass_not_executed(self):
        class Hostile(str):
            def __hash__(self):
                raise AssertionError("PRIVATE-SOURCE")
            def casefold(self):
                raise AssertionError("PRIVATE-SOURCE")
        with self.assertRaisesRegex(ValueError, "label must be text"):
            raw_values([{"id": Hostile("A")}], "id")

    def test_invalid_row_does_not_call_str(self):
        class Dangerous:
            def __str__(self):
                raise AssertionError("PRIVATE-SOURCE")
        with self.assertRaisesRegex(ValueError, "must be mappings"):
            raw_values([Dangerous()], "id")

    def test_supports_native_mapping_subtypes(self):
        self.assertEqual(raw_values([UserDict({"id": "A"})], "id"), ("A",))

    def test_deterministic_across_source_permutations(self):
        a = [{"id": "B"}, {"id": " b"}, {"id": "A "}, {"id": "A"}]
        self.assertEqual(raw_values(a, "id"), raw_values(reversed(a), "id"))
        self.assertEqual(labels_for_report(a, "id"), labels_for_report(reversed(a), "id"))

    def test_never_mutates_original_rows(self):
        rows = [{"id": " A "}, {"id": "A"}]
        snapshot = [dict(row) for row in rows]
        labels_for_report(rows, "id")
        normalized_collision(rows, "id")
        self.assertEqual(rows, snapshot)

    def test_multi_field_program_collision(self):
        self.assertEqual(reconciliation_status(
            [{"id": "C1", "program": " GRANT"}],
            [{"id": "C1", "program": "GRANT"}],
            Decimal("0"), Decimal("0"),
            missing_left="missing_claim", missing_right="missing_ledger",
            fields=(("id", "normalized_id_review"), ("program", "normalized_program_review"))),
            "normalized_program_review")


if __name__ == "__main__":
    unittest.main()
