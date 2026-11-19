"""R537: no private ledger is read before both override configurations pass."""
from __future__ import annotations

from decimal import Decimal
import unittest
from unittest.mock import patch

from fvs_suite.ledger_mapping_preflight_r537 import preflight_ledger_overrides


class LedgerMappingPreflightPureTests(unittest.TestCase):
    def test_accepts_absent_overrides(self):
        self.assertIsNone(preflight_ledger_overrides())

    def test_accepts_each_boundary_size(self):
        for valid in ("a", "_", "a" * 128, " z ", "Ref ID", "Ref__ID"):
            with self.subTest(valid=valid[:15]):
                self.assertIsNone(preflight_ledger_overrides(left_match_column=valid))

    def test_accepts_distinct_per_side_headers(self):
        self.assertIsNone(preflight_ledger_overrides(
            left_match_column="invoice_no", left_amount_column="total",
            right_match_column="reference", right_amount_column="paid"))

    def test_allows_same_header_across_distinct_sources(self):
        self.assertIsNone(preflight_ledger_overrides(
            left_match_column="Ref ID", right_match_column="ref_id",
            left_amount_column="net", right_amount_column="net"))

    def test_rejects_non_native_types_on_each_side(self):
        class TextSubclass(str):
            def lower(self):
                raise AssertionError("subclass coercion")
        for field in ("left_match_column", "right_match_column",
                      "left_amount_column", "right_amount_column"):
            for bad in (True, 7, 1.5, Decimal("7"), b"ref", TextSubclass("ref"), []):
                with self.subTest(field=field, kind=type(bad).__name__):
                    with self.assertRaisesRegex(ValueError, "Invalid explicit ledger"):
                        preflight_ledger_overrides(**{field: bad})

    def test_rejects_bad_characters_before_normalizing(self):
        for bad in ("", "   ", "9id", "é", "=cmd", "ref-id", "ref\tid", "a\x00b", "a\nb"):
            with self.subTest(kind=repr(bad)):
                with self.assertRaisesRegex(ValueError, "Invalid explicit ledger"):
                    preflight_ledger_overrides(right_amount_column=bad)

    def test_rejects_overlong_normalized_header(self):
        for bad in ("x" * 129, " " + "x" * 129 + " "):
            with self.assertRaisesRegex(ValueError, "Invalid explicit ledger"):
                preflight_ledger_overrides(left_amount_column=bad)

    def test_rejects_left_same_column_after_normalizing(self):
        with self.assertRaisesRegex(ValueError, "distinct CSV columns"):
            preflight_ledger_overrides(left_match_column=" Ref ID ",
                                       left_amount_column="ref_id")

    def test_rejects_right_same_column_after_normalizing(self):
        with self.assertRaisesRegex(ValueError, "distinct CSV columns"):
            preflight_ledger_overrides(right_match_column="TOTAL ",
                                       right_amount_column="total")

    def test_rejects_alias_without_changing_other_side_policy(self):
        with self.assertRaisesRegex(ValueError, "distinct CSV columns"):
            preflight_ledger_overrides(left_match_column="valid",
                                       left_amount_column="balance",
                                       right_match_column="invoice no",
                                       right_amount_column="invoice_no")

    def test_errors_never_echo_private_headers(self):
        private = "sensitive-client-PO=999"
        try:
            preflight_ledger_overrides(right_match_column=private)
        except ValueError as exc:
            self.assertNotIn(private, str(exc))
        else:
            self.fail("unsafe header accepted")

    def test_no_stringification_of_adversarial_object(self):
        class Trap:
            def __str__(self):
                raise AssertionError("called user __str__")
            def __repr__(self):
                raise AssertionError("called user __repr__")
        with self.assertRaises(ValueError):
            preflight_ledger_overrides(right_match_column=Trap())

    def test_no_mutation_of_caller_values(self):
        source = " Ref ID "
        preflight_ledger_overrides(left_match_column=source)
        self.assertEqual(source, " Ref ID ")


class LedgerDiffPreflightIntegrationTests(unittest.TestCase):
    def test_invalid_right_match_does_not_read_left_or_right(self):
        from fvs_suite import engine
        with patch.object(engine, "table", side_effect=AssertionError("private CSV read")) as table:
            with self.assertRaisesRegex(ValueError, "Invalid explicit ledger match"):
                engine.ledger_diff("left-private.csv", "right-private.csv", "out",
                                   right_match_column=True)
            table.assert_not_called()

    def test_invalid_right_amount_does_not_read_left_or_right(self):
        from fvs_suite import engine
        with patch.object(engine, "table", side_effect=AssertionError("private CSV read")) as table:
            with self.assertRaisesRegex(ValueError, "Invalid explicit ledger amount"):
                engine.ledger_diff("left-private.csv", "right-private.csv", "out",
                                   right_amount_column="=HYPERLINK(1)")
            table.assert_not_called()

    def test_same_right_override_does_not_read_left(self):
        from fvs_suite import engine
        with patch.object(engine, "table", side_effect=AssertionError("private CSV read")) as table:
            with self.assertRaisesRegex(ValueError, "distinct CSV columns"):
                engine.ledger_diff("left-private.csv", "right-private.csv", "out",
                                   right_match_column="Ref ID", right_amount_column="ref_id")
            table.assert_not_called()

    def test_valid_override_reaches_both_sources_and_report(self):
        from fvs_suite import engine
        def fake_table(_source, _required, **_kw):
            return [], "0" * 64, {"id": "reference", "amount": "total"}
        with patch.object(engine, "table", side_effect=fake_table) as table:
            with patch.object(engine, "save", return_value="fake-report.csv") as save:
                self.assertEqual(engine.ledger_diff(
                    "left.csv", "right.csv", "output",
                    left_match_column="reference", right_amount_column="total"),
                    ["fake-report.csv"])
                self.assertEqual(table.call_count, 2)
                save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
