"""R124 synthetic dirty-inventory regressions; NEVER physical Win11 acceptance."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))

import windows11_manual_acceptance_r109 as qa
import windows11_witness_inventory_r124 as inventory
import test_windows11_witness_writer_r122 as fixture_module


class WitnessInventoryR124(unittest.TestCase):
    def setUp(self):
        # Reuse R122's complete source-bound synthetic six-app fixture. No
        # native Windows 11/real user observation is asserted by these tests.
        self.fixture = fixture_module.PrivateWitnessR122(
            methodName="test_one_observed_pass_updates_exact_check_only")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def matrix(self):
        return json.loads(self.fixture.review.read_text(encoding="utf-8"))

    def note(self):
        return self.fixture.path()

    def test_empty_inventory_accepts_zero_expected(self):
        self.assertEqual(inventory.verify_clean(self.matrix(), self.fixture.witnesses), 0)

    def test_clean_existing_inventory_accepts_next_record(self):
        self.fixture.one()
        self.assertEqual(inventory.verify_clean(self.matrix(), self.fixture.witnesses), 1)
        self.fixture.one(check=qa.FREE_CHECKS[1])
        self.assertEqual(inventory.verify_clean(self.matrix(), self.fixture.witnesses), 2)

    def test_orphan_other_app_prevents_first_record(self):
        extra = self.fixture.witnesses / "OtherApp--physical_tab_shift_tab.json"
        extra.write_text("unattributed synthetic note", encoding="utf-8")
        original = self.fixture.review.read_bytes()
        with self.assertRaises(qa.ReviewHold):
            self.fixture.one()
        self.assertEqual(self.fixture.review.read_bytes(), original)
        self.assertEqual(extra.read_text(), "unattributed synthetic note")
        self.assertFalse(self.note().exists())

    def test_orphan_other_check_prevents_next_record(self):
        self.fixture.one()
        second = qa.FREE_CHECKS[1]
        extra = self.fixture.witnesses / "other-leftover.json"
        extra.write_text("private synthetic leftover", encoding="utf-8")
        before = self.fixture.review.read_bytes()
        note_before = self.note().read_bytes()
        with self.assertRaises(qa.ReviewHold):
            self.fixture.one(check=second)
        self.assertEqual(self.fixture.review.read_bytes(), before)
        self.assertEqual(self.note().read_bytes(), note_before)
        self.assertFalse((self.fixture.witnesses / (
            self.fixture.app.removesuffix(".exe") + "--" + second + ".json")).exists())

    def test_directory_entry_prevents_record(self):
        extra = self.fixture.witnesses / "unexplained-subfolder"
        extra.mkdir()
        with self.assertRaises(qa.ReviewHold):
            self.fixture.one()
        self.assertTrue(extra.is_dir())

    def test_hidden_temp_entry_prevents_record(self):
        extra = self.fixture.witnesses / ".unfinished-r122.tmp"
        extra.write_text("not a witness", encoding="utf-8")
        with self.assertRaises(qa.ReviewHold):
            self.fixture.one()
        self.assertTrue(extra.exists())

    def test_unreferenced_same_target_prevents_record(self):
        self.note().write_text("previous unlinked witness", encoding="utf-8")
        with self.assertRaises(qa.ReviewHold):
            self.fixture.one()
        self.assertEqual(self.note().read_text(), "previous unlinked witness")

    def test_missing_referenced_note_raises_hold(self):
        self.fixture.one()
        original = self.matrix()
        self.note().unlink()
        with self.assertRaises(qa.ReviewHold):
            inventory.verify_clean(original, self.fixture.witnesses)

    def test_hardlinked_referenced_note_raises_hold(self):
        self.fixture.one()
        target = self.note()
        original = Path.lstat

        def pretend_hardlink(path):
            value = original(path)
            if path == target:
                return SimpleNamespace(st_mode=value.st_mode, st_nlink=2)
            return value

        with patch.object(Path, "lstat", pretend_hardlink):
            with self.assertRaises(qa.ReviewHold):
                inventory.verify_clean(self.matrix(), self.fixture.witnesses)

    def test_symlinked_referenced_note_raises_hold(self):
        self.fixture.one()
        target = self.note()
        original = Path.is_symlink

        def pretend_symlink(path):
            return path == target or original(path)

        with patch.object(Path, "is_symlink", pretend_symlink):
            with self.assertRaises(qa.ReviewHold):
                inventory.verify_clean(self.matrix(), self.fixture.witnesses)

    def test_injected_orphan_during_commit_rolls_back(self):
        # Simulate a noncooperating actor leaving an unexplained note after
        # the initial inventory check but before the matrix is committed.
        original = self.fixture.review.read_bytes()
        real = inventory.verify_clean
        calls = [0]
        stray = self.fixture.witnesses / "unlinked-race-leftover.json"

        def inject(matrix, folder):
            calls[0] += 1
            if calls[0] == 2:
                stray.write_text("synthetic interrupted write", encoding="utf-8")
            return real(matrix, folder)

        with patch.object(inventory, "verify_clean", side_effect=inject):
            with self.assertRaises(qa.ReviewHold):
                self.fixture.one()
        self.assertEqual(calls[0], 2)
        self.assertTrue(stray.exists())  # Never silently delete unknown evidence.
        self.assertEqual(self.fixture.review.read_bytes(), original)
        self.assertFalse(self.note().exists())
        self.assertFalse((self.fixture.root / "review.json.r122.lock").exists())

    def test_witness_and_review_folder_co_location_rejected(self):
        alternate = self.fixture.witnesses / "matrix.json"
        alternate.write_bytes(self.fixture.review.read_bytes())
        with self.assertRaises(qa.ReviewHold):
            self.fixture.one(review=alternate)
        self.assertEqual(alternate.read_bytes(), self.fixture.review.read_bytes())
        self.assertFalse(self.note().exists())
        self.assertFalse((self.fixture.witnesses / "matrix.json.r122.lock").exists())

    def test_cleared_orphan_allows_record_after_human_review(self):
        # Removal is explicitly simulated operator action, never automatic.
        extra = self.fixture.witnesses / "unexplained-note.json"
        extra.write_text("synthetic orphan", encoding="utf-8")
        with self.assertRaises(qa.ReviewHold):
            self.fixture.one()
        extra.unlink()
        self.fixture.one()
        self.assertEqual(inventory.verify_clean(self.matrix(), self.fixture.witnesses), 1)

    def test_inventory_does_not_mutate_existing_private_evidence(self):
        self.fixture.one()
        note_before = self.note().read_bytes()
        matrix_before = self.fixture.review.read_bytes()
        self.assertEqual(inventory.verify_clean(self.matrix(), self.fixture.witnesses), 1)
        self.assertEqual(self.note().read_bytes(), note_before)
        self.assertEqual(self.fixture.review.read_bytes(), matrix_before)


if __name__ == "__main__":
    unittest.main()
