"""R388 source-level customer-data privacy and strict policy parsing checks."""
from __future__ import annotations

import unittest

from fvs_suite.procurement_policy_private_json_r388 import decode_price_policy_document


class PricePolicyPrivateJsonR388(unittest.TestCase):
    def assert_rejected_privately(self, source: bytes, message: str):
        with self.assertRaises(ValueError) as result:
            decode_price_policy_document(source)
        error = result.exception
        self.assertIn(message, str(error))
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn("CLIENT_PRIVATE", str(error))

    def test_valid_bom_document(self):
        self.assertEqual(decode_price_policy_document(
            b'\xef\xbb\xbf{"version":1,"price_absolute":"0.01","price_fraction":"0.02"}'),
            {"version": 1, "price_absolute": "0.01", "price_fraction": "0.02"})

    def test_valid_nested_object_not_silently_coerced(self):
        self.assertEqual(decode_price_policy_document(b'{"x":{"y":1}}'), {"x": {"y": 1}})

    def test_valid_json_array_retains_parser_contract(self):
        self.assertEqual(decode_price_policy_document(b'[1,2,3]'), [1, 2, 3])

    def test_valid_empty_dict_retains_parser_contract(self):
        self.assertEqual(decode_price_policy_document(b'{}'), {})

    def test_invalid_utf8_never_chains_sensitive_bytes(self):
        self.assert_rejected_privately(b'{"private":"CLIENT_PRIVATE\xff"}', "Invalid UTF-8 JSON")

    def test_invalid_continuation_never_chains_payload(self):
        self.assert_rejected_privately(b'CLIENT_PRIVATE\x80', "Invalid UTF-8 JSON")

    def test_malformed_json_never_chains_sensitive_doc(self):
        self.assert_rejected_privately(b'{"client":"CLIENT_PRIVATE",', "Invalid UTF-8 JSON")

    def test_trailing_content_never_chains_sensitive_doc(self):
        self.assert_rejected_privately(b'{"client":"CLIENT_PRIVATE"}garbage', "Invalid UTF-8 JSON")

    def test_empty_bytes_rejected_privately(self):
        self.assert_rejected_privately(b'', "Invalid UTF-8 JSON")

    def test_duplicate_key_rejection_kept(self):
        self.assert_rejected_privately(b'{"x":1,"x":"CLIENT_PRIVATE"}', "Duplicate JSON price policy key")

    def test_nested_duplicate_key_rejection_kept(self):
        self.assert_rejected_privately(b'{"x":{"k":1,"k":2}}', "Duplicate JSON price policy key")

    def test_nonfinite_nan_rejection_kept(self):
        self.assert_rejected_privately(b'{"x":NaN}', "Nonfinite JSON values")

    def test_nonfinite_infinity_rejection_kept(self):
        self.assert_rejected_privately(b'{"x":Infinity}', "Nonfinite JSON values")

    def test_nonfinite_negative_infinity_rejection_kept(self):
        self.assert_rejected_privately(b'{"x":-Infinity}', "Nonfinite JSON values")

    def test_no_untrusted_nonbytes_coercion(self):
        for value in (bytearray(b'{}'), memoryview(b'{}'), '{"x":1}', None):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError) as result:
                    decode_price_policy_document(value)
                self.assertIsNone(result.exception.__cause__)
                self.assertIsNone(result.exception.__context__)

    def test_repeated_keys_in_different_objects_permitted(self):
        self.assertEqual(decode_price_policy_document(b'{"left":{"id":1},"right":{"id":2}}'),
                         {"left": {"id": 1}, "right": {"id": 2}})

    def test_boolean_and_numeric_values_pass_through(self):
        self.assertEqual(decode_price_policy_document(b'{"x":true,"y":5}'), {"x": True, "y": 5})


if __name__ == '__main__':
    unittest.main()
