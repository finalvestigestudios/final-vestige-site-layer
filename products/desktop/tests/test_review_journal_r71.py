"""Synthetic R71 premium journal custody tests; never use customer records."""
from __future__ import annotations
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from fvs_suite.review_identity import journal_snapshot_identity
from fvs_suite.review_queue_load import ReviewQueue

class JournalSnapshotR71(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r71-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.report = self.root / "report.csv"
        self.journal = self.root / "report.review.jsonl"
        self.batch = ("grants", "a" * 64)
        self.queue = ReviewQueue()
        self.cases = Mock(return_value=self.batch)
        self.states = Mock(return_value={})

    def load(self): self.queue.load(self.report, "grants", self.cases, self.states)
    def check(self): return self.queue.verify_current("grants", self.cases, self.states)
    def assert_cleared(self):
        self.assertIsNone(self.queue.batch)
        self.assertIsNone(self.queue.report_path)
        self.assertIsNone(self.queue.journal)
        self.assertIsNone(self.queue.journal_identity)

    def test_missing_is_distinct_from_empty(self):
        self.assertEqual(journal_snapshot_identity(self.journal), "absent")
        self.journal.write_bytes(b"")
        self.assertTrue(journal_snapshot_identity(self.journal).startswith("sha256:"))
        self.assertNotEqual(journal_snapshot_identity(self.journal), "absent")

    def test_deterministic_identity_and_actual_byte_changes(self):
        self.journal.write_bytes(b'{"event":1}\n')
        a = journal_snapshot_identity(self.journal)
        self.assertEqual(a, journal_snapshot_identity(self.journal))
        self.journal.write_bytes(b'{"event":2}\n')
        self.assertNotEqual(a, journal_snapshot_identity(self.journal))

    def test_valid_unmodified_selection(self):
        self.load()
        self.assertEqual(self.queue.journal_identity, "absent")
        self.assertEqual(self.check(), self.batch)
        self.states.assert_called_with(self.journal, self.batch)

    def test_existing_valid_journal_can_be_selected(self):
        self.journal.write_bytes(b'one\n')
        self.load()
        self.assertTrue(self.queue.journal_identity.startswith("sha256:"))
        self.assertEqual(self.check(), self.batch)

    def test_new_event_after_open_is_rejected(self):
        self.journal.write_bytes(b'one\n')
        self.load()
        self.states.reset_mock()
        self.journal.write_bytes(b'one\ntwo\n')
        with self.assertRaisesRegex(ValueError, "changed since opening"):
            self.check()
        self.states.assert_not_called()
        self.assert_cleared()

    def test_file_created_after_open_is_rejected(self):
        self.load()
        self.journal.write_bytes(b'new\n')
        with self.assertRaises(ValueError): self.check()
        self.assert_cleared()

    def test_file_removed_after_open_is_rejected(self):
        self.journal.write_bytes(b'old\n')
        self.load()
        self.journal.unlink()
        with self.assertRaises(ValueError): self.check()
        self.assert_cleared()

    def test_same_length_rewrite_is_rejected(self):
        self.journal.write_bytes(b'AAAA\n')
        self.load()
        self.journal.write_bytes(b'BBBB\n')
        with self.assertRaises(ValueError): self.check()
        self.assert_cleared()

    def test_change_during_load_cannot_commit_selection(self):
        def mutate(*_): self.journal.write_bytes(b'new\n')
        self.states.side_effect = mutate
        with self.assertRaisesRegex(ValueError, "changed while opening"):
            self.load()
        self.assert_cleared()

    def test_change_during_verification_is_rejected(self):
        self.load()
        self.states.side_effect = lambda *_: self.journal.write_bytes(b'changed\n')
        with self.assertRaisesRegex(ValueError, "changed during validation"):
            self.check()
        self.assert_cleared()

    def test_after_own_review_queue_must_reload(self):
        self.load()
        self.journal.write_bytes(b'human-reviewed\n')
        with self.assertRaises(ValueError): self.check()
        self.load()
        self.assertEqual(self.check(), self.batch)

    def test_swapped_journal_rejected(self):
        self.journal.write_bytes(b'first\n')
        self.load()
        substitute = self.root / 'substitute'
        substitute.write_bytes(b'second\n')
        os.replace(substitute, self.journal)
        with self.assertRaises(ValueError): self.check()
        self.assert_cleared()

    def test_symlink_is_rejected(self):
        target = self.root / "target"
        target.write_bytes(b'x\n')
        try: self.journal.symlink_to(target)
        except (OSError, NotImplementedError): self.skipTest("symlink unsupported")
        with self.assertRaises(ValueError): self.load()
        self.assert_cleared()

    def test_hardlink_is_rejected(self):
        self.journal.write_bytes(b'x\n')
        try: os.link(self.journal, self.root / "alias")
        except (OSError, NotImplementedError): self.skipTest("hardlink unsupported")
        with self.assertRaises(ValueError): self.load()
        self.assert_cleared()

    def test_directory_in_journal_path_rejected(self):
        self.journal.mkdir()
        with self.assertRaises(ValueError): self.load()
        self.assert_cleared()

    def test_report_changes_first_discard_journal_selection(self):
        self.load()
        self.cases.return_value = ("grants", "b"*64)
        with self.assertRaises(ValueError): self.check()
        self.assert_cleared()

    def test_privacy_never_interpolates_financial_source(self):
        private = "PRIVATE-INVOICE-4455\x1b[31m"
        self.journal.write_bytes(private.encode())
        self.load()
        self.journal.write_bytes(b'different')
        with self.assertRaises(ValueError) as error: self.check()
        self.assertNotIn(private, str(error.exception))
        self.assertNotIn(str(self.journal), str(error.exception))
        self.assert_cleared()

    def test_failed_validator_clears_preexisting_queue(self):
        self.load()
        self.states.side_effect = ValueError("broken journal")
        with self.assertRaises(ValueError): self.check()
        self.assert_cleared()

    def test_no_disk_changes_on_unmodified_validations(self):
        self.journal.write_bytes(b'fixed\n')
        before = self.journal.read_bytes()
        self.load()
        self.check()
        self.assertEqual(before, self.journal.read_bytes())
        self.assertEqual({p.name for p in self.root.iterdir()}, {self.journal.name})

if __name__ == '__main__': unittest.main()
