"""R11: real cryptographic verification with ephemeral keys, never production credentials."""
import base64
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from fvs_suite import offline_entitlement as license

UTC = timezone.utc
NOW = datetime(2026, 10, 28, 12, 0, tzinfo=UTC)


class LicenseR11Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.key = Ed25519PrivateKey.generate()
        self.pub = self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)
        self.keys = {"fvs-release-r11": self.pub}
        self.item = {"schema": license.SCHEMA, "kid": "fvs-release-r11",
                     "product": "grants", "license_id": "license-100001",
                     "holder": "Synthetic Example Organization",
                     "issued_at": "2026-10-01T00:00:00Z",
                     "not_before": "2026-10-01T00:00:00Z",
                     "expires_at": "2027-10-01T00:00:00Z"}

    def write(self, item=None, sign=True):
        obj = dict(self.item if item is None else item)
        if sign:
            payload = license._canonical_payload(obj)
            obj["signature"] = base64.urlsafe_b64encode(self.key.sign(payload)).decode().rstrip("=")
        path = self.root / "grants.fvslicense"
        path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        return path

    def check(self, path, product="grants"):
        return license.verify_license(path, product, trusted_keys=self.keys, now=NOW)

    def test_valid_license_verified_ed25519(self):
        result = self.check(self.write())
        self.assertEqual(result.product, "grants")
        self.assertEqual(result.license_id, "license-100001")

    def test_no_trusted_keys_fails_closed(self):
        with self.assertRaisesRegex(license.EntitlementError, "not activated"):
            license.verify_license(self.write(), "grants", now=NOW)

    def test_wrong_product_rejected_even_with_valid_signature(self):
        with self.assertRaisesRegex(license.EntitlementError, "product does not match"):
            self.check(self.write(), product="procurement")

    def test_modified_signed_payload_rejected(self):
        path = self.write()
        obj = json.loads(path.read_text())
        obj["holder"] = "Attacker Name"
        path.write_text(json.dumps(obj))
        with self.assertRaisesRegex(license.EntitlementError, "signature failed"):
            self.check(path)

    def test_invalid_unknown_and_noncanonical_signatures(self):
        path = self.write()
        obj = json.loads(path.read_text())
        obj["signature"] = obj["signature"][:-1] + ("A" if obj["signature"][-1] != "A" else "B")
        path.write_text(json.dumps(obj))
        with self.assertRaises(license.EntitlementError):
            self.check(path)
        obj = json.loads(self.write().read_text())
        obj["kid"] = "unknown-key"
        path.write_text(json.dumps(obj))
        with self.assertRaises(license.EntitlementError):
            self.check(path)

    def test_duplicate_json_fields_rejected(self):
        path = self.write()
        raw = path.read_text()
        raw = raw.replace('"schema":', '"schema": "bad", "schema":', 1)
        path.write_text(raw)
        with self.assertRaisesRegex(license.EntitlementError, "Duplicate"):
            self.check(path)

    def test_not_yet_valid_and_expired(self):
        path = self.write()
        for date in (datetime(2026,9,30,tzinfo=UTC), datetime(2027,10,1,tzinfo=UTC)):
            with self.subTest(date=date), self.assertRaises(license.EntitlementError):
                license.verify_license(path, "grants", trusted_keys=self.keys, now=date)

    def test_invalid_utc_timestamp_rejected(self):
        for value in ("2026-10-01", "2026-10-01T00:00:00+00:00", "2026-02-30T00:00:00Z"):
            with self.subTest(value=value), self.assertRaises(license.EntitlementError):
                self.check(self.write({**self.item, "expires_at":value}))

    def test_invalid_validity_window_rejected(self):
        obj = {**self.item, "expires_at":"2039-10-01T00:00:00Z"}
        with self.assertRaisesRegex(license.EntitlementError, "validity window"):
            self.check(self.write(obj))

    def test_unsigned_and_malformed_license_rejected(self):
        with self.assertRaises(license.EntitlementError):
            self.check(self.write(sign=False))
        p = self.root / "bad.fvslicense"
        p.write_bytes(b"{not json")
        with self.assertRaises(license.EntitlementError):
            self.check(p)

    def test_oversized_and_symlink_rejected(self):
        p = self.root / "big.fvslicense"
        p.write_bytes(b"x"*(license.MAX_BYTES+1))
        with self.assertRaisesRegex(license.EntitlementError, "size limit"):
            self.check(p)
        q = self.root / "link.fvslicense"
        try: q.symlink_to(self.write())
        except (NotImplementedError, OSError): self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(license.EntitlementError, "regular"):
            self.check(q)

    def test_no_private_key_in_package(self):
        self.assertEqual(license.TRUSTED_PUBLIC_KEYS, {})
        self.assertNotIn("PRIVATE KEY", Path(license.__file__).read_text(encoding="utf-8"))

    def test_reject_naive_clock(self):
        path = self.write()
        with self.assertRaisesRegex(license.EntitlementError, "timezone-aware"):
            license.verify_license(path, "grants", trusted_keys=self.keys, now=datetime(2026,10,28))

    def test_wrong_public_key_fails(self):
        path = self.write()
        keys = {"fvs-release-r11":Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)}
        with self.assertRaisesRegex(license.EntitlementError, "signature failed"):
            license.verify_license(path, "grants", trusted_keys=keys, now=NOW)

    def test_both_premium_products_can_be_signed_but_not_interchanged(self):
        path = self.write({**self.item,"product":"procurement"})
        self.assertEqual(self.check(path, product="procurement").product,"procurement")
        with self.assertRaises(license.EntitlementError):
            self.check(path, product="grants")


if __name__ == "__main__":
    unittest.main()
