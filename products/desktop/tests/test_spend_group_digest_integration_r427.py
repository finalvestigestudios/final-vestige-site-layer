"""R427 real SpendMap grouping tests: SHA-bound full physical-row membership.

Synthetic CSV rows only. No claim that supplied SHA was computed from records.
These execute the actual shared summarize_spend engine, not a model.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from hashlib import sha256
import unittest

from fvs_suite.spend_analysis import _vendor_month_line_digest, summarize_spend

SOURCE = sha256(b"R427 synthetic CSV snapshot").hexdigest()


def records():
    return [
        {"row": "4", "vendor": "ACME", "date": "2026-11-02",
         "amount": "15.00", "category": "Equipment"},
        {"row": "2", "vendor": "ACME", "date": "2026-11-01",
         "amount": "10.00", "category": "Supplies"},
    ]


def run(rows):
    return summarize_spend(
        rows, normalize_vendor=str.upper,
        parse_date=date.fromisoformat, parse_money=Decimal,
        format_money=lambda value: format(value, "f"), source_sha256=SOURCE)


class SpendGroupDigestIntegrationR427(unittest.TestCase):
    def test_real_group_fingerprint_matches_helper(self):
        report = run(records())
        expected = _vendor_month_line_digest(SOURCE, "ACME", "2026-11", [2, 4])
        self.assertEqual({r["vendor_month_evidence_sha256"] for r in report}, {expected})

    def test_real_group_evidence_not_truncated_by_categories(self):
        report = run(records())
        for row in report:
            self.assertEqual(row["vendor_month_evidence_count"], "2")
            self.assertEqual(row["vendor_month_evidence_rows"], "2;4")
            self.assertEqual(row["vendor_month_evidence_omitted"], "0")

    def test_real_group_evidence_is_input_permutation_invariant(self):
        original = run(records())
        reversed_rows = run(list(reversed(records())))
        self.assertEqual(original, reversed_rows)

    def test_real_group_evidence_changes_with_source_line(self):
        first = run(records())
        moved = records()
        moved[0]["row"] = "5"
        second = run(moved)
        self.assertNotEqual(first[0]["vendor_month_evidence_sha256"],
                            second[0]["vendor_month_evidence_sha256"])

    def test_real_historical_year_keeps_native_strftime_month(self):
        # Some Python platforms emit "1-11", others "0001-11".
        # Do not reject a legitimate imported historical calendar date.
        historical = records()
        historical[0]["date"] = "0001-11-02"
        historical[1]["date"] = "0001-11-01"
        result = run(historical)
        expected_month = date(1, 11, 1).strftime("%Y-%m")
        self.assertEqual({r["month"] for r in result}, {expected_month})
        self.assertEqual(
            {r["vendor_month_evidence_sha256"] for r in result},
            {_vendor_month_line_digest(SOURCE, "ACME", expected_month, [2, 4])})

    def test_direct_digest_rejects_forged_vendor(self):
        class Forged(str):
            def encode(self, *_args, **_kwargs):
                raise AssertionError("PRIVATE_VENDOR")
        with self.assertRaisesRegex(ValueError, "source-group"):
            _vendor_month_line_digest(SOURCE, Forged("ACME"), "2026-11", [2])

    def test_direct_digest_rejects_forged_month(self):
        class Forged(str):
            def encode(self, *_args, **_kwargs):
                raise AssertionError("PRIVATE_MONTH")
        with self.assertRaisesRegex(ValueError, "source-group"):
            _vendor_month_line_digest(SOURCE, "ACME", Forged("2026-11"), [2])

    def test_direct_digest_rejects_noncanonical_source_membership(self):
        for lines in ([4, 2], [2, 2], [2, True], ["2"], []):
            with self.subTest(lines=lines), self.assertRaisesRegex(ValueError, "source-group"):
                _vendor_month_line_digest(SOURCE, "ACME", "2026-11", lines)

    def test_valid_group_hash_still_domain_separates_vendor_month_and_source(self):
        baseline = _vendor_month_line_digest(SOURCE, "ACME", "2026-11", [2])
        self.assertNotEqual(baseline, _vendor_month_line_digest(SOURCE, "OTHER", "2026-11", [2]))
        self.assertNotEqual(baseline, _vendor_month_line_digest(SOURCE, "ACME", "2026-12", [2]))
        self.assertNotEqual(baseline, _vendor_month_line_digest(sha256(b"other").hexdigest(),
                                                              "ACME", "2026-11", [2]))


if __name__ == "__main__":
    unittest.main()
