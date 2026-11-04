"""R176: shared financial numeric parsers reject executable value disguises.

Synthetic direct-API regression fixtures only. No accounts, network, source
modification, compliance inference, or premium distribution.
"""
from __future__ import annotations

import unittest
from decimal import Decimal

from fvs_suite import engine


class ForgedStr(str):
    def __str__(self):
        return "0"


class TrapStr(str):
    def __str__(self):
        raise AssertionError("untrusted string conversion called")


class ForgedInt(int):
    def __str__(self):
        return "0"


class TrapInt(int):
    def __str__(self):
        raise AssertionError("untrusted integer conversion called")


class ForgedDecimal(Decimal):
    def __str__(self):
        return "0"


class TrapDecimal(Decimal):
    def __str__(self):
        raise AssertionError("untrusted Decimal conversion called")


class ArbitraryObject:
    def __str__(self):
        raise AssertionError("untrusted arbitrary conversion called")


class SharedPrimitiveCustodyR176(unittest.TestCase):
    def invalid(self, parser, value, message):
        with self.assertRaisesRegex(ValueError, message) as caught:
            parser(value)
        self.assertNotIn("SENSITIVE_ACCOUNT", str(caught.exception))

    def test_money_rejects_forged_str(self):
        self.invalid(engine.money, ForgedStr("999999999999999"), "amount format")

    def test_money_rejects_trap_str_before_conversion(self):
        self.invalid(engine.money, TrapStr("SENSITIVE_ACCOUNT"), "amount format")

    def test_money_rejects_forged_int(self):
        self.invalid(engine.money, ForgedInt(999999999999999), "amount format")

    def test_money_rejects_trap_int_before_conversion(self):
        self.invalid(engine.money, TrapInt(25), "amount format")

    def test_money_rejects_forged_decimal(self):
        self.invalid(engine.money, ForgedDecimal("999999999999999"), "amount format")

    def test_money_rejects_trap_decimal_before_conversion(self):
        self.invalid(engine.money, TrapDecimal("20"), "amount format")

    def test_money_rejects_arbitrary_object(self):
        self.invalid(engine.money, ArbitraryObject(), "amount format")

    def test_money_rejects_float_and_bool(self):
        for value in (0.1, True, False):
            with self.subTest(value=repr(value)):
                self.invalid(engine.money, value, "amount format")

    def test_unit_cost_rejects_forged_str(self):
        self.invalid(engine.unit_cost, ForgedStr("999999999999999"), "amount format")

    def test_unit_cost_rejects_trap_str_before_conversion(self):
        self.invalid(engine.unit_cost, TrapStr("SENSITIVE_ACCOUNT"), "amount format")

    def test_unit_cost_rejects_forged_int(self):
        self.invalid(engine.unit_cost, ForgedInt(999999999999999), "amount format")

    def test_unit_cost_rejects_trap_int_before_conversion(self):
        self.invalid(engine.unit_cost, TrapInt(23), "amount format")

    def test_unit_cost_rejects_forged_decimal(self):
        self.invalid(engine.unit_cost, ForgedDecimal("999999999999999"), "amount format")

    def test_unit_cost_rejects_trap_decimal_before_conversion(self):
        self.invalid(engine.unit_cost, TrapDecimal("7"), "amount format")

    def test_unit_cost_rejects_arbitrary_object(self):
        self.invalid(engine.unit_cost, ArbitraryObject(), "amount format")

    def test_unit_cost_rejects_float_and_bool(self):
        for value in (1.25, True, False):
            with self.subTest(value=repr(value)):
                self.invalid(engine.unit_cost, value, "amount format")

    def test_quantity_rejects_forged_str(self):
        self.invalid(engine.qty, ForgedStr("999999999999999"), "quantity format")

    def test_quantity_rejects_trap_str_before_conversion(self):
        self.invalid(engine.qty, TrapStr("SENSITIVE_ACCOUNT"), "quantity format")

    def test_quantity_rejects_forged_int(self):
        self.invalid(engine.qty, ForgedInt(999999999999999), "quantity format")

    def test_quantity_rejects_trap_int_before_conversion(self):
        self.invalid(engine.qty, TrapInt(25), "quantity format")

    def test_quantity_rejects_forged_decimal(self):
        self.invalid(engine.qty, ForgedDecimal("999999999999999"), "quantity format")

    def test_quantity_rejects_trap_decimal_before_conversion(self):
        self.invalid(engine.qty, TrapDecimal("1"), "quantity format")

    def test_quantity_rejects_arbitrary_object(self):
        self.invalid(engine.qty, ArbitraryObject(), "quantity format")

    def test_quantity_rejects_float_and_bool(self):
        for value in (0.5, True, False):
            with self.subTest(value=repr(value)):
                self.invalid(engine.qty, value, "quantity format")

    def test_money_valid_native_strings_ints_and_decimals(self):
        self.assertEqual(engine.money("($1,234.56)"), Decimal("-1234.56"))
        self.assertEqual(engine.money(12), Decimal("12.00"))
        self.assertEqual(engine.money(Decimal("0.005")), Decimal("0.01"))

    def test_unit_cost_valid_native_strings_ints_and_decimals(self):
        self.assertEqual(engine.unit_cost("0.00000001"), Decimal("0.00000001"))
        self.assertEqual(engine.unit_cost(7), Decimal("7"))
        self.assertEqual(engine.unit_cost(Decimal("12.12345678")), Decimal("12.12345678"))

    def test_quantity_valid_native_strings_ints_and_decimals(self):
        self.assertEqual(engine.qty("1,000.125"), Decimal("1000.125"))
        self.assertEqual(engine.qty(7), Decimal("7"))
        self.assertEqual(engine.qty(Decimal("1.250")), Decimal("1.250"))

    def test_native_huge_integer_fails_before_conversion_limit(self):
        enormous = 10 ** 6000
        for parser, message in ((engine.money, "amount format"),
                                (engine.unit_cost, "amount format"),
                                (engine.qty, "quantity format")):
            with self.subTest(parser=parser.__name__):
                self.invalid(parser, enormous, message)

    def test_exact_decimal_boundaries_unchanged(self):
        self.assertEqual(engine.money("1,000,000,000,000"), Decimal("1000000000000.00"))
        self.invalid(engine.money, "1,000,000,000,000.01", "out-of-range")
        self.invalid(engine.qty, "0.000000001", "precision")
        self.invalid(engine.unit_cost, "0.000000001", "precision")

    def test_scientific_notation_remains_rejected(self):
        for parser, value, message in ((engine.money, Decimal("1E+3"), "amount format"),
                                       (engine.unit_cost, Decimal("1E+3"), "amount format"),
                                       (engine.qty, Decimal("1E+3"), "quantity format")):
            with self.subTest(parser=parser.__name__):
                self.invalid(parser, value, message)


if __name__ == "__main__":
    unittest.main()
