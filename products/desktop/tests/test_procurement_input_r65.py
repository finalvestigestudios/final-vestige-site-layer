"""R65: exact policy threshold syntax and confidential movement error handling."""
from __future__ import annotations

import unittest
from decimal import Decimal

from fvs_suite.procurement_input import event_kind, exact_policy_limit


class PricePolicyIntakeR65Tests(unittest.TestCase):
    def test_fixed_point_boundaries_are_exact_decimals(self):
        cases = (("0", "0"), (0, "0"), ("0.01", "0.01"),
                 ("0.00000001", "0.00000001"),
                 ("100.00000000", "100.00000000"), (100, "100"))
        for raw, expected in cases:
            with self.subTest(raw=raw):
                parsed = exact_policy_limit(raw, "price_absolute", Decimal("100.00"))
                self.assertIsInstance(parsed, Decimal)
                self.assertEqual(parsed, Decimal(expected))

    def test_fractional_policy_range_is_exact(self):
        for value in ("0", "0.02", "0.10000000", "0.00000001"):
            with self.subTest(value=value):
                self.assertEqual(exact_policy_limit(value, "price_fraction", Decimal("0.10")), Decimal(value))

    def test_over_limit_is_rejected_without_echo(self):
        for value in ("100.00000001", "101", "0.10000001", "1"):
            maximum = Decimal("0.10") if value in ("0.10000001", "1") else Decimal("100")
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as raised:
                    exact_policy_limit(value, "price_limit", maximum)
                self.assertNotIn(value, str(raised.exception))

    def test_exponent_sign_locale_and_non_ascii_are_rejected(self):
        bad = ("1e-2", "1E+1", "+0.02", "-0", "01.00", " 0.02", "0.02 ",
               ".02", "0.", "0,02", "٠.٢", "０.０２", "0\n1", "NaN", "Infinity")
        for value in bad:
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as raised:
                    exact_policy_limit(value, "price_fraction", Decimal("0.10"))
                self.assertNotIn(value, str(raised.exception))

    def test_more_than_eight_fractional_places_is_rejected(self):
        for value in ("0.000000001", "0.020000000", "0." + "1" * 8000):
            with self.subTest(length=len(value)):
                with self.assertRaises(ValueError):
                    exact_policy_limit(value, "price_fraction", Decimal("0.10"))

    def test_float_bool_and_decimal_object_inputs_are_rejected(self):
        for value in (True, False, 0.02, Decimal("0.02"), None, [], {}):
            with self.subTest(type=type(value).__name__):
                with self.assertRaises(ValueError):
                    exact_policy_limit(value, "price_fraction", Decimal("0.10"))

    def test_integer_json_value_still_accepted(self):
        self.assertEqual(exact_policy_limit(1, "price_absolute", Decimal(100)), Decimal(1))

    def test_invalid_error_does_not_repeat_source_value(self):
        private = "ACME/private invoice 442\n\x1b[31mSECRET"
        with self.assertRaises(ValueError) as raised:
            event_kind({"event_type": private, "row": "42"}, source="invoice")
        self.assertEqual(str(raised.exception), "Unsupported invoice event_type at input physical row 42")
        self.assertNotIn("SECRET", str(raised.exception))

    def test_non_numeric_row_citation_does_not_leak(self):
        with self.assertRaisesRegex(ValueError, r"physical row \?") as raised:
            event_kind({"event_type": "confidential", "row": "42\nPII"}, source="receipt")
        self.assertNotIn("PII", str(raised.exception))

    def test_reject_invalid_stream(self):
        with self.assertRaisesRegex(ValueError, "Unsupported procurement event stream"):
            event_kind({"event_type": "invoice"}, source="refund")

    def test_expected_event_types_remain_valid_and_casefolded(self):
        for stream, label, expected in (("invoice", " CREDIT ", "credit"),
                                        ("invoice", "invoice", "invoice"),
                                        ("receipt", " ReTuRn ", "return"),
                                        ("receipt", "receipt", "receipt")):
            with self.subTest(stream=stream, label=label):
                self.assertEqual(event_kind({"event_type": label}, source=stream), expected)

    def test_empty_event_type_preserves_legacy_source_default(self):
        for stream in ("invoice", "receipt"):
            with self.subTest(stream=stream):
                self.assertEqual(event_kind({"event_type": ""}, source=stream), stream)
                self.assertEqual(event_kind({}, source=stream), stream)


if __name__ == "__main__":
    unittest.main()
