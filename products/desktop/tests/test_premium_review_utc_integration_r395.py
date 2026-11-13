"""R395 both-premium journal replay tests; requires real full repository checkout.

Uses synthetic report rows and deliberately recomputed unkeyed journal hashes.
No auto-approval, customer data, network, or existing journal mutation.
"""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from fvs_suite import exception_review


class BothPremiumJournalTimestampCustody(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r395-review-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.report = self.root / "report.csv"
        self.journal = self.root / "review.jsonl"

    def setup_product(self, product):
        self.report.write_text(
            "id,status\nC-1,variance\n" if product == "grants"
            else "po,line,status\nP-1,1,quantity_variance\n",
            encoding="utf-8")
        batch = exception_review.read_cases(self.report, product)
        self.assertEqual(len(batch.cases), 1)
        return batch

    def save_hash_valid_event(self, batch, timestamp):
        case = batch.cases[0]
        payload = dict(
            schema=1, product=batch.product, report_sha256=batch.report_sha256,
            case_id=case.case_id, report_row=case.report_row, flags=case.flags,
            decision="needs_evidence", reviewer="Synthetic Reviewer",
            rationale="Human documentation must be reviewed.",
            created_utc=timestamp, previous_hash=exception_review.ZERO_HASH,
        )
        event = {**payload, "event_hash": exception_review._hex_hash(
            exception_review._json(payload))}
        self.journal.write_bytes(exception_review._json(event) + b"\n")
        return event

    def test_both_premium_apps_reject_ambiguous_separator_even_with_valid_sha_chain(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.setup_product(product)
                self.save_hash_valid_event(batch, "2026-11-13X05:01:02Z")
                before = self.journal.read_bytes()
                with self.assertRaisesRegex(ValueError, "invalid UTC timestamp") as caught:
                    exception_review.read_journal(self.journal, batch)
                self.assertIsNone(caught.exception.__context__)
                self.assertIsNone(caught.exception.__cause__)
                self.assertEqual(self.journal.read_bytes(), before)
                self.journal.unlink()

    def test_both_premium_apps_reject_truncated_fractional_precision(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.setup_product(product)
                self.save_hash_valid_event(batch, "2026-11-13T05:01:02.1234567Z")
                before = self.journal.read_bytes()
                with self.assertRaisesRegex(ValueError, "invalid UTC timestamp"):
                    exception_review.read_journal(self.journal, batch)
                self.assertEqual(self.journal.read_bytes(), before)
                self.journal.unlink()

    def test_both_premium_apps_accept_historical_unambiguous_utc(self):
        for product in ("grants", "procurement"):
            for ts in ("2026-11-13T05:01:02Z", "2026-11-13T05:01:02-00:00",
                       "2026-11-13T05:01:02.123456+00:00"):
                with self.subTest(product=product, ts=ts):
                    batch = self.setup_product(product)
                    event = self.save_hash_valid_event(batch, ts)
                    self.assertEqual(exception_review.read_journal(self.journal, batch), [event])
                    self.journal.unlink()

    def test_both_premium_apps_refuse_append_to_invalid_existing_history(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.setup_product(product)
                self.save_hash_valid_event(batch, "2026-11-13T05:01:02+00:00:00")
                original = self.journal.read_bytes()
                with self.assertRaises(ValueError):
                    exception_review.append_review(
                        self.report, product, self.journal,
                        case_id=batch.cases[0].case_id,
                        expected_report_sha256=batch.report_sha256,
                        reviewer="Synthetic Reviewer", decision="needs_evidence",
                        rationale="Requires an independent human review.")
                self.assertEqual(self.journal.read_bytes(), original)
                self.journal.unlink()

    def test_both_premium_register_exports_refuse_noncanonical_journal(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self.setup_product(product)
                self.save_hash_valid_event(batch, "20261113T050102Z")
                before = set(self.root.iterdir())
                with self.assertRaises(ValueError):
                    exception_review.export_register(self.report, product, self.journal, self.root)
                self.assertEqual(set(self.root.iterdir()), before)
                self.journal.unlink()


if __name__ == "__main__":
    unittest.main()
