"""R127 synthetic private observation-file provenance, never physical Win11 QA."""
from __future__ import annotations

import ast
import io
import os
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

TESTS = Path(__file__).resolve().parent
SCRIPTS = TESTS.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))
import windows11_manual_acceptance_r109 as qa
import test_windows11_witness_writer_r122 as fixtures

writer = fixtures.writer


class PrivateObservationInputR127(unittest.TestCase):
    def setUp(self):
        self.fx = fixtures.PrivateWitnessR122(
            methodName="test_one_observed_pass_updates_exact_check_only")
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.original = self.fx.review.read_bytes()

    def hold(self, **kwargs):
        with self.assertRaises((qa.ReviewHold, OSError, UnicodeError)):
            self.fx.one(**kwargs)
        self.assertEqual(self.fx.review.read_bytes(), self.original)
        self.assertFalse(self.fx.path().exists())

    def test_stable_standalone_note_passes_without_release(self):
        result = self.fx.one()
        self.assertEqual(result["state"], "PASS")
        self.assertIs(result["release_authorized"], False)
        self.assertTrue(self.fx.path().is_file())

    def test_oversized_note_fails_without_new_witness(self):
        self.fx.observation.write_bytes(b"x" * (writer.NOTE_LIMIT + 1))
        self.hold()

    def test_invalid_utf8_note_fails_closed(self):
        self.fx.observation.write_bytes(b"x" * 100 + b"\xff")
        self.hold()

    def test_note_reusing_raw_r9_report_path_is_rejected(self):
        self.fx.r9.write_bytes(self.fx.observation.read_bytes())
        self.hold(observation_file=self.fx.r9)
        self.assertTrue(self.fx.r9.is_file())

    def test_note_inside_witness_directory_is_rejected(self):
        inside = self.fx.witnesses / "untrusted-note.txt"
        inside.write_bytes(self.fx.observation.read_bytes())
        self.hold(observation_file=inside)
        self.assertTrue(inside.is_file())

    def test_direct_note_symlink_is_rejected_without_following(self):
        original = Path.is_symlink
        source = self.fx.observation
        with patch.object(Path, "is_symlink",
                          lambda path: path == source or original(path)):
            self.hold()
        self.assertEqual(self.fx.observation.read_bytes()[:5], b"HUMAN")

    def test_note_parent_symlink_is_rejected_before_reading(self):
        parent = self.fx.root / "private-notes"
        parent.mkdir()
        moved = parent / "human.txt"
        moved.write_bytes(self.fx.observation.read_bytes())
        original = Path.is_symlink
        with patch.object(Path, "is_symlink",
                          lambda path: path == parent or original(path)):
            self.hold(observation_file=moved)

    def test_hardlinked_note_is_not_accepted(self):
        alias = self.fx.root / "alias.txt"
        try:
            os.link(self.fx.observation, alias)
        except OSError:
            # Some sandbox filesystems do not support hardlinks. Exercise
            # the explicit identity rejection instead of skipping the method.
            with patch.object(writer, "_ordinary_file_identity",
                              side_effect=qa.ReviewHold("unsafe hardlink")):
                self.hold()
        else:
            self.hold()
            self.assertTrue(alias.exists())

    def test_replaced_note_before_open_is_rejected_even_if_bytes_identical(self):
        original_open = os.open
        source = self.fx.observation
        replaced = [False]

        def swap_before_open(path, flags, *args, **kwargs):
            if Path(path) == source and not replaced[0]:
                substitute = self.fx.root / "substitute-before.txt"
                substitute.write_bytes(source.read_bytes())
                os.replace(substitute, source)
                replaced[0] = True
            return original_open(path, flags, *args, **kwargs)

        with patch.object(writer.os, "open", side_effect=swap_before_open):
            self.hold()
        self.assertTrue(replaced[0])

    def test_changed_note_after_open_is_rejected_on_both_platforms(self):
        original_open, original_fstat = os.open, os.fstat
        source = self.fx.observation
        held = {"fd": None, "count": 0, "replaced": False}

        def track_open(path, flags, *args, **kwargs):
            fd = original_open(path, flags, *args, **kwargs)
            if Path(path) == source:
                held["fd"] = fd
            return fd

        def change_on_second_fstat(fd):
            if held["fd"] is not None and fd == held["fd"]:
                held["count"] += 1
                if held["count"] == 2:
                    replacement = self.fx.root / "substitute-after.txt"
                    replacement.write_bytes(source.read_bytes())
                    try:
                        os.replace(replacement, source)
                    except PermissionError:
                        # Windows may deny rename while a read descriptor is
                        # open. Mutate in place to exercise the same hold.
                        with source.open("r+b") as current:
                            current.seek(0)
                            current.write(b"Z")
                            current.flush()
                        replacement.unlink()
                    held["replaced"] = True
            return original_fstat(fd)

        with patch.object(writer.os, "open", side_effect=track_open), patch.object(
                writer.os, "fstat", side_effect=change_on_second_fstat):
            self.hold()
        self.assertTrue(held["replaced"])

    def test_nonregular_file_is_rejected_without_blocking(self):
        original = writer._ordinary_file_identity

        def reject_nonregular(path):
            if path == self.fx.observation:
                raise qa.ReviewHold("nonregular note")
            return original(path)

        with patch.object(writer, "_ordinary_file_identity",
                          side_effect=reject_nonregular):
            self.hold()

    def test_redacted_cli_error_contains_no_private_observation_or_path(self):
        self.fx.observation.write_bytes(b"PRIVATE_ABC" * 2000)
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = writer.main([
                "--dist", str(self.fx.dist), "--r9-report", str(self.fx.r9),
                "--expected-r9-sha256", self.fx.pin, "--review", str(self.fx.review),
                "--witnesses", str(self.fx.witnesses), "--app", self.fx.app,
                "--check", self.fx.check, "--state", "PASS",
                "--observation-file", str(self.fx.observation)])
        self.assertEqual(code, 1)
        self.assertEqual(stderr.getvalue().strip(), qa.ERROR)
        self.assertNotIn("PRIVATE_ABC", stderr.getvalue())
        self.assertNotIn(str(self.fx.observation), stderr.getvalue())

    def test_no_assertions_in_observation_gate_or_writer(self):
        source = (SCRIPTS / "windows11_witness_writer_r122.py").read_text(
            encoding="utf-8")
        self.assertFalse(any(isinstance(n, ast.Assert)
                             for n in ast.walk(ast.parse(source))))


if __name__ == "__main__":
    unittest.main()
