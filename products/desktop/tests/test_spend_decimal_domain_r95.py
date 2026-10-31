"""R95 SpendMap: exact bounded direct Decimal representation and private errors.

No uploads, external files, or operational financial data. These exercise the
real reusable import-boundary helper, not a reconstructed money parser.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, Inexact, Rounded, ROUND_DOWN, localcontext
import unittest

from fvs_suite.spend_input import MAX_SPEND_ROWS, validated_spend_rows

PRIVATE = "account: 8675309; secret-token\x1b[31m"


def row(n=2):
    return {"row": str(n), "vendor": "ACME", "date": "2026-01-01",
            "amount": PRIVATE, "category": "Parts"}


def parse(values):
    if not isinstance(values, list):
        values = [values]
    values_iter = iter(values)
    return list(validated_spend_rows(
        [row(index + 2) for index in range(len(values))],
        normalize_vendor=lambda _: "ACME",
        parse_date=date.fromisoformat,
        parse_money=lambda _: next(values_iter),
    ))


class SpendDecimalDomainR95(unittest.TestCase):
    def assert_private_failure(self, amount, expected):
        with self.assertRaises(ValueError) as caught:
            parse([amount])
        message = str(caught.exception)
        self.assertIn(expected, message)
        self.assertIn("physical row 2", message)
        self.assertNotIn("8675309", message)
        self.assertNotIn("secret-token", message)
        self.assertNotIn("\x1b", message)

    def test_reject_extreme_negative_zero_exponent(self):
        self.assert_private_failure(Decimal("0E-999999999"), "numeric representation")

    def test_reject_negative_signed_zero_exponent(self):
        self.assert_private_failure(Decimal("-0E-999999999"), "numeric representation")

    def test_reject_extreme_positive_zero_exponent(self):
        self.assert_private_failure(Decimal("0E+999999999"), "numeric representation")

    def test_reject_nonzero_very_large_negative_exponent_before_quantization(self):
        self.assert_private_failure(Decimal("1E-999999999"), "numeric representation")

    def test_reject_81_digit_fractional_coefficient(self):
        self.assert_private_failure(Decimal("1" + "2" * 80 + "E-80"), "numeric representation")

    def test_reject_long_trailing_zero_coefficient_even_if_exact_value_is_one(self):
        self.assert_private_failure(Decimal("1" + "0" * 80 + "E-80"), "numeric representation")

    def test_accept_80_digit_coefficient_at_lower_exponent_boundary(self):
        number = Decimal("12" + "0" * 78 + "E-80")
        self.assertEqual(parse([number])[0][-1], Decimal("0.12"))

    def test_reject_81st_negative_exponent_even_for_zero(self):
        self.assert_private_failure(Decimal("0E-81"), "numeric representation")

    def test_accept_zero_at_negative_exponent_boundary(self):
        self.assertEqual(parse([Decimal("0E-80")])[0][-1], Decimal("0E-80"))

    def test_accept_zero_at_positive_exponent_boundary(self):
        self.assertEqual(parse([Decimal("0E+12")])[0][-1], Decimal("0E+12"))

    def test_reject_zero_at_positive_exponent_outside_boundary(self):
        self.assert_private_failure(Decimal("0E+13"), "numeric representation")

    def test_reject_nonzero_third_significant_fractional_place(self):
        self.assert_private_failure(Decimal("1.2300001"), "cent precision")

    def test_accept_fractional_trailing_zeroes_at_eight_places(self):
        self.assertEqual(parse([Decimal("1.23000000")])[0][-1], Decimal("1.23000000"))

    def test_accept_eight_place_integer_lexical_scientific_value(self):
        self.assertEqual(parse([Decimal("1.23E+2")])[0][-1], Decimal("123"))

    def test_preserve_negative_cents_and_signed_zero(self):
        originals = [Decimal("-123.45"), Decimal("-0.00")]
        self.assertEqual([p[-1] for p in parse(originals)], originals)

    def test_exact_boundary_one_trillion_still_allowed(self):
        self.assertEqual(parse([Decimal("1000000000000.00")])[0][-1],
                         Decimal("1000000000000.00"))

    def test_out_of_range_valid_tuple_still_fails(self):
        self.assert_private_failure(Decimal("1000000000000.01"), "permitted range")

    def test_caller_context_precision_rounding_traps_and_exponents_unchanged(self):
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.Emax = 6
            ctx.Emin = -6
            ctx.rounding = ROUND_DOWN
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            before = (ctx.prec, ctx.Emax, ctx.Emin, ctx.rounding, ctx.traps.copy())
            self.assertEqual(parse([Decimal("999999999999.99")])[0][-1],
                             Decimal("999999999999.99"))
            self.assert_private_failure(Decimal("0E-100000000"), "numeric representation")
            self.assertEqual((ctx.prec, ctx.Emax, ctx.Emin, ctx.rounding, ctx.traps.copy()), before)

    def test_sources_remain_unchanged_and_parser_is_called_once(self):
        records = [row(2), row(4)]
        snapshot = [dict(v) for v in records]
        invocations = []
        def amount(_):
            invocations.append(1)
            return Decimal("1.00")
        result = list(validated_spend_rows(records,
            normalize_vendor=lambda _: "ACME", parse_date=date.fromisoformat,
            parse_money=amount))
        self.assertEqual(len(invocations), 2)
        self.assertEqual([r[0]["row"] for r in result], ["2", "4"])
        self.assertEqual(records, snapshot)

    def test_late_failure_preserves_private_value_and_validation_order(self):
        records = [row(2), row(3), row(4)]
        values = iter([Decimal("1.00"), Decimal("2.00"), Decimal("0E-2000")])
        with self.assertRaises(ValueError) as caught:
            list(validated_spend_rows(records, normalize_vendor=lambda _: "ACME",
                parse_date=date.fromisoformat, parse_money=lambda _: next(values)))
        self.assertIn("physical row 4", str(caught.exception))
        self.assertNotIn(PRIVATE, str(caught.exception))

    def test_200k_record_bound_and_complete_canonical_row_evidence(self):
        # Stress the public generator itself without constructing a CSV file.
        total = 0
        source = [row(index + 2) for index in range(MAX_SPEND_ROWS)]
        for record, vendor, month, category, amount in validated_spend_rows(
            source, normalize_vendor=lambda _: "ACME", parse_date=date.fromisoformat,
            parse_money=lambda _: Decimal("0.01")):
            total += 1
            self.assertEqual((vendor, month, category, amount),
                             ("ACME", "2026-01", "Parts", Decimal("0.01")))
        self.assertEqual(total, MAX_SPEND_ROWS)


if __name__ == "__main__":
    unittest.main()
