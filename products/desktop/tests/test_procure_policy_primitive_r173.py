"""R173: policy thresholds and procurement stream identities are actual built-in primitives.

Synthetic data only. A direct API caller must not spoof policy limits using
Python str/int subclasses or trigger hostile string/hash hooks in error paths.
"""
from __future__ import annotations

from decimal import Decimal
import unittest

from fvs_suite.grant_input import claim_kind
from fvs_suite.procurement_input import event_kind, exact_policy_limit


class LyingString(str):
    def __str__(self):
        return "0"


class LyingInteger(int):
    def __str__(self):
        return "0"


class ExplodingString(str):
    def __str__(self):
        raise AssertionError("untrusted string hook invoked")

    def __eq__(self, other):
        raise AssertionError("untrusted equality hook invoked")

    def __hash__(self):
        raise AssertionError("untrusted hash hook invoked")


class ExplodingInteger(int):
    def __str__(self):
        raise AssertionError("untrusted integer hook invoked")

    def __eq__(self, other):
        raise AssertionError("untrusted equality hook invoked")

    def __hash__(self):
        raise AssertionError("untrusted integer hash hook invoked")


class MaliciousSource:
    def __hash__(self):
        raise AssertionError("untrusted stream hash invoked")

    def __eq__(self, other):
        raise AssertionError("untrusted stream comparison invoked")

    def __str__(self):
        raise AssertionError("untrusted stream value printed")


class ProcurePolicyNativePrimitiveR173(unittest.TestCase):
    MAX_ABSOLUTE = Decimal("100.00")
    MAX_FRACTION = Decimal("0.10")

    def limit(self, value, maximum=None):
        return exact_policy_limit(value, "price_fraction", maximum or self.MAX_FRACTION)

    def reject(self, value, maximum=None):
        with self.assertRaises(ValueError) as error:
            self.limit(value, maximum)
        self.assertNotIn("SECRET", str(error.exception))
        return str(error.exception)

    def test_string_subclass_lies_about_stored_absolute(self):
        self.reject(LyingString("9999"), self.MAX_ABSOLUTE)

    def test_string_subclass_lies_about_stored_fraction(self):
        self.reject(LyingString("999"), self.MAX_FRACTION)

    def test_integer_subclass_lies_about_stored_absolute(self):
        self.reject(LyingInteger(9999), self.MAX_ABSOLUTE)

    def test_integer_subclass_lies_about_stored_fraction(self):
        self.reject(LyingInteger(999), self.MAX_FRACTION)

    def test_subclass_string_hook_cannot_run(self):
        self.reject(ExplodingString("SECRET 10"))

    def test_subclass_integer_hook_cannot_run(self):
        self.reject(ExplodingInteger(999))

    def test_subclass_private_string_not_printed(self):
        self.assertNotIn("SECRET", self.reject(LyingString("SECRET financial data")))

    def test_subclass_private_integer_not_printed(self):
        self.assertNotIn("9999", self.reject(LyingInteger(9999)))

    def test_spoofed_str_equality_hooks_not_run(self):
        self.reject(ExplodingString("SECRET"))

    def test_spoofed_int_equality_hooks_not_run(self):
        self.reject(ExplodingInteger(500))

    def test_bool_subclass_family_rejected(self):
        self.reject(True)
        self.reject(False)

    def test_exact_string_absolute_preserved(self):
        self.assertEqual(self.limit("1.25000000", self.MAX_ABSOLUTE), Decimal("1.25000000"))

    def test_exact_int_absolute_preserved(self):
        self.assertEqual(self.limit(75, self.MAX_ABSOLUTE), Decimal(75))

    def test_exact_string_fraction_preserved(self):
        self.assertEqual(self.limit("0.02000000"), Decimal("0.02000000"))

    def test_exact_zero_integer_preserved(self):
        self.assertEqual(self.limit(0), Decimal(0))

    def test_exact_upper_bound_preserved(self):
        self.assertEqual(self.limit("0.10"), Decimal("0.10"))
        self.assertEqual(self.limit(100, self.MAX_ABSOLUTE), Decimal(100))

    def test_out_of_bounds_string_fails(self):
        self.reject("0.10000001")

    def test_out_of_bounds_integer_fails(self):
        self.reject(101, self.MAX_ABSOLUTE)

    def test_negative_integer_fails(self):
        self.reject(-1, self.MAX_ABSOLUTE)

    def test_exponent_string_fails(self):
        self.reject("1e-2")

    def test_overprecision_string_fails(self):
        self.reject("0.010000000")

    def test_non_ascii_digits_fail(self):
        self.reject("٠.٠١")

    def test_nonprimitive_numeric_rejected(self):
        for value in (Decimal("0.02"), 0.02, None, (), [], {}):
            with self.subTest(type=type(value).__name__):
                self.reject(value)

    def test_source_string_subclass_no_hash_called(self):
        with self.assertRaisesRegex(ValueError, "Unsupported procurement event stream"):
            event_kind( {"event_type": "invoice"}, source=ExplodingString("invoice"))

    def test_source_object_no_hash_called(self):
        with self.assertRaisesRegex(ValueError, "Unsupported procurement event stream"):
            event_kind({"event_type": "credit"}, source=MaliciousSource())

    def test_source_integer_no_hash_called(self):
        with self.assertRaisesRegex(ValueError, "Unsupported procurement event stream"):
            event_kind({"event_type": "invoice"}, source=ExplodingInteger(1))

    def test_source_unknown_plain_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported procurement event stream"):
            event_kind({"event_type": "invoice"}, source="unknown")

    def test_invoice_stream_retains_credit(self):
        self.assertEqual(event_kind({"event_type": " CrEdIt "}, source="invoice"), "credit")
        self.assertEqual(event_kind({}, source="invoice"), "invoice")

    def test_receipt_stream_retains_return(self):
        self.assertEqual(event_kind({"event_type": " ReTuRn "}, source="receipt"), "return")
        self.assertEqual(event_kind({}, source="receipt"), "receipt")

    def test_grant_classification_unchanged(self):
        self.assertEqual(claim_kind({"claim_type": "credit"}), "credit")
        self.assertEqual(claim_kind({}), "claim")

    def test_all_error_messages_hide_private_cells(self):
        for value in (ExplodingString("SECRET customer"), LyingString("SECRET budget")):
            with self.subTest(type=type(value).__name__):
                message = self.reject(value)
                self.assertEqual(
                    message,
                    "price_fraction must be an ASCII fixed-point decimal string or integer",
                )


if __name__ == "__main__":
    unittest.main()
