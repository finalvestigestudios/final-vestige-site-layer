"""Real premium review/report/export integration with custody-aware writer lock."""
from __future__ import annotations

from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite import exception_review
from synthetic_windows_fs_r104 import altered_lstat


class PremiumWriterIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.journal = self.root / "human-decisions.jsonl"
        self.lock = Path(str(self.journal) + ".lock")

    def _report(self, product):
        report = self.root / "review.csv"
        if product == "grants":
            report.write_text("id,status\nclaim-001,variance\nclaim-002,matched\n", encoding="utf-8")
        else:
            report.write_text("po,line,status\nP-1,1,quantity_variance\nP-2,2,matched\n", encoding="utf-8")
        batch = exception_review.read_cases(report, product)
        self.assertEqual(len(batch.cases), 1)
        return report, batch

    def _append(self, report, batch):
        return exception_review.append_review(
            report, batch.product, self.journal, case_id=batch.cases[0].case_id,
            expected_report_sha256=batch.report_sha256,
            reviewer="Example Human Reviewer", decision="needs_evidence",
            rationale="Supporting documentation required.")

    def test_grant_review_and_atomic_register_export(self):
        self._review_and_export("grants")

    def test_procurement_review_and_atomic_register_export(self):
        self._review_and_export("procurement")

    def _review_and_export(self, product):
        report, batch = self._report(product)
        original_report = report.read_bytes()
        event = self._append(report, batch)
        self.assertFalse(self.lock.exists())
        history = exception_review.read_journal(self.journal, batch)
        self.assertEqual(history, [event])
        self.assertEqual(history[0]["decision"], "needs_evidence")
        result = exception_review.export_register(report, product, self.journal, self.root)
        self.assertTrue(result.is_file())
        content = result.read_text(encoding="utf-8-sig")
        self.assertIn("needs_evidence", content)
        self.assertIn(batch.report_sha256, content)
        self.assertEqual(report.read_bytes(), original_report)

    def test_preexisting_writer_lock_never_modifies_report_or_journal(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                report, batch = self._report(product)
                old = report.read_bytes()
                self.lock.write_bytes(b"another writer\n")
                with self.assertRaises(ValueError):
                    self._append(report, batch)
                self.assertEqual(report.read_bytes(), old)
                self.assertFalse(self.journal.exists())
                self.assertEqual(self.lock.read_bytes(), b"another writer\n")
                self.lock.unlink()

    def test_lost_lock_during_revalidation_blocks_journal_append(self):
        report, batch = self._report("grants")
        real_read_cases = exception_review.read_cases
        calls = 0


        state = {"active": False}
        real_lstat = os.lstat

        def lose_lock(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:  # Just after the descriptor-held append begins.
                if os.name == "nt":
                    # A held lock cannot always be unlinked on Windows.
                    # Model the path-identity attack rather than skipping it.
                    state["active"] = True
                else:
                    self.lock.unlink()
                    self.lock.write_bytes(b"competitor owns lock\\n")
            return real_read_cases(*args, **kwargs)

        observer = altered_lstat(self.lock, state, real_lstat)
        with patch("fvs_suite.review_lock.os.lstat", side_effect=observer):
            with patch.object(exception_review, "read_cases", side_effect=lose_lock):
                with self.assertRaises(ValueError):
                    self._append(report, batch)
        if os.name == "nt":
            # Synthetic metadata drift leaves an original lock for inspection.
            self.assertTrue(self.lock.read_bytes().startswith(b"pid="))
        else:
            self.assertEqual(self.lock.read_bytes(), b"competitor owns lock\\n")
        self.assertFalse(self.journal.exists() and self.journal.read_bytes().strip())


if __name__ == "__main__":
    unittest.main()
