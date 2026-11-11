"""R352: injectable document normalizers cannot alter audit Decimal context.

Synthetic IDs only. Does not validate an executable or approve procurement.
"""
from __future__ import annotations

from decimal import (Clamped, Context, Decimal, DivisionByZero, Inexact,
                     InvalidOperation, ROUND_DOWN, ROUND_HALF_EVEN, Rounded,
                     getcontext, localcontext, setcontext)
import unittest

from fvs_suite.procurement_reference import normalized_document_key

ERROR = "Procurement document normalization requires a native text key"


def plain(text: str) -> str:
    return text.upper()


def mutate_precision(text: str) -> str:
    getcontext().prec = 1
    return plain(text)


def mutate_rounding(text: str) -> str:
    getcontext().rounding = ROUND_DOWN
    return plain(text)


def mutate_exponents(text: str) -> str:
    ctx = getcontext()
    ctx.Emax = 10
    ctx.Emin = -10
    ctx.capitals = 0
    ctx.clamp = 1
    return plain(text)


def mutate_flags_and_traps(text: str) -> str:
    ctx = getcontext()
    ctx.flags[Inexact] = True
    ctx.flags[Rounded] = True
    ctx.traps[DivisionByZero] = False
    ctx.traps[InvalidOperation] = False
    return plain(text)


def replace_context(text: str) -> str:
    setcontext(Context(prec=1, rounding=ROUND_DOWN))
    return plain(text)


class MaliciousText(str):
    def upper(self):
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")


def context_state(ctx):
    return (ctx.prec, ctx.rounding, ctx.Emin, ctx.Emax, ctx.capitals, ctx.clamp,
            dict(ctx.flags), dict(ctx.traps))


class IdentifierContextCustodyR352(unittest.TestCase):
    def assert_untouched(self, callback, *, label="Inv-1"):
        with localcontext(Context(prec=64, rounding=ROUND_HALF_EVEN)):
            context = getcontext()
            old = context.copy()
            self.assertEqual(normalized_document_key(label, callback), label.upper())
            self.assertIs(getcontext(), context)
            self.assertEqual(context_state(getcontext()), context_state(old))
            self.assertEqual(getcontext().flags, old.flags)
            self.assertEqual(getcontext().traps, old.traps)

    def test_plain_callback(self):
        self.assert_untouched(plain)

    def test_precision_mutation_is_isolated(self):
        self.assert_untouched(mutate_precision)

    def test_rounding_mutation_is_isolated(self):
        self.assert_untouched(mutate_rounding)

    def test_exponent_limits_are_isolated(self):
        self.assert_untouched(mutate_exponents)

    def test_flags_and_traps_are_isolated(self):
        self.assert_untouched(mutate_flags_and_traps)

    def test_setcontext_is_isolated(self):
        self.assert_untouched(replace_context)

    def test_callback_can_use_localcontext(self):
        def nested(text):
            with localcontext(Context(prec=2)):
                return text.upper()
        self.assert_untouched(nested)

    def test_callback_can_raise_private_error_without_context_leak(self):
        def error(_):
            getcontext().prec = 1
            raise RuntimeError("PRIVATE_FINANCIAL_PATH")
        with localcontext(Context(prec=64)):
            original = getcontext().copy()
            with self.assertRaises(ValueError) as raised:
                normalized_document_key("Inv-1", error)
            self.assertEqual(str(raised.exception), ERROR)
            self.assertIsNone(raised.exception.__cause__)
            self.assertTrue(raised.exception.__suppress_context__)
            self.assertEqual(context_state(getcontext()), context_state(original))

    def test_setcontext_then_exception_is_isolated(self):
        def error(_):
            setcontext(Context(prec=1))
            raise OSError("PRIVATE_FINANCIAL_PATH")
        with localcontext(Context(prec=64)):
            original = getcontext().copy()
            with self.assertRaisesRegex(ValueError, "native text key"):
                normalized_document_key("Inv-1", error)
            self.assertEqual(context_state(getcontext()), context_state(original))

    def test_invalid_result_is_rejected_after_context_mutation(self):
        def fake(_):
            getcontext().prec = 1
            return 42
        with localcontext(Context(prec=64)):
            original = getcontext().copy()
            with self.assertRaisesRegex(ValueError, "native text key"):
                normalized_document_key("INV-1", fake)
            self.assertEqual(context_state(getcontext()), context_state(original))

    def test_string_subclass_result_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "native text key"):
            normalized_document_key("INV-1", lambda _: MaliciousText("INV1"))

    def test_bad_source_identity_rejected_before_callback(self):
        calls = []
        with self.assertRaisesRegex(ValueError, "native text or a bounded integer"):
            normalized_document_key(MaliciousText("INV-1"), lambda v: calls.append(v))
        self.assertEqual(calls, [])

    def test_numeric_document_id_compatibility(self):
        with localcontext(Context(prec=64)):
            self.assertEqual(normalized_document_key(12345, mutate_precision), "12345")
            self.assertEqual(getcontext().prec, 64)

    def test_boolean_id_does_not_call_callback(self):
        calls = []
        with self.assertRaises(ValueError):
            normalized_document_key(True, lambda x: calls.append(x))
        self.assertEqual(calls, [])

    def test_oversized_integer_id_does_not_call_callback(self):
        calls = []
        with self.assertRaises(ValueError):
            normalized_document_key(1 << 270, lambda x: calls.append(x))
        self.assertEqual(calls, [])

    def test_none_id_does_not_call_callback(self):
        calls = []
        with self.assertRaises(ValueError):
            normalized_document_key(None, lambda x: calls.append(x))
        self.assertEqual(calls, [])

    def test_no_ambient_precision_dependency(self):
        with localcontext(Context(prec=64)):
            high = normalized_document_key("Invoice 42", replace_context)
        with localcontext(Context(prec=2)):
            low = normalized_document_key("Invoice 42", replace_context)
        self.assertEqual(high, low)

    def test_repeated_calls_are_deterministic_and_preserve_context(self):
        with localcontext(Context(prec=64)):
            context = getcontext()
            expected = context.copy()
            output = [normalized_document_key("Inv-42", mutate_precision) for _ in range(25)]
            self.assertEqual(output, ["INV-42"] * 25)
            self.assertIs(getcontext(), context)
            self.assertEqual(context_state(getcontext()), context_state(expected))

    def test_preexisting_flags_are_not_dropped(self):
        with localcontext(Context(prec=64)):
            getcontext().flags[Clamped] = True
            before = getcontext().copy()
            normalized_document_key("Invoice42", mutate_flags_and_traps)
            self.assertEqual(getcontext().flags, before.flags)

    def test_preexisting_disabled_trap_is_not_enabled(self):
        with localcontext(Context(prec=64)):
            getcontext().traps[DivisionByZero] = False
            before = getcontext().copy()
            normalized_document_key("Invoice42", mutate_flags_and_traps)
            self.assertEqual(getcontext().traps, before.traps)

    def test_callback_receives_plain_source_text(self):
        received = []
        def observe(value):
            received.append((value, type(value)))
            return value
        self.assertEqual(normalized_document_key("INV-4", observe), "INV-4")
        self.assertEqual(received, [("INV-4", str)])

    def test_callback_result_is_not_renormalized(self):
        self.assertEqual(normalized_document_key("INV-4", lambda _: "CASE-SENSITIVE"),
                         "CASE-SENSITIVE")

    def test_no_numeric_conversion_for_unusual_native_unicode(self):
        self.assertEqual(normalized_document_key("Ä-4", plain), "Ä-4")

    def test_later_exact_invoice_total_not_rounded_by_identity(self):
        with localcontext(Context(prec=64)):
            expected = Decimal(3) * Decimal("0.12345678")
            normalized_document_key("INV-1", mutate_precision)
            self.assertEqual(Decimal(3) * Decimal("0.12345678"), expected)
            self.assertEqual(format(expected, "f"), "0.37037034")

    def test_later_policy_expected_total_not_rounded_by_setcontext(self):
        with localcontext(Context(prec=64)):
            normalized_document_key("INV-1", replace_context)
            self.assertEqual(format(Decimal(3) * Decimal("0.12345678"), "f"),
                             "0.37037034")

    def test_later_decimal_calculation_does_not_trip_callback_trap(self):
        def poison(text):
            getcontext().traps[Inexact] = True
            return text.upper()
        with localcontext(Context(prec=64)):
            normalized_document_key("INV-1", poison)
            self.assertEqual(Decimal(3) * Decimal("0.12345678"),
                             Decimal("0.37037034"))


if __name__ == "__main__":
    unittest.main()
