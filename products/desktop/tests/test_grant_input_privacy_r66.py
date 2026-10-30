"""R66 focused, engine-independent GrantAudit confidential-input regressions."""
from __future__ import annotations

import unittest
from fvs_suite.grant_input import claim_kind


class GrantClaimPrivacyR66Tests(unittest.TestCase):
    def test_explicit_claim(self):
        self.assertEqual(claim_kind({"claim_type": "claim", "row": "2"}), "claim")

    def test_explicit_credit(self):
        self.assertEqual(claim_kind({"claim_type": "credit", "row": "3"}), "credit")

    def test_uppercase_and_whitespace_compatibility(self):
        self.assertEqual(claim_kind({"claim_type": "  CrEdIt \t", "row": "3"}), "credit")

    def test_missing_type_defaults_to_claim(self):
        self.assertEqual(claim_kind({"row": "2"}), "claim")

    def test_whitespace_only_type_preserves_rejection(self):
        with self.assertRaisesRegex(ValueError, "Unsupported claim_type"):
            claim_kind({"claim_type": " \t", "row": "2"})

    def test_none_type_defaults_to_claim(self):
        self.assertEqual(claim_kind({"claim_type": None, "row": "2"}), "claim")

    def test_reject_unknown_type_without_echo(self):
        secret = "ACME confidential reimbursement #841"
        with self.assertRaises(ValueError) as caught:
            claim_kind({"claim_type": secret, "row": "42"})
        self.assertEqual(str(caught.exception),
                         "Unsupported claim_type at claim CSV physical row 42; use claim or credit")
        self.assertNotIn(secret, str(caught.exception))

    def test_reject_multiline_control_sequence_without_echo(self):
        secret = "void\n\x1b[31mPERSONAL DATA\x1b[0m"
        with self.assertRaises(ValueError) as caught:
            claim_kind({"claim_type": secret, "row": "12"})
        self.assertNotIn("PERSONAL DATA", str(caught.exception))
        self.assertNotIn("\x1b", str(caught.exception))
        self.assertNotIn("\n", str(caught.exception))

    def test_reject_untrusted_row_label(self):
        with self.assertRaisesRegex(ValueError, r"physical row \?") as caught:
            claim_kind({"claim_type": "invalid", "row": "2\nSECRET ACCOUNT"})
        self.assertNotIn("SECRET", str(caught.exception))

    def test_unicode_digits_not_accepted_as_row(self):
        with self.assertRaisesRegex(ValueError, r"physical row \?"):
            claim_kind({"claim_type": "invalid", "row": "٢"})

    def test_plus_sign_not_accepted_as_row(self):
        with self.assertRaisesRegex(ValueError, r"physical row \?"):
            claim_kind({"claim_type": "invalid", "row": "+2"})

    def test_zero_not_accepted_as_row(self):
        with self.assertRaisesRegex(ValueError, r"physical row \?"):
            claim_kind({"claim_type": "invalid", "row": "0"})

    def test_leading_zeros_not_accepted_as_row(self):
        with self.assertRaisesRegex(ValueError, r"physical row \?"):
            claim_kind({"claim_type": "invalid", "row": "002"})

    def test_excessively_long_row_label_not_echoed(self):
        secret = "9" * 6000
        with self.assertRaisesRegex(ValueError, r"physical row \?") as caught:
            claim_kind({"claim_type": "invalid", "row": secret})
        self.assertNotIn(secret, str(caught.exception))

    def test_missing_row_is_private(self):
        with self.assertRaisesRegex(ValueError, r"physical row \?"):
            claim_kind({"claim_type": "invalid"})

    def test_non_string_type_never_echoed(self):
        class PrivateValue:
            def __str__(self):
                return "private trust beneficiary"
        with self.assertRaises(ValueError) as caught:
            claim_kind({"claim_type": PrivateValue(), "row": "2"})
        self.assertNotIn("beneficiary", str(caught.exception))

    def test_physical_line_for_csv_with_quoted_newlines(self):
        with self.assertRaisesRegex(ValueError, r"physical row 17"):
            claim_kind({"claim_type": "void", "row": "17"})


if __name__ == "__main__":
    unittest.main()
