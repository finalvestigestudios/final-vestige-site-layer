"""R348: injected procurement parsers cannot poison the caller's Decimal context.

Synthetic amounts only. Test as ordinary and optimized Python, with warnings
as errors. An injected parser is not a sandbox for arbitrary Python code.
"""
from decimal import (Clamped, Context, Decimal, DivisionByZero, Inexact,
                     InvalidOperation, ROUND_DOWN, ROUND_HALF_UP, Rounded,
                     getcontext, localcontext, setcontext)
import unittest

from fvs_suite.procurement_numeric_result_r345 import checked_quantity, checked_unit_price


class CallbackDecimalContextCustodyR348(unittest.TestCase):
    def _case(self, fn, source, expected, poison, *, error=False):
        # Test the whole context (traps, flags, rounding, Emax/Emin/precision),
        # not just precision. Seed a nondefault outer context on purpose.
        with localcontext(Context(prec=64)) as outer:
            outer.rounding = ROUND_HALF_UP
            outer.Emax = 777
            outer.Emin = -777
            outer.traps[DivisionByZero] = True
            outer.flags[Clamped] = True
            prior = outer.copy()
            called = []
            def parser(value):
                called.append(value)
                return poison(value)
            if error:
                with self.assertRaises(ValueError) as raised:
                    fn(source, parser)
                self.assertIsNone(raised.exception.__cause__)
                self.assertNotIn("PRIVATE_FINANCE_PATH", str(raised.exception))
            else:
                self.assertEqual(fn(source, parser), Decimal(expected))
            self.assertEqual(called, [source])
            self.assertEqual(getcontext().prec, prior.prec)
            self.assertEqual(getcontext().flags, prior.flags)
            self.assertEqual(getcontext().traps, prior.traps)
            self.assertEqual(getcontext().Emax, 777)
            self.assertEqual(getcontext().Emin, -777)
            self.assertEqual(getcontext().rounding, ROUND_HALF_UP)
            # This exact multiplication must not round after parser execution.
            self.assertEqual(Decimal("3") * Decimal("0.12345678"), Decimal("0.37037034"))

    @staticmethod
    def _low_precision(value):
        getcontext().prec = 4
        return Decimal(value)

    @staticmethod
    def _alter_rounding(value):
        getcontext().rounding = ROUND_DOWN
        getcontext().prec = 3
        return Decimal(value)

    @staticmethod
    def _alter_exponents(value):
        getcontext().Emax = 9
        getcontext().Emin = -9
        return Decimal(value)

    @staticmethod
    def _alter_traps(value):
        getcontext().traps[DivisionByZero] = False
        getcontext().traps[InvalidOperation] = False
        return Decimal(value)

    @staticmethod
    def _alter_flags(value):
        context = getcontext()
        context.prec = 4
        context.clear_flags()
        context.flags[Inexact] = True
        context.flags[Rounded] = True
        return Decimal(value)

    @staticmethod
    def _replace_context(value):
        setcontext(Context(prec=2, rounding=ROUND_DOWN, Emax=10, Emin=-10))
        return Decimal(value)

    def test_quantity_precision_mutation(self):
        self._case(checked_quantity, "3.00000001", "3.00000001", self._low_precision)

    def test_price_precision_mutation(self):
        self._case(checked_unit_price, "0.12345678", "0.12345678", self._low_precision)

    def test_quantity_rounding_mutation(self):
        self._case(checked_quantity, "5", "5", self._alter_rounding)

    def test_price_rounding_mutation(self):
        self._case(checked_unit_price, "-5.5", "-5.5", self._alter_rounding)

    def test_quantity_exponent_mutation(self):
        self._case(checked_quantity, "9.001", "9.001", self._alter_exponents)

    def test_price_exponent_mutation(self):
        self._case(checked_unit_price, "0.00000001", "0.00000001", self._alter_exponents)

    def test_quantity_trap_mutation(self):
        self._case(checked_quantity, "2", "2", self._alter_traps)

    def test_price_trap_mutation(self):
        self._case(checked_unit_price, "-2", "-2", self._alter_traps)

    def test_quantity_flag_mutation(self):
        self._case(checked_quantity, "3", "3", self._alter_flags)

    def test_price_flag_mutation(self):
        self._case(checked_unit_price, "0.01234567", "0.01234567", self._alter_flags)

    def test_quantity_setcontext_mutation(self):
        self._case(checked_quantity, "10", "10", self._replace_context)

    def test_price_setcontext_mutation(self):
        self._case(checked_unit_price, "10", "10", self._replace_context)

    def test_grouped_quantity_context_mutation(self):
        def poison(_):
            getcontext().prec = 2
            return Decimal("1234.50")
        self._case(checked_quantity, "1,234.50", "1234.5", poison)

    def test_parenthesized_accounting_context_mutation(self):
        def poison(_):
            getcontext().prec = 2
            return Decimal("-1234.50")
        self._case(checked_unit_price, "($1,234.50)", "-1234.5", poison)

    def test_non_native_result_context_restored(self):
        def poison(_):
            getcontext().prec = 2
            return 1.0
        self._case(checked_unit_price, "1", None, poison, error=True)

    def test_wrong_amount_and_poisoned_context_rejected(self):
        def poison(_):
            getcontext().prec = 2
            return Decimal("2")
        self._case(checked_quantity, "1", None, poison, error=True)

    def test_private_exception_and_context_restored(self):
        def poison(_):
            getcontext().prec = 2
            getcontext().rounding = ROUND_DOWN
            raise OSError("PRIVATE_FINANCE_PATH")
        self._case(checked_unit_price, "1", None, poison, error=True)

    def test_untrusted_trap_error_and_context_restored(self):
        def poison(_):
            getcontext().traps[DivisionByZero] = True
            return Decimal(1) / Decimal(0)
        self._case(checked_quantity, "1", None, poison, error=True)

    def test_valid_price_result_in_low_precision_protected(self):
        with localcontext(Context(prec=64)):
            def poison(value):
                getcontext().prec = 2
                return Decimal(value)
            a = checked_unit_price("0.12345678", poison)
            b = checked_quantity("3", poison)
            self.assertEqual(a * b, Decimal("0.37037034"))
            self.assertEqual(getcontext().prec, 64)

    def test_repeated_calls_do_not_accumulate_context_changes(self):
        with localcontext(Context(prec=64)) as outer:
            before = outer.copy()
            for n in range(30):
                poison = (self._alter_rounding, self._replace_context,
                          self._alter_exponents, self._alter_flags)[n % 4]
                self.assertEqual(checked_quantity("3", poison), Decimal(3))
                self.assertEqual(getcontext().prec, before.prec)
                self.assertEqual(getcontext().flags, before.flags)

    def test_invalid_source_does_not_invoke_poisoning_callback(self):
        with localcontext(Context(prec=64)) as outer:
            before = outer.copy()
            called = []
            def poison(_):
                called.append(True)
                getcontext().prec = 2
                return Decimal(1)
            with self.assertRaises(ValueError):
                checked_quantity("-1", poison)
            self.assertEqual(called, [])
            self.assertEqual(getcontext().prec, before.prec)

    def test_valid_nested_localcontext_preserves_caller(self):
        def poison(value):
            with localcontext() as ctx:
                ctx.prec = 2
                ctx.rounding = ROUND_DOWN
                return Decimal(value)
        self._case(checked_unit_price, "0.12345678", "0.12345678", poison)


if __name__ == "__main__":
    unittest.main()
