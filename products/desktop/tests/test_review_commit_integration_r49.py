"""R49 integration: premium human review must confirm its on-disk commit."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite import exception_review


class PremiumCommitReadbackIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.source = self.folder / "source.csv"
        self.journal = self.folder / "human-decisions.jsonl"
        self.lock = Path(str(self.journal) + ".lock")

    def _setup_batch(self, product):
        if product == "grants":
            self.source.write_bytes(b"id,status\nclaim-001,variance\nclaim-002,matched\n")
        else:
            self.source.write_bytes(b"po,line,status\nP-1,1,quantity_variance\nP-2,2,matched\n")
        batch = exception_review.read_cases(self.source, product)
        self.assertEqual(len(batch.cases), 1)
        return batch

    def _review(self, batch, decision="needs_evidence"):
        return exception_review.append_review(
            self.source, batch.product, self.journal,
            case_id=batch.cases[0].case_id,
            expected_report_sha256=batch.report_sha256,
            reviewer="Synthetic Human Reviewer", decision=decision,
            rationale="Synthetic documentation required for this case.",
        )

    def test_both_premium_products_acknowledge_only_verified_events(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._setup_batch(product)
                first = self._review(batch)
                second = self._review(batch, "escalated")
                self.assertEqual(exception_review.read_journal(self.journal, batch), [first, second])
                self.assertFalse(self.lock.exists())
                self.journal.unlink()

    def test_tampering_with_written_decision_blocks_acknowledgment(self):
        original = exception_review.append_verified_event
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._setup_batch(product)

                def corrupt_after_fsync(path, payload, limit, verify):
                    original(path, payload, limit, verify)
                    raw = Path(path).read_bytes()
                    self.assertIn(b'needs_evidence', raw)
                    Path(path).write_bytes(raw.replace(b'needs_evidence', b'needs_evidencf', 1))

                with patch.object(exception_review, "append_verified_event", side_effect=corrupt_after_fsync):
                    with self.assertRaises(ValueError):
                        self._review(batch)
                self.assertFalse(self.lock.exists())
                self.assertTrue(self.journal.exists())  # Preserve for human inspection.
                self.journal.unlink()

    def test_missing_append_is_not_reported_as_success(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._setup_batch(product)

                def phantom_write(path, payload, limit, verify):
                    verify()  # No journal bytes written despite apparent success.

                with patch.object(exception_review, "append_verified_event", side_effect=phantom_write):
                    with self.assertRaisesRegex(ValueError, "could not be confirmed"):
                        self._review(batch)
                self.assertFalse(self.lock.exists())
                self.assertFalse(self.journal.exists())

    def test_post_fsync_source_change_is_not_acknowledged(self):
        original = exception_review.append_verified_event
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                batch = self._setup_batch(product)

                def edit_source_after_fsync(path, payload, limit, verify):
                    original(path, payload, limit, verify)
                    self.source.write_bytes(self.source.read_bytes() + b"\n")

                with patch.object(exception_review, "append_verified_event", side_effect=edit_source_after_fsync):
                    with self.assertRaisesRegex(ValueError, "source changed"):
                        self._review(batch)
                self.assertFalse(self.lock.exists())
                self.journal.unlink()


if __name__ == "__main__":
    unittest.main()
