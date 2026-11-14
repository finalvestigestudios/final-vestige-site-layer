"""R426 native SpendMap source SHA tests; deterministic and offline."""
from __future__ import annotations

import traceback
import unittest

from fvs_suite.spend_source_digest_r426 import require_native_spend_source_sha256 as guard


class SpendSourceDigestR426(unittest.TestCase):
    def assert_private_refusal(self, value):
        try:
            guard(value)
        except ValueError as error:
            self.assertEqual(str(error), "Source snapshot SHA-256 must be 64 lowercase hexadecimal characters")
            self.assertIsNone(error.__context__)
            self.assertIsNone(error.__cause__)
            self.assertNotIn("PRIVATE_CUSTOMER", "".join(traceback.format_exception(error)))
        else:
            self.fail("Expected a source digest refusal")

    def test_lowercase_a_is_accepted(self):
        token = "a" * 64
        self.assertIs(guard(token), token)

    def test_lowercase_mixed_hex_is_accepted(self):
        token = "0123456789abcdef" * 4
        self.assertEqual(guard(token), token)

    def test_sha256_of_empty_bytes_is_accepted(self):
        self.assertEqual(guard("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
                         "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    def test_uppercase_hex_rejected(self):
        self.assert_private_refusal("A" * 64)

    def test_mixed_case_hex_rejected(self):
        self.assert_private_refusal("a" * 63 + "B")

    def test_nonhex_ascii_rejected(self):
        self.assert_private_refusal("g" * 64)

    def test_unicode_digit_rejected(self):
        self.assert_private_refusal("٠" * 64)

    def test_single_character_short_rejected(self):
        self.assert_private_refusal("0" * 63)

    def test_single_character_long_rejected(self):
        self.assert_private_refusal("0" * 65)

    def test_newline_and_whitespace_rejected(self):
        for value in (" " + "a" * 63, "a" * 63 + "\n", "\ta" * 32, "\r" * 64):
            with self.subTest(value=repr(value)):
                self.assert_private_refusal(value)

    def test_builtins_other_than_str_rejected(self):
        for value in (None, True, 42, 0.0, b"a" * 64, ["a" * 64], {"sha256": "a" * 64}):
            with self.subTest(type=type(value).__name__):
                self.assert_private_refusal(value)

    def test_subclass_encoded_digest_spoof_rejected_without_encode(self):
        class Forged(str):
            def encode(self, *args, **kwargs):
                raise AssertionError("PRIVATE_CUSTOMER encode invoked")
        self.assert_private_refusal(Forged("a" * 64))

    def test_subclass_equality_spoof_rejected_without_eq(self):
        class Forged(str):
            def __eq__(self, other):
                raise AssertionError("PRIVATE_CUSTOMER eq invoked")
        self.assert_private_refusal(Forged("a" * 64))

    def test_subclass_length_spoof_rejected_without_len(self):
        class Forged(str):
            def __len__(self):
                raise AssertionError("PRIVATE_CUSTOMER len invoked")
        self.assert_private_refusal(Forged("a" * 64))

    def test_subclass_str_spoof_rejected_without_str(self):
        class Forged(str):
            def __str__(self):
                raise AssertionError("PRIVATE_CUSTOMER str invoked")
        self.assert_private_refusal(Forged("a" * 64))

    def test_subclass_format_spoof_rejected_without_format(self):
        class Forged(str):
            def __format__(self, spec):
                raise AssertionError("PRIVATE_CUSTOMER format invoked")
        self.assert_private_refusal(Forged("a" * 64))

    def test_source_hash_is_not_lowercased_or_trimmed(self):
        self.assert_private_refusal("A" * 64)
        self.assert_private_refusal("a" * 64 + " ")

    def test_source_hash_does_not_claim_signature_authenticity(self):
        # This is shape/identity custody, not confirmation the digest matches a source.
        self.assertEqual(guard("0" * 64), "0" * 64)


if __name__ == "__main__":
    unittest.main()
