"""R85: fixed-point SpendMap aggregates/medians stay exact under any low Decimal context."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, Rounded, Inexact, localcontext
import re
import unittest

from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.spend_median import RunningDecimalMedian
from fvs_suite.spend_input import validated_spend_rows

SHA = "e" * 64
CENT = Decimal("0.01")


def spend(rows, *, parse_money=None):
    def cents(raw):
        return Decimal(raw).quantize(CENT, rounding=ROUND_HALF_UP)
    return summarize_spend(
        rows, normalize_vendor=lambda s: re.sub("[^A-Z0-9]+", "", s.upper()),
        parse_date=date.fromisoformat, parse_money=parse_money or cents,
        format_money=lambda d: format(d.quantize(CENT, rounding=ROUND_HALF_UP), ".2f"),
        source_sha256=SHA,
    )


def row(n, month, amount, *, vendor="ACME", category="Parts"):
    return {"row": str(n), "vendor": vendor, "date": f"2026-{month:02d}-01",
            "amount": amount, "category": category}


class SpendContextR85(unittest.TestCase):
    def test_two_large_values_have_exact_half_cent_median_under_precision_six(self):
        history = RunningDecimalMedian()
        with localcontext() as ctx:
            ctx.prec = 6
            history.add(Decimal("123456789012.01"))
            history.add(Decimal("123456789012.02"))
            self.assertEqual(history.median(), Decimal("123456789012.015"))
            self.assertEqual(ctx.prec, 6)

    def test_one_large_value_preserves_all_fractional_digits(self):
        history = RunningDecimalMedian()
        with localcontext() as ctx:
            ctx.prec = 3
            history.add(Decimal("999999999999.99"))
            self.assertEqual(history.median(), Decimal("999999999999.99"))

    def test_heap_rebalance_retains_cents_and_order_under_low_precision(self):
        history = RunningDecimalMedian()
        values = ("100000000000.01", "100000000000.03", "100000000000.02",
                  "100000000000.04", "100000000000.00")
        with localcontext() as ctx:
            ctx.prec = 4
            for value in values:
                history.add(Decimal(value))
            self.assertEqual(history.median(), Decimal("100000000000.02"))
            self.assertEqual(len(history), 5)

    def test_negative_large_and_positive_values_keep_exact_sign(self):
        median = RunningDecimalMedian()
        with localcontext() as ctx:
            ctx.prec = 3
            for value in ("-123456789012.02", "-123456789012.01", "0.00"):
                median.add(Decimal(value))
            self.assertEqual(median.median(), Decimal("-123456789012.01"))

    def test_midpoint_of_wide_precision_values_is_exact(self):
        median = RunningDecimalMedian()
        a = Decimal("9" * 70 + ".01")
        b = Decimal("9" * 70 + ".02")
        with localcontext() as ctx:
            ctx.prec = 5
            median.add(a)
            median.add(b)
            self.assertEqual(median.median(), Decimal("9" * 70 + ".015"))

    def test_spend_aggregation_no_low_precision_rounding(self):
        data = [row(2, 1, "999999999999.99"), row(3, 1, "999999999999.99")]
        with localcontext() as ctx:
            ctx.prec = 6
            report = spend(data)
            self.assertEqual(ctx.prec, 6)
        self.assertEqual(report[0]["amount"], "1999999999999.98")
        self.assertEqual(report[0]["vendor_month_total"], "1999999999999.98")
        self.assertEqual(report[0]["source_rows"], "2;3")

    def test_spend_month_history_precision_does_not_change_spike(self):
        rows = [row(2, 1, "10.00"), row(3, 2, "10.01"),
                row(4, 3, "10.00"), row(5, 4, "10.01"),
                row(6, 5, "20.01")]
        with localcontext() as ctx:
            ctx.prec = 3
            report = spend(rows)
            self.assertEqual(ctx.prec, 3)
        self.assertEqual(report[-1]["baseline_median"], "10.005")
        self.assertEqual(report[-1]["flag"], "review_spike")

    def test_spike_exact_boundary_below_2x_is_not_flagged(self):
        rows = [row(2, 1, "10.00"), row(3, 2, "10.01"),
                row(4, 3, "10.00"), row(5, 4, "10.01"),
                row(6, 5, "20.00")]
        with localcontext() as ctx:
            ctx.prec = 3
            report = spend(rows)
        self.assertEqual(report[-1]["baseline_median"], "10.005")
        self.assertEqual(report[-1]["flag"], "")

    def test_context_rounding_mode_is_not_changed(self):
        with localcontext() as ctx:
            ctx.prec = 5
            ctx.rounding = ROUND_DOWN
            spend([row(2, 1, "1000000000000.00")])
            self.assertEqual(ctx.prec, 5)
            self.assertEqual(ctx.rounding, ROUND_DOWN)

    def test_custom_direct_parser_cannot_bypass_money_upper_bound(self):
        with self.assertRaisesRegex(ValueError, "permitted range"):
            spend([row(2, 1, "secret")], parse_money=lambda _: Decimal("1000000000000.01"))

    def test_custom_direct_parser_cannot_bypass_cent_precision(self):
        with self.assertRaisesRegex(ValueError, "cent precision"):
            spend([row(2, 1, "secret")], parse_money=lambda _: Decimal("0.001"))

    def test_direct_parser_allows_decimal_with_trailing_zeroes(self):
        report = spend([row(2, 1, "unused")], parse_money=lambda _: Decimal("1.0000"))
        self.assertEqual(report[0]["amount"], "1.00")

    def test_direct_spend_validator_accepts_large_cents_under_low_context(self):
        with localcontext() as ctx:
            ctx.prec = 4
            parsed = list(validated_spend_rows(
                [row(2, 1, "999999999999.99")],
                normalize_vendor=lambda s: s,
                parse_date=date.fromisoformat,
                parse_money=Decimal,
            ))
            self.assertEqual(ctx.prec, 4)
        self.assertEqual(parsed[0][-1], Decimal("999999999999.99"))

    def test_private_cells_not_in_callback_validation_errors(self):
        secret = "bank-999-000=SECRET\x1b[31m"
        for amount in (Decimal("1000000000000.01"), Decimal("0.001")):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError) as caught:
                    spend([row(2, 1, secret)], parse_money=lambda _, m=amount: m)
                self.assertNotIn(secret, str(caught.exception))
                self.assertIn("physical row 2", str(caught.exception))

    def test_ambient_decimal_traps_do_not_reject_exact_median(self):
        median = RunningDecimalMedian()
        with localcontext() as ctx:
            ctx.prec = 5
            ctx.traps[Rounded] = True
            ctx.traps[Inexact] = True
            median.add(Decimal("123456789012.01"))
            median.add(Decimal("123456789012.02"))
            self.assertEqual(median.median(), Decimal("123456789012.015"))

    def test_nonstandard_caller_exponent_limit_does_not_overflow(self):
        data = [row(2, 1, "999999999999.99"), row(3, 1, "999999999999.99")]
        with localcontext() as ctx:
            ctx.prec = 6
            ctx.Emax = 6
            report = spend(data)
            self.assertEqual(ctx.Emax, 6)
            self.assertEqual(ctx.prec, 6)
        self.assertEqual(report[0]["amount"], "1999999999999.98")

    def test_original_input_rows_not_mutated(self):
        data = [row(2, 1, "0.10"), row(3, 1, "0.20")]
        snapshot = [dict(item) for item in data]
        with localcontext() as ctx:
            ctx.prec = 4
            first = spend(data)
            second = spend(data)
        self.assertEqual(first, second)
        self.assertEqual(data, snapshot)


if __name__ == "__main__":
    unittest.main()
