"""R129 synthetic private Win11 evidence ancestry regressions, no physical QA."""
from __future__ import annotations

import ast
import io
import json
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))

import windows11_manual_acceptance_r109 as qa
import test_windows11_witness_writer_r122 as fixtures

writer = fixtures.writer


class ParentPathCustodyR129(unittest.TestCase):
    def setUp(self):
        self.fx = fixtures.PrivateWitnessR122(
            methodName="test_one_observed_pass_updates_exact_check_only")
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)

    def matrix(self):
        return json.loads(self.fx.review.read_text(encoding="utf-8"))

    def validate(self, folder=None):
        return qa.validate_review(
            self.matrix(), self.fx.template,
            self.fx.witnesses if folder is None else folder)

    def faux_symlink(self, marked):
        original = Path.is_symlink
        def marked_link(path):
            return path == marked or original(path)
        return patch.object(Path, "is_symlink", marked_link)

    def test_ordinary_directory_ancestors_are_stable(self):
        snapshot = qa._directory_chain(self.fx.root)
        self.assertTrue(snapshot)
        self.assertEqual(snapshot, qa._directory_chain(self.fx.root))

    def test_ordinary_nested_private_file_remains_readable(self):
        nested = self.fx.root / "nested"
        nested.mkdir()
        note = nested / "note.txt"
        note.write_bytes(b"synthetic private evidence")
        self.assertEqual(qa._bytes(note, 1024), b"synthetic private evidence")

    def test_linked_ancestor_blocks_r9_source_read(self):
        with self.faux_symlink(self.fx.root):
            with self.assertRaises(qa.ReviewHold):
                qa._bytes(self.fx.review, qa.MAX_REPORT_BYTES)

    def test_linked_review_parent_blocks_matrix_read(self):
        with self.faux_symlink(self.fx.review.parent):
            with self.assertRaises(qa.ReviewHold):
                qa._bytes(self.fx.review, qa.MAX_REPORT_BYTES)

    def test_linked_witness_parent_blocks_private_note_read(self):
        self.fx.one()
        with self.faux_symlink(self.fx.witnesses):
            with self.assertRaises(qa.ReviewHold):
                qa._bytes(self.fx.path(), qa.MAX_WITNESS_BYTES)

    def test_linked_leaf_still_blocked(self):
        with self.faux_symlink(self.fx.review):
            with self.assertRaises(qa.ReviewHold):
                qa._bytes(self.fx.review, qa.MAX_REPORT_BYTES)

    def test_linked_witness_folder_blocks_empty_matrix(self):
        with self.faux_symlink(self.fx.witnesses):
            with self.assertRaises(qa.ReviewHold):
                self.validate()

    def test_linked_witness_ancestor_blocks_empty_matrix(self):
        with self.faux_symlink(self.fx.root):
            with self.assertRaises(qa.ReviewHold):
                self.validate()

    def test_linked_ancestor_blocks_existing_pass_evidence(self):
        self.fx.one()
        with self.faux_symlink(self.fx.root):
            with self.assertRaises(qa.ReviewHold):
                self.validate()

    def test_junction_ancestor_blocks_source_read_without_privilege(self):
        marked = self.fx.root
        # Path.is_junction exists in Python 3.12; emulate a Win32 junction
        # on Linux without privileged junction creation or test skips.
        with patch.object(Path, "is_junction",
                          lambda path: path == marked, create=True):
            with self.assertRaises(qa.ReviewHold):
                qa._bytes(self.fx.review, qa.MAX_REPORT_BYTES)

    def test_reparse_point_attribute_rejected_without_platform_skip(self):
        marked = self.fx.root
        original = Path.lstat
        class Metadata:
            def __init__(self, metadata):
                self.value = metadata
            def __getattr__(self, name):
                if name == "st_file_attributes":
                    return 0x400
                return getattr(self.value, name)
        def fake_lstat(path):
            value = original(path)
            return Metadata(value) if path == marked else value
        with patch.object(qa.stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400, create=True), \
             patch.object(Path, "is_junction", lambda path: False, create=True), \
             patch.object(Path, "lstat", fake_lstat):
            with self.assertRaises(qa.ReviewHold):
                qa._directory_chain(self.fx.root)

    def test_post_read_parent_identity_drift_fails_closed(self):
        stable = qa._directory_chain(self.fx.root)
        changed = stable[:-1] + ((stable[-1][0], stable[-1][1], -999),)
        with patch.object(qa, "_directory_chain", side_effect=[stable, changed]) as check:
            with self.assertRaises(qa.ReviewHold):
                qa._bytes(self.fx.review, qa.MAX_REPORT_BYTES)
        self.assertEqual(check.call_count, 2)

    def test_not_a_directory_parent_rejected(self):
        with self.assertRaises(qa.ReviewHold):
            qa._directory_chain(self.fx.review)

    def test_valid_six_app_pending_matrix_remains_hard_hold(self):
        summary = self.validate()
        self.assertEqual(summary["counts"],
                         {"PASS": 0, "FAIL": 0, "NOT_RUN": 46})
        self.assertFalse(summary["release_authorized"])

    def test_valid_free_and_premium_notes_remain_source_bound(self):
        self.fx.one()
        self.fx.one(app=qa.PREMIUM[0], check=qa.PREMIUM_CHECKS[0])
        summary = self.validate()
        self.assertEqual(summary["counts"],
                         {"PASS": 2, "FAIL": 0, "NOT_RUN": 44})
        self.assertEqual(summary["status"], "REVIEW_HOLD_INCOMPLETE_OR_FAILED")
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["premium_editor_licensed"])

    def test_no_assert_bypass_or_path_leak_in_cli(self):
        module = ast.parse((SCRIPTS / "windows11_manual_acceptance_r109.py")
                           .read_text(encoding="utf-8"))
        guarded = ("_directory_chain", "_bytes", "validate_review")
        for node in module.body:
            if isinstance(node, ast.FunctionDef) and node.name in guarded:
                self.assertFalse(any(isinstance(child, ast.Assert)
                                     for child in ast.walk(node)))
        error = io.StringIO()
        with redirect_stderr(error), patch.object(
                qa, "load_custody", side_effect=qa.ReviewHold(
                    "PRIVATE source filename: pretend-customer-ledger.csv")):
            rc = qa.main(["verify", "--dist", str(self.fx.dist),
                          "--r9-report", str(self.fx.r9),
                          "--expected-r9-sha256", self.fx.pin,
                          "--review", str(self.fx.review),
                          "--witnesses", str(self.fx.witnesses)])
        self.assertEqual(rc, 1)
        self.assertEqual(error.getvalue().strip(), qa.ERROR)
        self.assertNotIn("pretend-customer", error.getvalue())


if __name__ == "__main__":
    unittest.main()
