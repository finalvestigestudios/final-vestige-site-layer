"""R356 full SpendMap + importer integration regressions; require real repository.

These tests use synthetic in-memory source rows and real engine.money. Nothing
is released or uploaded; findings and mismatches always require human review.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
import unittest

from fvs_suite.engine import money
from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.spend_input import validated_spend_rows
from fvs_suite.spend_source_custody_r356 import canonical_spend_source_cents

SOURCE_SHA = "6" * 64


def source(row, amount="100.00", vendor="ACME"):
    return {"row": str(row), "date": "2026-01-01", "vendor": vendor,
            "amount": amount, "category": "Supplies"}


def validated(rows, parse_money=money):
    return list(validated_spend_rows(
        rows, normalize_vendor=lambda s: s, parse_date=date.fromisoformat,
        parse_money=parse_money))


def report(rows, parse_money=money):
    return summarize_spend(
        rows, normalize_vendor=lambda s: s, parse_date=date.fromisoformat,
        parse_money=parse_money, format_money=lambda d: format(d, ".2f"),
        source_sha256=SOURCE_SHA)


class SpendSourceEngineR356(unittest.TestCase):
    def test_parity_with_native_importer(self):
        for raw in ("0", "-0.00", "$1.25", "($1,230.005)", "$-5.50", "+$1",
                    ".125", "12.", "1,000,000,000,000", "  1.25  "):
            with self.subTest(raw=raw):
                expected = money(raw)
                actual = canonical_spend_source_cents(raw)
                self.assertEqual(actual, expected)
                self.assertEqual(actual.is_signed(), expected.is_signed())

    def test_amount_callback_cannot_inflate_source(self):
        with self.assertRaisesRegex(ValueError, "Spend parser changed original amount"):
            validated([source(2, "$100.00")], parse_money=lambda _: Decimal("1000.00"))

    def test_amount_callback_cannot_reduce_source(self):
        with self.assertRaisesRegex(ValueError, "Spend parser changed original amount"):
            validated([source(2, "100.00")], parse_money=lambda _: Decimal("0.00"))

    def test_negative_zero_source_sign_must_remain(self):
        with self.assertRaisesRegex(ValueError, "Spend parser changed original amount"):
            validated([source(2, "-0.00")], parse_money=lambda _: Decimal("0.00"))

    def test_positive_zero_source_sign_must_remain(self):
        with self.assertRaisesRegex(ValueError, "Spend parser changed original amount"):
            validated([source(2, "0.00")], parse_money=lambda _: Decimal("-0.00"))

    def test_real_money_accepts_accounting_credits(self):
        values = validated([source(2, "($1,234.50)")])
        self.assertEqual(values[0][-1], Decimal("-1234.50"))
        self.assertEqual(report([source(2, "($1,234.50)")])[0]["gross_credits"], "1234.50")

    def test_native_half_up_cents_matches_source(self):
        rows = validated([source(2, "1.005")])
        self.assertEqual(rows[0][-1], Decimal("1.01"))

    def test_nonstandard_lexical_source_is_rejected(self):
        for raw in ("1e3", "1,23", "500.00CR", "NaN", "1_000"):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "Invalid original spend amount"):
                validated([source(2, raw)], parse_money=lambda _: Decimal("100.00"))

    def test_late_invalid_row_prevents_all_callbacks(self):
        called = []
        def parser(raw):
            called.append(raw)
            return Decimal("100.00")
        with self.assertRaisesRegex(ValueError, "physical row 3"):
            validated([source(2), source(3, "PRIVATE-INPUT")], parse_money=parser)
        self.assertEqual(called, [])

    def test_amount_mismatch_at_late_row_fails_closed(self):
        rows = [source(2, "100.00"), source(3, "200.00")]
        with self.assertRaisesRegex(ValueError, "physical row 3"):
            report(rows, parse_money=lambda _: Decimal("100.00"))

    def test_error_message_does_not_echo_private_source(self):
        with self.assertRaises(ValueError) as caught:
            validated([source(2, "PRIVATE-SOURCE-500.00")])
        self.assertNotIn("PRIVATE-SOURCE", str(caught.exception))

    def test_different_decimal_scale_same_value_accepted(self):
        parsed = validated([source(2, "1.00")], parse_money=lambda _: Decimal("1.0"))
        self.assertEqual(parsed[0][-1], Decimal("1.0"))

    def test_source_rows_remain_unchanged(self):
        originals = [source(2, "$100.00"), source(3, "(50.00)")]
        copy = [dict(x) for x in originals]
        outcome = report(originals)
        self.assertEqual(originals, copy)
        self.assertEqual(outcome[0]["source_sha256"], SOURCE_SHA)
        self.assertEqual(outcome[0]["amount"], "50.00")

    def test_original_money_and_native_parser_same_results(self):
        originals = [source(2, "2.005"), source(3, "3.005")]
        result = report(originals, parse_money=money)
        self.assertEqual(result[0]["amount"], "5.02")
        self.assertEqual(result[0]["source_rows"], "2;3")


if __name__ == "__main__":
    unittest.main()
