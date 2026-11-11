"""R355 full SpendMap source-engine regressions; needs the full trusted checkout.

These are not substitutes for real CSV import, native Windows acceptance, or
independent QD review. No personal data or network requests.
"""
from __future__ import annotations

from datetime import date
from decimal import Context, Decimal, Inexact, ROUND_DOWN, getcontext, setcontext
import unittest

from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.spend_input import validated_spend_rows

SOURCE_SHA = "5" * 64


def entry(row, amount="999999999999.99", month=1):
    return {"row": str(row), "vendor": "ACME", "amount": amount,
            "date": f"2026-{month:02d}-01", "category": "Parts"}


def report(rows, *, vendor=None, calendar=None, money=None, formatter=None):
    return summarize_spend(
        rows, source_sha256=SOURCE_SHA,
        normalize_vendor=vendor or (lambda s: s),
        parse_date=calendar or date.fromisoformat,
        parse_money=money or Decimal,
        format_money=formatter or (lambda x: format(x, ".2f")),
    )


def poison_precision(_):
    getcontext().prec = 2


def poison_swap(_):
    setcontext(Context(prec=2, rounding=ROUND_DOWN))


class SpendCallbackEngineIntegrationR355(unittest.TestCase):
    def assert_exact_large_total(self, rows):
        self.assertEqual(rows[0]["amount"], "1999999999999.98")
        self.assertEqual(rows[0]["gross_charges"], "1999999999999.98")
        self.assertEqual(rows[0]["vendor_month_total"], "1999999999999.98")
        self.assertEqual(rows[0]["source_rows"], "2;3")

    def test_mutating_vendor_normalizer_does_not_round_amount(self):
        def vendor(raw):
            poison_precision(raw)
            return raw
        self.assert_exact_large_total(report([entry(2), entry(3)], vendor=vendor))

    def test_swapping_vendor_normalizer_does_not_round_amount(self):
        def vendor(raw):
            poison_swap(raw)
            return raw
        self.assert_exact_large_total(report([entry(2), entry(3)], vendor=vendor))

    def test_mutating_date_parser_does_not_round_amount(self):
        def calendar(raw):
            poison_precision(raw)
            return date.fromisoformat(raw)
        self.assert_exact_large_total(report([entry(2), entry(3)], calendar=calendar))

    def test_swapping_date_parser_does_not_round_amount(self):
        def calendar(raw):
            poison_swap(raw)
            return date.fromisoformat(raw)
        self.assert_exact_large_total(report([entry(2), entry(3)], calendar=calendar))

    def test_mutating_money_parser_does_not_round_amount(self):
        def money(raw):
            poison_precision(raw)
            return Decimal(raw)
        self.assert_exact_large_total(report([entry(2), entry(3)], money=money))

    def test_swapping_money_parser_does_not_round_amount(self):
        def money(raw):
            poison_swap(raw)
            return Decimal(raw)
        self.assert_exact_large_total(report([entry(2), entry(3)], money=money))

    def test_formatter_receives_original_64_precision_every_call(self):
        before = []
        def formatter(value):
            before.append((getcontext().prec, getcontext().rounding))
            poison_precision(value)
            return format(value, ".2f")
        output = report([entry(2), entry(3)], formatter=formatter)
        self.assert_exact_large_total(output)
        self.assertGreater(len(before), 3)
        self.assertEqual({precision for precision, _ in before}, {64})

    def test_formatter_setcontext_cannot_contaminate_following_calls(self):
        before = []
        def formatter(value):
            before.append(getcontext().prec)
            poison_swap(value)
            return format(value, ".2f")
        self.assert_exact_large_total(report([entry(2), entry(3)], formatter=formatter))
        self.assertEqual(set(before), {64})

    def test_trapping_parser_cannot_break_later_arithmetic(self):
        def money(raw):
            getcontext().traps[Inexact] = True
            getcontext().prec = 2
            return Decimal(raw)
        self.assert_exact_large_total(report([entry(2), entry(3)], money=money))

    def test_direct_iterator_preserves_ambient_context_after_parser(self):
        from decimal import localcontext
        with localcontext() as context:
            context.prec = 47
            parsed = list(validated_spend_rows(
                [entry(2)], normalize_vendor=lambda x: x,
                parse_date=date.fromisoformat,
                parse_money=lambda x: (poison_swap(x), Decimal(x))[1]))
            self.assertEqual(getcontext().prec, 47)
            self.assertEqual(parsed[0][-1], Decimal("999999999999.99"))

    def test_spike_review_threshold_unchanged_under_parser_attack(self):
        rows = [entry(2 + i, value, i + 1) for i, value in enumerate(
            ("10.00", "10.01", "10.00", "10.01", "20.01"))]
        def vendor(raw):
            poison_swap(raw)
            return raw
        actual = report(rows, vendor=vendor)
        expected = report(rows)
        self.assertEqual(actual, expected)
        self.assertEqual(actual[-1]["baseline_median"], "10.005")
        self.assertEqual(actual[-1]["flag"], "review_spike")

    def test_read_only_source_rows_and_provenance_stay_same(self):
        records = [entry(2), entry(3)]
        snapshot = [dict(x) for x in records]
        def money(raw):
            poison_precision(raw)
            return Decimal(raw)
        actual = report(records, money=money)
        self.assertEqual(records, snapshot)
        self.assertEqual(actual, report(records))
        self.assertEqual(actual[0]["source_sha256"], SOURCE_SHA)


if __name__ == "__main__":
    unittest.main()
