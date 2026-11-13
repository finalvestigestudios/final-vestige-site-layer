"""R397 — private financial-callback exception graphs (synthetic only).

Both premium ProcureGuard price/quantity hooks and free SpendMap parser,
normalizer, and formatter hooks must translate failures *outside* their
original handlers. This prevents private bytes from surviving in the
exposed ValueError.__context__, even when normal traceback text is safe.
"""
from __future__ import annotations

from datetime import date
from decimal import Context, Decimal, ROUND_DOWN, getcontext, localcontext, setcontext
import unittest

from fvs_suite.procurement_numeric_result_r345 import checked_quantity, checked_unit_price
from fvs_suite.spend_input import validated_spend_rows
from fvs_suite.spend_analysis import summarize_spend


_PRIVATE = "R397_PRIVATE_CUSTOMER_LEDGER_4711"
_SHA = "a" * 64


class PrivateCallbackError(RuntimeError):
    def __init__(self):
        super().__init__(_PRIVATE)
        self.customer_record = {"raw_csv_bytes": _PRIVATE.encode("ascii")}


def reject_private(test, callback, expected):
    try:
        callback()
    except ValueError as error:
        test.assertIsNone(error.__cause__, "Hidden original exception retained as cause")
        test.assertIsNone(error.__context__, "Hidden original exception retained as context")
        test.assertNotIn(_PRIVATE, str(error))
        test.assertIn(expected, str(error))
    else:
        test.fail("Expected sanitized ValueError")


def fail_private(_):
    raise PrivateCallbackError()


def fail_unicode(_):
    raw = (_PRIVATE + " - financial source evidence").encode("ascii")
    raise UnicodeDecodeError("utf-8", raw, 0, 1, "synthetic")


def fail_json(_):
    from json import JSONDecodeError
    raise JSONDecodeError("synthetic", '{"source":"' + _PRIVATE + '"', 1)


def row(**changes):
    result = {
        "row": "2", "vendor": "ACME", "date": "2026-01-02",
        "amount": "12.34", "category": "operations",
    }
    result.update(changes)
    return result


def spend_rows(records=None, *, normalizer=None, date_parser=None, money_parser=None):
    return list(validated_spend_rows(
        [row()] if records is None else records,
        normalize_vendor=(lambda value: value) if normalizer is None else normalizer,
        parse_date=date.fromisoformat if date_parser is None else date_parser,
        parse_money=Decimal if money_parser is None else money_parser,
    ))


def spend_report(*, formatter):
    return summarize_spend(
        [row()], normalize_vendor=lambda value: value,
        parse_date=date.fromisoformat, parse_money=Decimal,
        format_money=formatter, source_sha256=_SHA,
    )


class ProcurementCallbackPrivateBoundaryR397(unittest.TestCase):
    def test_quantity_runtime_exception_has_no_chain(self):
        reject_private(self, lambda: checked_quantity("3.500", fail_private), "quantity")

    def test_price_unicode_exception_has_no_chain(self):
        reject_private(self, lambda: checked_unit_price("3.500", fail_unicode), "unit price")

    def test_price_json_exception_has_no_chain(self):
        reject_private(self, lambda: checked_unit_price("3.500", fail_json), "unit price")

    def test_quantity_noncallable_has_no_chain(self):
        reject_private(self, lambda: checked_quantity("1", None), "quantity")

    def test_price_noncallable_has_no_chain(self):
        reject_private(self, lambda: checked_unit_price("1", None), "unit price")

    def test_parser_context_swap_and_failure_do_not_escape(self):
        def poison(_):
            setcontext(Context(prec=2, rounding=ROUND_DOWN))
            raise PrivateCallbackError()
        with localcontext(Context(prec=64)) as outer:
            reject_private(self, lambda: checked_unit_price("1.01", poison), "unit price")
            self.assertEqual(getcontext().prec, 64)
            self.assertEqual(getcontext().rounding, outer.rounding)

    def test_recovery_preserves_subcent_precision(self):
        reject_private(self, lambda: checked_unit_price("1", fail_private), "unit price")
        self.assertEqual(checked_unit_price("0.00000001", Decimal), Decimal("0.00000001"))
        self.assertEqual(checked_quantity("3.1250", Decimal), Decimal("3.1250"))

    def test_source_rejection_skips_parser(self):
        calls = []
        def parser(raw):
            calls.append(raw)
            return Decimal(1)
        reject_private(self, lambda: checked_quantity("-0", parser), "quantity")
        self.assertEqual(calls, [])


class SpendMapCallbackPrivateBoundaryR397(unittest.TestCase):
    def test_original_bad_money_does_not_retain_validator_error(self):
        reject_private(self, lambda: spend_rows([row(amount="not-money")]),
                       "original spend amount")

    def test_original_bad_date_does_not_retain_validator_error(self):
        reject_private(self, lambda: spend_rows([row(date="2026-13-99")]),
                       "original spend date")

    def test_vendor_normalizer_exception_has_no_chain(self):
        reject_private(self, lambda: spend_rows(normalizer=fail_private), "vendor")

    def test_date_parser_unicode_exception_has_no_chain(self):
        reject_private(self, lambda: spend_rows(date_parser=fail_unicode), "spend date")

    def test_money_parser_json_exception_has_no_chain(self):
        reject_private(self, lambda: spend_rows(money_parser=fail_json), "spend amount")

    def test_noncallable_vendor_has_no_chain(self):
        reject_private(self, lambda: spend_rows(normalizer=False), "vendor")

    def test_noncallable_date_has_no_chain(self):
        reject_private(self, lambda: spend_rows(date_parser=False), "spend date")

    def test_noncallable_money_has_no_chain(self):
        reject_private(self, lambda: spend_rows(money_parser=False), "spend amount")

    def test_formatter_exception_has_no_chain(self):
        reject_private(self, lambda: spend_report(formatter=fail_private),
                       "monetary display")

    def test_formatter_unicode_exception_has_no_chain(self):
        reject_private(self, lambda: spend_report(formatter=fail_unicode),
                       "monetary display")

    def test_noncallable_formatter_has_no_chain(self):
        reject_private(self, lambda: spend_report(formatter=False),
                       "monetary display")

    def test_spend_date_and_money_success_are_unchanged(self):
        prepared = spend_rows()
        self.assertEqual(len(prepared), 1)
        self.assertEqual(prepared[0][1:4], ("ACME", "2026-01", "operations"))
        self.assertEqual(prepared[0][4], Decimal("12.34"))

    def test_spend_report_success_is_exact_and_review_only(self):
        report = spend_report(formatter=lambda amount: format(amount, ".2f"))
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["amount"], "12.34")
        self.assertEqual(report[0]["source_sha256"], _SHA)
        self.assertEqual(report[0]["source_rows"], "2")

    def test_context_swap_on_parser_failure_is_isolated(self):
        def poison(_):
            setcontext(Context(prec=2, rounding=ROUND_DOWN))
            raise PrivateCallbackError()
        with localcontext(Context(prec=64)) as outer:
            reject_private(self, lambda: spend_rows(money_parser=poison), "spend amount")
            self.assertEqual(getcontext().prec, 64)
            self.assertEqual(getcontext().rounding, outer.rounding)


if __name__ == "__main__":
    unittest.main()
