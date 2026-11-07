"""R249: unexpected premium review evidence faults must revoke every actionable field.

Only synthetic report names and callback results are used; no customer data.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch
import sys

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
from fvs_suite.review_queue_load import ReviewQueue


class QueueFailureCustodyR249Tests(unittest.TestCase):
    def setUp(self):
        self.path = Path("synthetic-premium.csv")
        self.batch = object()
        self.queue = ReviewQueue()
        self.identity = patch(
            "fvs_suite.review_queue_load.journal_snapshot_identity",
            return_value="sha256:synthetic",
        )
        self.digest = self.identity.start()
        self.addCleanup(self.identity.stop)
        self.queue.load(self.path, "grants", lambda *_: self.batch, lambda *_: {})

    def check_cleared(self):
        self.assertIsNone(self.queue.batch)
        self.assertIsNone(self.queue.report_path)
        self.assertIsNone(self.queue.journal)
        self.assertIsNone(self.queue.journal_identity)

    def _raise(self, error):
        def broken(*_args):
            raise error
        return broken

    def test_valid_source_and_journal_remain_selected(self):
        self.assertIs(self.queue.verify_current("grants", lambda *_: self.batch,
                                                lambda *_: {}), self.batch)
        self.assertIs(self.queue.batch, self.batch)
        self.assertEqual(self.queue.report_path, self.path)
        self.assertEqual(self.queue.journal_identity, "sha256:synthetic")

    def test_read_cases_runtime_error_revokes(self):
        with self.assertRaises(RuntimeError):
            self.queue.verify_current("grants", self._raise(RuntimeError("PRIVATE_PATH")),
                                      lambda *_: {})
        self.check_cleared()

    def test_read_cases_type_error_revokes(self):
        with self.assertRaises(TypeError):
            self.queue.verify_current("grants", self._raise(TypeError("PRIVATE_PATH")),
                                      lambda *_: {})
        self.check_cleared()

    def test_read_cases_lookup_error_revokes(self):
        with self.assertRaises(LookupError):
            self.queue.verify_current("grants", self._raise(LookupError("PRIVATE_PATH")),
                                      lambda *_: {})
        self.check_cleared()

    def test_latest_states_runtime_error_revokes(self):
        with self.assertRaises(RuntimeError):
            self.queue.verify_current("grants", lambda *_: self.batch,
                                      self._raise(RuntimeError("JOURNAL_INTERNAL")))
        self.check_cleared()

    def test_latest_states_type_error_revokes(self):
        with self.assertRaises(TypeError):
            self.queue.verify_current("grants", lambda *_: self.batch,
                                      self._raise(TypeError("JOURNAL_INTERNAL")))
        self.check_cleared()

    def test_identity_first_read_fails_revokes(self):
        self.digest.side_effect = RuntimeError("SECRET_JOURNAL")
        with self.assertRaises(RuntimeError):
            self.queue.verify_current("grants", lambda *_: self.batch, lambda *_: {})
        self.check_cleared()

    def test_identity_second_read_fails_revokes(self):
        self.digest.side_effect = ["sha256:synthetic", RuntimeError("SECRET_JOURNAL")]
        with self.assertRaises(RuntimeError):
            self.queue.verify_current("grants", lambda *_: self.batch, lambda *_: {})
        self.check_cleared()

    def test_missing_selected_field_revokes_all_other_fields(self):
        self.queue.journal = None
        with self.assertRaises(ValueError):
            self.queue.verify_current("grants", lambda *_: self.batch, lambda *_: {})
        self.check_cleared()

    def test_no_current_batch_revokes_path_and_journal(self):
        self.queue.batch = None
        with self.assertRaises(ValueError):
            self.queue.verify_current("grants", lambda *_: self.batch, lambda *_: {})
        self.check_cleared()

    def test_wrong_product_revokes(self):
        with self.assertRaises(ValueError):
            self.queue.verify_current("other", lambda *_: self.batch, lambda *_: {})
        self.check_cleared()

    def test_missing_batch_revokes(self):
        with self.assertRaises(ValueError):
            self.queue.verify_current("grants", lambda *_: None, lambda *_: {})
        self.check_cleared()

    def test_changed_batch_revokes(self):
        with self.assertRaises(ValueError):
            self.queue.verify_current("grants", lambda *_: object(), lambda *_: {})
        self.check_cleared()

    def test_changed_journal_prior_to_read_revokes(self):
        self.digest.return_value = "sha256:changed"
        with self.assertRaises(ValueError):
            self.queue.verify_current("grants", lambda *_: self.batch, lambda *_: {})
        self.check_cleared()

    def test_changed_journal_during_read_revokes(self):
        self.digest.side_effect = ["sha256:synthetic", "sha256:changed"]
        with self.assertRaises(ValueError):
            self.queue.verify_current("grants", lambda *_: self.batch, lambda *_: {})
        self.check_cleared()

    def test_keyboard_interrupt_revokes_without_swallowing(self):
        with self.assertRaises(KeyboardInterrupt):
            self.queue.verify_current("grants", self._raise(KeyboardInterrupt()), lambda *_: {})
        self.check_cleared()

    def test_system_exit_revokes_without_swallowing(self):
        with self.assertRaises(SystemExit):
            self.queue.verify_current("grants", self._raise(SystemExit()), lambda *_: {})
        self.check_cleared()


if __name__ == "__main__":
    unittest.main()
