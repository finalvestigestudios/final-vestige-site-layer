"""R125 synthetic file-identity custody tests; never physical Win11 acceptance."""
from __future__ import annotations

import ast
import os
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
import test_windows11_witness_writer_r122 as fixture_module

writer = fixture_module.writer


class WitnessIdentityR125(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_module.PrivateWitnessR122(
            methodName="test_one_observed_pass_updates_exact_check_only")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def replaced_note(self, same_bytes):
        prior = self.fixture.review.read_bytes()
        verify = writer.inventory.verify_clean
        calls = [0]
        replacement = []

        def swap(matrix, directory):
            calls[0] += 1
            if calls[0] == 2:
                target = self.fixture.path()
                alternate = self.fixture.root / "other-actor-note.json"
                alternate.write_bytes(target.read_bytes() if same_bytes else b"foreign evidence")
                os.replace(alternate, target)
                replacement.append(target.read_bytes())
                raise qa.ReviewHold("synthetic injected failure")
            return verify(matrix, directory)

        with patch.object(writer.inventory, "verify_clean", side_effect=swap):
            with self.assertRaises(qa.ReviewHold):
                self.fixture.one()
        self.assertEqual(calls[0], 2)
        self.assertEqual(self.fixture.review.read_bytes(), prior)
        self.assertEqual(self.fixture.path().read_bytes(), replacement[0])
        self.assertFalse((self.fixture.root / "review.json.r122.lock").exists())

    def test_clean_record_is_human_only(self):
        result = self.fixture.one()
        self.assertIs(result["release_authorized"], False)
        self.assertTrue(self.fixture.path().is_file())

    def test_owned_note_rollback_after_replace_error(self):
        prior = self.fixture.review.read_bytes()
        with patch.object(writer.os, "replace", side_effect=OSError("synthetic failure")):
            with self.assertRaises(OSError):
                self.fixture.one()
        self.assertEqual(self.fixture.review.read_bytes(), prior)
        self.assertFalse(self.fixture.path().exists())

    def test_replaced_identical_note_survives_failed_write(self):
        self.replaced_note(True)

    def test_replaced_different_note_survives_failed_write(self):
        self.replaced_note(False)

    def test_identical_review_replacement_causes_hold(self):
        prior = self.fixture.review.read_bytes()
        verify = writer.inventory.verify_clean
        calls = [0]

        def swap_matrix(matrix, directory):
            calls[0] += 1
            result = verify(matrix, directory)
            if calls[0] == 2:
                other = self.fixture.root / "other-reviewer.json"
                other.write_bytes(prior)
                os.replace(other, self.fixture.review)
            return result

        with patch.object(writer.inventory, "verify_clean", side_effect=swap_matrix):
            with self.assertRaises(qa.ReviewHold):
                self.fixture.one()
        self.assertEqual(calls[0], 2)
        self.assertEqual(self.fixture.review.read_bytes(), prior)
        self.assertFalse(self.fixture.path().exists())

    def test_symlinked_review_matrix_rejected(self):
        original = Path.is_symlink
        target = self.fixture.review

        def fake(path):
            return path == target or original(path)

        with patch.object(Path, "is_symlink", fake):
            with self.assertRaises(qa.ReviewHold):
                self.fixture.one()
        self.assertFalse(self.fixture.path().exists())

    def test_hardlinked_review_matrix_rejected(self):
        original = Path.lstat
        target = self.fixture.review

        def fake(path):
            value = original(path)
            if path == target:
                return SimpleNamespace(
                    st_mode=value.st_mode, st_nlink=2,
                    st_dev=value.st_dev, st_ino=value.st_ino,
                    st_file_attributes=getattr(value, "st_file_attributes", 0))
            return value

        with patch.object(Path, "lstat", fake):
            with self.assertRaises(qa.ReviewHold):
                self.fixture.one()
        self.assertFalse(self.fixture.path().exists())

    def test_directory_matrix_rejected(self):
        self.fixture.review.unlink()
        self.fixture.review.mkdir()
        with self.assertRaises(qa.ReviewHold):
            self.fixture.one()
        self.assertFalse(self.fixture.path().exists())

    def test_missing_matrix_rejected(self):
        self.fixture.review.unlink()
        with self.assertRaises((qa.ReviewHold, OSError)):
            self.fixture.one()
        self.assertFalse(self.fixture.path().exists())

    def test_production_module_has_no_assert_statements(self):
        source = (SCRIPTS / "windows11_witness_writer_r122.py").read_text()
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(source))))


if __name__ == "__main__":
    unittest.main()
