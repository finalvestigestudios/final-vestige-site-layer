"""R61 SpendMap Lite provenance binding; synthetic, no customer data."""
from __future__ import annotations

import re
import unittest
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from fvs_suite.spend_analysis import summarize_spend

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def _summary(rows: list[dict[str, str]], digest: str = DIGEST_A):
    return summarize_spend(
        rows, normalize_vendor=lambda s: re.sub(r"[^A-Z0-9]+", "", s.upper()),
        parse_date=date.fromisoformat,
        parse_money=lambda s: Decimal(s).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        format_money=lambda d: format(d.quantize(Decimal("0.01")), ".2f"),
        source_sha256=digest,
    )


def _row(n=2, *, vendor="Acme", month="2026-01-01", amount="1.00", category="Part"):
    return {"row": str(n), "vendor": vendor, "date": month, "amount": amount,
            "category": category}


class SpendSourceSnapshotR61(unittest.TestCase):
    def test_source_hash_follows_every_bucket(self):
        rows = [_row(2), _row(3, category="Travel"),
                _row(4, vendor="OTHER", month="2026-02-02")]
        report = _summary(rows)
        self.assertEqual(len(report), 3)
        self.assertEqual({row["source_sha256"] for row in report}, {DIGEST_A})
        self.assertEqual([row["source_rows"] for row in report], ["2", "3", "4"])

    def test_different_sources_do_not_reuse_identity(self):
        rows = [_row()]
        left, right = _summary(rows, DIGEST_A), _summary(rows, DIGEST_B)
        self.assertEqual(left[0]["amount"], right[0]["amount"])
        self.assertNotEqual(left[0]["source_sha256"], right[0]["source_sha256"])
        # R154 binds complete vendor/month membership to the source hash too.
        # Both source identity fields MUST change; the actual financial and
        # review values remain equal for otherwise identical imported rows.
        self.assertNotEqual(left[0]["vendor_month_evidence_sha256"],
                            right[0]["vendor_month_evidence_sha256"])
        identity_fields = {"source_sha256", "vendor_month_evidence_sha256"}
        self.assertEqual({k: v for k, v in left[0].items() if k not in identity_fields},
                         {k: v for k, v in right[0].items() if k not in identity_fields})

    def test_source_digest_is_not_rehashed_or_reformatted(self):
        digest = "0123456789abcdef" * 4
        self.assertEqual(_summary([_row()], digest)[0]["source_sha256"], digest)

    def test_empty_input_preserves_empty_report(self):
        self.assertEqual(_summary([]), [])

    def test_wrong_hash_types_are_rejected_before_work(self):
        for bad in (None, 123, False, b"a" * 64, {}, [], object()):
            with self.subTest(bad=repr(bad)), self.assertRaisesRegex(ValueError, "SHA-256"):
                _summary([_row()], bad)

    def test_wrong_hash_lengths_and_noncanonical_forms_rejected(self):
        for bad in ("", "a" * 63, "a" * 65, "A" * 64, "z" * 64,
                    " a" + "a" * 63, "a" * 64 + "\n", "0" * 63 + "é",
                    "0" * 63 + " ", "0" * 63 + "\x00"):
            with self.subTest(bad=repr(bad)), self.assertRaisesRegex(ValueError, "SHA-256"):
                _summary([], bad)

    def test_required_digest_cannot_be_omitted(self):
        with self.assertRaises(TypeError):
            summarize_spend([_row()], normalize_vendor=lambda x: x,
                            parse_date=date.fromisoformat,
                            parse_money=Decimal, format_money=str)

    def test_collision_warning_and_exact_money_unchanged(self):
        report = _summary([_row(2, vendor="A-CME", amount="0.10"),
                           _row(3, vendor="ACME", amount="0.20")])
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["amount"], "0.30")
        self.assertEqual(report[0]["source_rows"], "2;3")
        self.assertEqual(report[0]["flag"], "normalized_vendor_collision_review")
        self.assertEqual(report[0]["source_sha256"], DIGEST_A)

    def test_spike_baseline_and_identity_are_independent(self):
        records = [_row(2 + month, month=f"2026-{month+1:02d}-01",
                        amount=("10.00" if month < 3 else "20.00"))
                   for month in range(4)]
        report = _summary(records, DIGEST_B)
        self.assertEqual([item["flag"] for item in report], ["", "", "", "review_spike"])
        self.assertEqual(report[-1]["baseline_median"], "10.00")
        self.assertEqual(report[-1]["source_sha256"], DIGEST_B)

    def test_repeated_execution_is_deterministic(self):
        data = [_row(2, amount="10.05"), _row(4, amount="-0.05")]
        self.assertEqual(_summary(data), _summary(data))

    def test_source_digest_does_not_expose_original_records(self):
        report = _summary([_row(2, vendor="Acme Secret", amount="123.45")])
        digest = report[0]["source_sha256"]
        self.assertRegex(digest, r"\A[0-9a-f]{64}\Z")
        self.assertNotIn("Secret", digest)
        self.assertNotIn("123.45", digest)


if __name__ == "__main__":
    unittest.main()
