"""R51 both-premium end-to-end chronology tests; require a full repository checkout."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from fvs_suite import exception_review


class PremiumChronologyIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r51-review-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.report = self.root / "source.csv"
        self.journal = self.root / "review.jsonl"

    def _setup(self, product):
        self.report.write_text(
            "id,status\nclaim-1,variance\n" if product == "grants"
            else "po,line,status\nP-1,1,quantity_variance\n",
            encoding="utf-8",
        )
        return exception_review.read_cases(self.report, product)

    def _record(self, batch):
        return exception_review.append_review(
            self.report, batch.product, self.journal,
            case_id=batch.cases[0].case_id,
            expected_report_sha256=batch.report_sha256,
            reviewer="Synthetic Human Reviewer", decision="needs_evidence",
            rationale="A supporting financial record requires human validation.",
        )

    def _rewrite_time(self, position: int, timestamp: str):
        events = [json.loads(line) for line in self.journal.read_text(encoding="utf-8").splitlines()]
        event = events[position]
        event["created_utc"] = timestamp
        event["event_hash"] = exception_review._hex_hash(
            exception_review._json({name: event[name] for name in exception_review.FIELDS})
        )
        # This test deliberately recalculates an *unkeyed* SHA-256 chain, showing
        # why chain validity alone does not establish chronology or authorship.
        self.journal.write_bytes(b"".join(exception_review._json(item) + b"\n" for item in events))

    def test_both_premium_journals_reject_backdated_hash_valid_record(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._setup(product)
                self._record(batch)
                self._record(batch)
                self._rewrite_time(1, "2000-01-01T00:00:00+00:00")
                with self.assertRaisesRegex(ValueError, "chronological"):
                    exception_review.read_journal(self.journal, batch)
                self.journal.unlink()

    def test_both_premium_apps_refuse_clock_rollback_without_new_decision(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._setup(product)
                self._record(batch)
                self._rewrite_time(0, "2099-01-01T00:00:00+00:00")
                original = self.journal.read_bytes()
                with self.assertRaisesRegex(ValueError, "predates"):
                    self._record(batch)
                self.assertEqual(self.journal.read_bytes(), original)
                self.assertFalse(Path(str(self.journal) + ".lock").exists())
                self.journal.unlink()

    def test_same_second_multiple_human_reviews_still_valid(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._setup(product)
                first = self._record(batch)
                second = self._record(batch)
                self.assertEqual(exception_review.read_journal(self.journal, batch), [first, second])
                self.journal.unlink()

    def test_export_blocks_backdated_hash_valid_review_history(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._setup(product)
                self._record(batch)
                self._record(batch)
                self._rewrite_time(1, "2000-01-01T00:00:00+00:00")
                with self.assertRaises(ValueError):
                    exception_review.export_register(self.report, product, self.journal, self.root)
                self.journal.unlink()


if __name__ == "__main__":
    unittest.main()
