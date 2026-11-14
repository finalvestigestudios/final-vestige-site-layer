"""R426 real SpendMap summarizer/native digest custody integration tests.

Synthetic records only. The source SHA is supplied, not inferred from records;
these tests do not prove the caller's snapshot-to-record binding.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
import hashlib
import unittest

from fvs_suite.spend_analysis import summarize_spend, _vendor_month_line_digest


HASH_A = hashlib.sha256(b"synthetic-source-A").hexdigest()
HASH_B = hashlib.sha256(b"synthetic-source-B").hexdigest()


def rows():
    return [{"row": "2", "vendor": "ACME", "date": "2026-11-01", "amount": "10.00",
             "category": "Supplies"}]


def summarize(source_digest, *, records=None, normalize_vendor=str.upper):
    return summarize_spend(
        rows() if records is None else records,
        normalize_vendor=normalize_vendor,
        parse_date=date.fromisoformat,
        parse_money=Decimal,
        format_money=lambda v: format(v, "f"),
        source_sha256=source_digest,
    )


class SpendSourceDigestIntegrationR426(unittest.TestCase):
    def test_native_sha_remains_exact_in_report(self):
        report = summarize(HASH_A)
        self.assertEqual(len(report), 1)
        self.assertIs(type(report[0]["source_sha256"]), str)
        self.assertEqual(report[0]["source_sha256"], HASH_A)

    def test_real_single_vendor_month_digest_is_deterministic(self):
        self.assertEqual(summarize(HASH_A), summarize(HASH_A))
        self.assertEqual(summarize(HASH_A)[0]["vendor_month_evidence_sha256"],
                         _vendor_month_line_digest(HASH_A, "ACME", "2026-11", [2]))

    def test_source_digest_changes_membership_hash_not_money(self):
        a = summarize(HASH_A)[0]
        b = summarize(HASH_B)[0]
        self.assertNotEqual(a["vendor_month_evidence_sha256"], b["vendor_month_evidence_sha256"])
        self.assertEqual(a["amount"], b["amount"])
        self.assertEqual(a["source_rows"], b["source_rows"])

    def test_invalid_sha_denied_before_vendor_callback(self):
        def unsafe(_value):
            self.fail("Vendor callback should not run for invalid digest")
        with self.assertRaisesRegex(ValueError, "Source snapshot SHA-256"):
            summarize("g" * 64, normalize_vendor=unsafe)

    def test_spoofed_encode_cannot_influence_report(self):
        class Spoof(str):
            def encode(self, *args, **kwargs):
                raise AssertionError("PRIVATE_CUSTOMER digest encode invoked")
        with self.assertRaisesRegex(ValueError, "Source snapshot SHA-256") as denial:
            summarize(Spoof(HASH_A))
        self.assertNotIn("PRIVATE_CUSTOMER", str(denial.exception))

    def test_spoofed_comparison_cannot_influence_report(self):
        class Spoof(str):
            def __eq__(self, other):
                raise AssertionError("PRIVATE_CUSTOMER digest equality invoked")
        with self.assertRaisesRegex(ValueError, "Source snapshot SHA-256"):
            summarize(Spoof(HASH_A))

    def test_digest_helper_cannot_accept_forged_encode(self):
        class Spoof(str):
            def encode(self, *args, **kwargs):
                return b"b" * 64
        with self.assertRaisesRegex(ValueError, "Source snapshot SHA-256"):
            _vendor_month_line_digest(Spoof(HASH_A), "ACME", "2026-11", [2])

    def test_digest_helper_keeps_native_reference(self):
        self.assertEqual(_vendor_month_line_digest(HASH_A, "ACME", "2026-11", [2]),
                         _vendor_month_line_digest(HASH_A, "ACME", "2026-11", [2]))
        self.assertNotEqual(_vendor_month_line_digest(HASH_A, "ACME", "2026-11", [2]),
                            _vendor_month_line_digest(HASH_A, "ACME", "2026-11", [3]))


if __name__ == "__main__":
    unittest.main()
