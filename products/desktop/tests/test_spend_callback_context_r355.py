"""R355: SpendMap callback Decimal context custody; synthetic values only."""
from __future__ import annotations

from decimal import (Context, Decimal, Inexact, ROUND_DOWN, ROUND_HALF_EVEN,
                     Rounded, getcontext, localcontext, setcontext)
import unittest

from fvs_suite.spend_callback_context_r355 import invoke_spend_callback


class SpendCallbackContextR355(unittest.TestCase):
    def test_return_identity(self):
        marker = Decimal("999999999999.99")
        self.assertIs(invoke_spend_callback(lambda x: x, marker), marker)

    def test_parser_receives_exact_original_text(self):
        original = "01.2300"
        self.assertEqual(invoke_spend_callback(Decimal, original), Decimal("1.2300"))

    def test_normalizer_receives_exact_original_text(self):
        original = " A-CME\u00a0"
        self.assertEqual(invoke_spend_callback(lambda x: x, original), original)

    def test_callback_called_once(self):
        calls = []
        self.assertEqual(invoke_spend_callback(lambda x: calls.append(x) or x, "v"), "v")
        self.assertEqual(calls, ["v"])

    def test_mutating_precision_does_not_leak(self):
        with localcontext() as outer:
            outer.prec = 64
            invoke_spend_callback(lambda _: setattr(getcontext(), "prec", 2), "x")
            self.assertEqual(outer.prec, 64)
            self.assertEqual((Decimal("999999999999.99") + Decimal("999999999999.99")),
                             Decimal("1999999999999.98"))

    def test_mutating_rounding_does_not_leak(self):
        with localcontext() as outer:
            outer.rounding = ROUND_HALF_EVEN
            invoke_spend_callback(lambda _: setattr(getcontext(), "rounding", ROUND_DOWN), 1)
            self.assertEqual(getcontext().rounding, ROUND_HALF_EVEN)

    def test_mutating_traps_does_not_leak(self):
        with localcontext() as outer:
            outer.traps[Inexact] = False
            invoke_spend_callback(lambda _: getcontext().traps.__setitem__(Inexact, True), 1)
            self.assertFalse(getcontext().traps[Inexact])

    def test_mutating_flags_does_not_leak(self):
        with localcontext() as outer:
            outer.flags[Inexact] = False
            invoke_spend_callback(lambda _: getcontext().flags.__setitem__(Inexact, True), 1)
            self.assertFalse(getcontext().flags[Inexact])

    def test_setcontext_swap_does_not_leak(self):
        with localcontext() as outer:
            outer.prec = 64
            outer.rounding = ROUND_HALF_EVEN
            invoke_spend_callback(lambda _: setcontext(Context(prec=2, rounding=ROUND_DOWN)), "x")
            self.assertEqual(getcontext().prec, 64)
            self.assertEqual(getcontext().rounding, ROUND_HALF_EVEN)

    def test_setcontext_swap_on_exception_restores(self):
        def bad(_):
            setcontext(Context(prec=2, rounding=ROUND_DOWN))
            raise ValueError("private invoice source")
        with localcontext() as outer:
            outer.prec = 64
            with self.assertRaises(ValueError):
                invoke_spend_callback(bad, "sensitive")
            self.assertEqual(getcontext().prec, 64)
            self.assertEqual(getcontext().rounding, outer.rounding)

    def test_regular_exception_restores(self):
        def bad(_):
            getcontext().prec = 2
            raise RuntimeError("synthetic")
        with localcontext() as outer:
            outer.prec = 64
            with self.assertRaises(RuntimeError):
                invoke_spend_callback(bad, "synthetic")
            self.assertEqual(getcontext().prec, 64)

    def test_exception_is_not_silenced_or_sanitized_at_helper(self):
        def bad(_):
            raise TypeError("synthetic-private")
        with self.assertRaisesRegex(TypeError, "synthetic-private"):
            invoke_spend_callback(bad, "source")

    def test_malicious_low_context_does_not_round_exact_output(self):
        def parser(raw):
            getcontext().prec = 2
            return Decimal(raw)
        with localcontext(Context(prec=64)):
            first = invoke_spend_callback(parser, "999999999999.99")
            second = invoke_spend_callback(parser, "999999999999.99")
            self.assertEqual(first + second, Decimal("1999999999999.98"))

    def test_formatter_callback_sees_fresh_context_each_call(self):
        before = []
        def formatter(amount):
            before.append(getcontext().prec)
            getcontext().prec = 2
            return format(amount, "f")
        with localcontext(Context(prec=64)):
            self.assertEqual(invoke_spend_callback(formatter, Decimal("1.23456789")), "1.23456789")
            self.assertEqual(invoke_spend_callback(formatter, Decimal("2.34567891")), "2.34567891")
            self.assertEqual(getcontext().prec, 64)
        self.assertEqual(before, [64, 64])

    def test_context_status_flags_from_callback_do_not_leak(self):
        with localcontext(Context(prec=64)) as outer:
            outer.clear_flags()
            def status(_):
                _ = Decimal(1) / Decimal(3)
                self.assertTrue(getcontext().flags[Inexact])
                self.assertTrue(getcontext().flags[Rounded])
            invoke_spend_callback(status, 0)
            self.assertFalse(getcontext().flags[Inexact])
            self.assertFalse(getcontext().flags[Rounded])

    def test_caller_custom_precision_is_preserved(self):
        with localcontext() as outer:
            outer.prec = 23
            invoke_spend_callback(lambda _: setcontext(Context(prec=2)), "x")
            self.assertEqual(getcontext().prec, 23)

    def test_nested_callback_contexts_do_not_leak(self):
        with localcontext(Context(prec=64)):
            def inner(value):
                getcontext().prec = 3
                return value
            def outer(value):
                getcontext().prec = 4
                return invoke_spend_callback(inner, value)
            self.assertEqual(invoke_spend_callback(outer, Decimal("7.0009")), Decimal("7.0009"))
            self.assertEqual(getcontext().prec, 64)


if __name__ == "__main__":
    unittest.main()
