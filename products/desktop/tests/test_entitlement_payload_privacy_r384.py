"""R384: exact premium verifier policy, real ephemeral Ed25519, no real customer data.

The imported verifier is the repository module in CI. Local runs use a
reconstructed copy of that module plus a stubbed I/O dependency; direct file
custody / Windows behavior require separate gates.
"""
from __future__ import annotations

import base64
import binascii
import contextlib
from datetime import datetime, timezone
import io
import json
import traceback
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fvs_suite import offline_entitlement as ent

CANARY = "PRIVATE-TEST-ONLY-CLIENT-EMPLOYEE-PAYROLL"
NOW = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)


class EntitlementPayloadPrivacyR384Tests(unittest.TestCase):
    def setUp(self):
        self.signer = Ed25519PrivateKey.generate()
        self.public = self.signer.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.keys = {"issued_2026": self.public}
        self.product = "grants"
        self.item = {
            "schema": ent.SCHEMA,
            "kid": "issued_2026",
            "product": self.product,
            "license_id": "synthetic_001",
            "holder": "Synthetic Customer",
            "issued_at": "2026-11-01T00:00:00Z",
            "not_before": "2026-11-02T00:00:00Z",
            "expires_at": "2026-12-01T00:00:00Z",
        }

    def encoded(self, item=None, signer=None):
        data = dict(self.item if item is None else item)
        sig = (self.signer if signer is None else signer).sign(ent._canonical_payload(data))
        data["signature"] = base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")
        return json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    def verify(self, data, product=None, keys=None, now=NOW):
        with patch.object(ent, "_read_signed_entitlement", return_value=data) as read:
            result = ent.verify_license("synthetic-never-opened.fvslicense", product or self.product,
                                        trusted_keys=self.keys if keys is None else keys, now=now)
            read.assert_called_once_with("synthetic-never-opened.fvslicense")
            return result

    def denied(self, data, message, *, product=None):
        with self.assertRaises(ent.EntitlementError) as failure:
            self.verify(data, product)
        self.clean(failure.exception, message)

    def clean(self, exception, expected):
        self.assertEqual(str(exception), expected)
        self.assertIsNone(exception.__cause__, "raw lower-level cause must not escape")
        self.assertIsNone(exception.__context__, "raw lower-level context must not escape")
        self.assertNotIn(CANARY, repr(exception.args))
        self.assertNotIn(CANARY, "".join(traceback.format_exception(exception)))

    def test_genuine_ed25519_grant_accepted(self):
        accepted = self.verify(self.encoded())
        self.assertEqual((accepted.product, accepted.license_id), ("grants", "synthetic_001"))

    def test_genuine_ed25519_procurement_accepted(self):
        item = dict(self.item, product="procurement")
        accepted = self.verify(self.encoded(item), "procurement")
        self.assertEqual(accepted.product, "procurement")

    def test_synthetic_invalid_json_retains_no_raw_document(self):
        self.denied(b'{"holder":"' + CANARY.encode() + b'",', "Malformed entitlement document")

    def test_invalid_json_with_unicode_string_retains_no_document(self):
        self.denied(('{"holder":"日本語' + CANARY + '",').encode(), "Malformed entitlement document")

    def test_invalid_utf8_retains_no_raw_bytes(self):
        self.denied(b'{"holder":"' + CANARY.encode() + b'\xff"}', "Malformed entitlement document")

    def test_utf8_truncated_sequence_retains_no_bytes(self):
        self.denied(b'{"holder":"' + CANARY.encode() + b'\xe2', "Malformed entitlement document")

    def test_corrupt_utf8_with_nested_secret_is_redacted(self):
        self.denied(CANARY.encode() + b'\xfe', "Malformed entitlement document")

    def test_invalid_issued_timestamp_no_strptime_exception(self):
        self.denied(self.encoded(dict(self.item, issued_at="2026-13-01T00:00:00Z")),
                    "Invalid issued_at UTC timestamp")

    def test_invalid_not_before_timestamp_no_strptime_exception(self):
        self.denied(self.encoded(dict(self.item, not_before="2026-11-33T00:00:00Z")),
                    "Invalid not_before UTC timestamp")

    def test_invalid_expiry_timestamp_no_strptime_exception(self):
        self.denied(self.encoded(dict(self.item, expires_at="2026-02-30T00:00:00Z")),
                    "Invalid expires_at UTC timestamp")

    def test_tampered_grant_signature_fails_without_crypto_exception(self):
        data = self.encoded()
        item = json.loads(data)
        item["holder"] = CANARY
        self.denied(json.dumps(item).encode(), "Entitlement signature failed verification")

    def test_tampered_procurement_signature_fails_without_crypto_exception(self):
        data = self.encoded(dict(self.item, product="procurement"))
        item = json.loads(data)
        item["holder"] = CANARY
        self.denied(json.dumps(item).encode(), "Entitlement signature failed verification", product="procurement")

    def test_wrong_ed25519_signer_rejected_without_crypto_cause(self):
        alt = Ed25519PrivateKey.generate()
        self.denied(self.encoded(signer=alt), "Entitlement signature failed verification")

    def test_base64_decode_error_does_not_expose_nested_private_cause(self):
        document = self.encoded()
        with patch.object(ent.base64, "urlsafe_b64decode", side_effect=binascii.Error(CANARY)):
            self.denied(document, "Invalid entitlement signature encoding")

    def test_crypto_public_key_error_does_not_expose_private_cause(self):
        document = self.encoded()
        with patch.object(ent.Ed25519PublicKey, "from_public_bytes", side_effect=ValueError(CANARY)):
            self.denied(document, "Entitlement signature failed verification")

    def test_no_trusted_authority_remains_fail_closed(self):
        with self.assertRaises(ent.EntitlementError) as caught:
            self.verify(self.encoded(), keys={})
        self.clean(caught.exception, "Premium entitlements are not activated in this pre-release build")

    def test_wrong_product_fails_even_if_signature_valid(self):
        self.denied(self.encoded(), "Entitlement schema or product does not match", product="procurement")

    def test_expired_license_fails(self):
        self.denied(self.encoded(dict(self.item, expires_at="2026-11-11T00:00:00Z")),
                    "Entitlement is not yet valid or has expired")

    def test_nan_json_is_never_accepted(self):
        raw = self.encoded().replace(b'"Synthetic Customer"', b'NaN')
        self.denied(raw, "Nonfinite entitlement field")

    def test_duplicate_json_field_never_accepted(self):
        raw = self.encoded().replace(b'"holder":', b'"holder":"duplicate","holder":')
        self.denied(raw, "Duplicate entitlement field")

    def test_programming_errors_still_propagate(self):
        with patch.object(ent.json, "loads", side_effect=TypeError("programming fault")):
            with self.assertRaisesRegex(TypeError, "programming fault"):
                self.verify(self.encoded())

    def test_read_once_and_no_console_on_sensitive_failure(self):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(ent, "_read_signed_entitlement", return_value=b'{"holder":"' + CANARY.encode() + b'",') as reader:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                with self.assertRaises(ent.EntitlementError) as caught:
                    ent.verify_license("synthetic.fvslicense", "grants", trusted_keys=self.keys, now=NOW)
            reader.assert_called_once_with("synthetic.fvslicense")
        self.clean(caught.exception, "Malformed entitlement document")
        self.assertEqual((out.getvalue(), err.getvalue()), ("", ""))


if __name__ == "__main__":
    unittest.main()
