"""R388 full-repository integration regression for offline premium policy privacy.

Requires real fvs_suite.procurement and descriptor-based csv_snapshot; run in CI.
No real customer files or automated approval decisions.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from fvs_suite.procurement import load_price_policy


class PricePolicyPrivacyIntegrationR388(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r388-")
        self.addCleanup(temp.cleanup)
        self.file = Path(temp.name) / "review-policy.json"

    def save(self, content: bytes):
        self.file.write_bytes(content)
        return self.file

    def private_error(self, raw: bytes, public_message: str):
        self.save(raw)
        with self.assertRaises(ValueError) as result:
            load_price_policy(self.file)
        exc = result.exception
        self.assertEqual(str(exc), public_message)
        self.assertIsNone(exc.__cause__)
        self.assertIsNone(exc.__context__)
        self.assertNotIn("CLIENT_PRIVATE", str(exc))

    def test_malformed_json_no_payload_in_error_chain(self):
        self.private_error(b'{"client":"CLIENT_PRIVATE",', "Invalid UTF-8 JSON price policy")

    def test_invalid_utf8_no_payload_in_error_chain(self):
        self.private_error(b'{"client":"CLIENT_PRIVATE\xff"}', "Invalid UTF-8 JSON price policy")

    def test_trailing_json_no_payload_in_error_chain(self):
        self.private_error(b'{"client":"CLIENT_PRIVATE"}broken', "Invalid UTF-8 JSON price policy")

    def test_snapshot_failure_does_not_chain_private_path(self):
        self.save(b'{}')
        with patch("fvs_suite.csv_snapshot.read_csv_snapshot",
                   side_effect=ValueError("CLIENT_PRIVATE_PATH_FROM_SNAPSHOT")):
            with self.assertRaises(ValueError) as result:
                load_price_policy(self.file)
        exc = result.exception
        self.assertEqual(str(exc),
                         "Price policy requires a stable regular JSON file (8 KiB maximum)")
        self.assertIsNone(exc.__context__)
        self.assertIsNone(exc.__cause__)

    def test_missing_path_reports_generic_error_without_chain(self):
        with self.assertRaises(ValueError) as result:
            load_price_policy(self.file)
        self.assertIn("stable regular JSON", str(result.exception))
        self.assertIsNone(result.exception.__cause__)
        self.assertIsNone(result.exception.__context__)

    def test_valid_policy_still_returns_exact_decimal_and_sha(self):
        raw = b'{"version":1,"price_absolute":"0.01000000","price_fraction":"0.02"}'
        self.save(raw)
        policy = load_price_policy(self.file)
        self.assertEqual(policy.absolute, Decimal("0.01000000"))
        self.assertEqual(policy.fraction, Decimal("0.02"))
        self.assertEqual(policy.source_sha256, hashlib.sha256(raw).hexdigest())
        self.assertFalse(policy.widened)

    def test_duplicate_key_policy_is_rejected(self):
        self.private_error(b'{"version":1,"version":1}', "Duplicate JSON price policy key")

    def test_nonfinite_json_policy_is_rejected(self):
        self.private_error(b'{"version":1,"price_absolute":NaN,"price_fraction":"0.02"}',
                           "Nonfinite JSON values are not allowed")

    def test_missing_threshold_never_defaulted_implicitly(self):
        self.save(b'{"version":1,"price_absolute":"0.01"}')
        with self.assertRaisesRegex(ValueError, "requires exactly version=1"):
            load_price_policy(self.file)

    def test_wider_review_threshold_is_not_approval(self):
        self.save(b'{"version":1,"price_absolute":"1.00","price_fraction":"0.05"}')
        policy = load_price_policy(self.file)
        self.assertTrue(policy.widened)
        self.assertEqual(policy.absolute, Decimal("1.00"))


if __name__ == "__main__":
    unittest.main()
