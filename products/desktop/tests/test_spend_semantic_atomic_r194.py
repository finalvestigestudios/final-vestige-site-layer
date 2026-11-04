"""R194: direct SpendMap iterators do not leak partial rows on late semantic errors.

Synthetic only. Parser callbacks are trusted and may have side effects; this
contract guarantees no yielded evidence until every converted row is valid,
not that a callback's externally visible side effects can be rolled back.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, Inexact, Rounded, localcontext
import unittest

from fvs_suite.spend_input import validated_spend_rows

SECRET = "PRIVATE CLIENT: 123-45-6789\n=FORMULA"


def record(row="2", vendor="ACME", date_text="2026-01-02", amount="12.34", category="Parts"):
    return {"row": row, "vendor": vendor, "date": date_text,
            "amount": amount, "category": category}


def convert(rows, *, normalize=lambda s: s.upper(), day=date.fromisoformat, money=Decimal):
    return validated_spend_rows(rows, normalize_vendor=normalize,
                                parse_date=day, parse_money=money)


class SpendAtomicSemanticPreflightR194(unittest.TestCase):
    def fail_first_pull(self, rows, fragment, **converters):
        iterator = convert(rows, **converters)
        with self.assertRaises(ValueError) as caught:
            next(iterator)  # A previous valid row must NEVER leak out.
        self.assertIn(fragment, str(caught.exception))
        self.assertNotIn(SECRET, str(caught.exception))
        with self.assertRaises(StopIteration):
            next(iterator)

    def test_late_unparseable_money(self):
        self.fail_first_pull([record(), record("3", amount=SECRET)], "Invalid spend amount")

    def test_late_unparseable_date(self):
        self.fail_first_pull([record(), record("3", date_text=SECRET)], "Invalid spend date")

    def test_late_unparseable_vendor(self):
        def normalize(s):
            if s == SECRET:
                raise RuntimeError(SECRET)
            return s
        self.fail_first_pull([record(), record("3", vendor=SECRET)], "Invalid vendor", normalize=normalize)

    def test_late_invalid_vendor_character(self):
        self.fail_first_pull([record(), record("3", vendor="A-CME")], "Invalid normalized vendor key")

    def test_late_invalid_vendor_lowercase_result(self):
        self.fail_first_pull([record(), record("3", vendor="acme")], "Invalid normalized vendor key", normalize=lambda s: s)

    def test_late_blank_vendor(self):
        self.fail_first_pull([record(), record("3", vendor="")], "Blank vendor at row 3")

    def test_late_vendor_callback_nontext(self):
        self.fail_first_pull([record(), record("3", vendor="LAST")], "Invalid normalized vendor key", normalize=lambda s: 42 if s == "LAST" else s)

    def test_late_date_type_datetime(self):
        self.fail_first_pull([record(), record("3", date_text="2026-01-03")], "Spend date must be a calendar date",
                             day=lambda s: datetime(2026, 1, 2) if s == "2026-01-03" else date.fromisoformat(s))

    def test_late_date_type_string(self):
        self.fail_first_pull([record(), record("3", date_text="2026-01-03")],
                             "Spend date must be a calendar date", day=lambda s: s if s.endswith("03") else date.fromisoformat(s))

    def test_late_money_float(self):
        self.fail_first_pull([record(), record("3", amount="99.99")],
                             "finite exact Decimal", money=lambda s: 99.99 if s == "99.99" else Decimal(s))

    def test_late_money_boolean(self):
        self.fail_first_pull([record(), record("3", amount="99.99")],
                             "finite exact Decimal", money=lambda s: True if s == "99.99" else Decimal(s))

    def test_late_money_subclass(self):
        class DecimalChild(Decimal):
            pass
        self.fail_first_pull([record(), record("3", amount="99.99")],
                             "finite exact Decimal", money=lambda s: DecimalChild(s) if s == "99.99" else Decimal(s))

    def test_late_money_nan(self):
        self.fail_first_pull([record(), record("3", amount="NaN")], "finite exact Decimal")

    def test_late_money_infinity(self):
        self.fail_first_pull([record(), record("3", amount="Infinity")], "finite exact Decimal")

    def test_late_money_outside_cap(self):
        self.fail_first_pull([record(), record("3", amount="1000000000000.01")], "permitted range")

    def test_late_money_overlong_coefficient(self):
        self.fail_first_pull([record(), record("3", amount="0." + "0" * 81)], "unsupported numeric representation")

    def test_late_money_extreme_exponent(self):
        self.fail_first_pull([record(), record("3", amount="0E-100")], "unsupported numeric representation")

    def test_late_money_subcent(self):
        self.fail_first_pull([record(), record("3", amount="1.001")], "cent precision")

    def test_late_money_private_callback_error(self):
        def parse(s):
            if s == SECRET:
                raise RuntimeError(SECRET)
            return Decimal(s)
        self.fail_first_pull([record(), record("3", amount=SECRET)], "Invalid spend amount", money=parse)

    def test_late_third_row_invalid_no_partial_next(self):
        self.fail_first_pull([record(), record("3"), record("4", amount="1.001")], "cent precision")

    def test_late_semantic_failure_callback_order_no_repeat(self):
        hits = []
        def v(s):
            hits.append(("vendor", s))
            return s
        def d(s):
            hits.append(("date", s))
            return date.fromisoformat(s)
        def m(s):
            hits.append(("money", s))
            return Decimal(s)
        self.fail_first_pull([record(), record("3", amount="1.001")], "cent precision", normalize=v, day=d, money=m)
        self.assertEqual(hits, [("vendor", "ACME"), ("date", "2026-01-02"), ("money", "12.34"),
                                ("vendor", "ACME"), ("date", "2026-01-02"), ("money", "1.001")])

    def test_early_structural_failure_still_prevents_callbacks(self):
        hits = []
        iterator = convert([record(), record("2")], normalize=lambda s: hits.append(s) or s)
        with self.assertRaisesRegex(ValueError, "Duplicate spend physical"):
            next(iterator)
        self.assertEqual(hits, [])

    def test_valid_source_order_and_all_callbacks_before_first_output(self):
        hits = []
        def normal(s):
            hits.append(s)
            return s
        values = [record("9", vendor="ALPHA"), record("2", vendor="BETA"), record("20", vendor="GAMMA")]
        iterator = convert(values, normalize=normal)
        self.assertEqual(hits, [])
        first = next(iterator)
        self.assertEqual(first[0]["row"], "9")
        self.assertEqual(hits, ["ALPHA", "BETA", "GAMMA"])
        rest = list(iterator)
        self.assertEqual([x[0]["row"] for x in [first] + rest], ["9", "2", "20"])

    def test_valid_three_rows_keep_exact_values_and_categories(self):
        values = list(convert([record(), record("3", amount="-0.02", category=""),
                               record("4", amount="0.00", category="Travel")]))
        self.assertEqual([x[-1] for x in values], [Decimal("12.34"), Decimal("-0.02"), Decimal("0.00")])
        self.assertEqual([x[3] for x in values], ["Parts", "Uncategorized", "Travel"])
        self.assertEqual([x[2] for x in values], ["2026-01"] * 3)

    def test_trapping_decimal_context_remains_isolated(self):
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            values = list(convert([record(), record("3", amount="10.00")]))
            self.assertEqual(ctx.prec, 3)
        self.assertEqual(values[0][-1], Decimal("12.34"))
        self.assertEqual(values[1][-1], Decimal("10.00"))

    def test_caller_mutation_after_first_yield_cannot_change_later(self):
        items = [record(), record("3", vendor="BETA", amount="20.00")]
        iterator = convert(items)
        first = next(iterator)
        items[1]["vendor"] = SECRET
        items[1]["amount"] = SECRET
        second = next(iterator)
        self.assertEqual(first[-1], Decimal("12.34"))
        self.assertEqual((second[0]["vendor"], second[-1]), ("BETA", Decimal("20.00")))
        self.assertIsNot(second[0], items[1])

    def test_empty_no_callbacks(self):
        hits = []
        self.assertEqual(list(convert([], normalize=lambda s: hits.append(s))), [])
        self.assertEqual(hits, [])

    def test_original_collection_not_mutated(self):
        items = [record(), record("3")]
        originals = [dict(x) for x in items]
        list(convert(items))
        self.assertEqual(items, originals)


if __name__ == "__main__":
    unittest.main()
