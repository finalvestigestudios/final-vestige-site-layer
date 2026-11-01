"""R122 local-only Win11 witness recorder; all tests use synthetic data."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import windows11_manual_acceptance_r109 as qa

spec = importlib.util.spec_from_file_location("windows11_witness_writer_r122", SCRIPTS / "windows11_witness_writer_r122.py")
writer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer)
sha = lambda b: hashlib.sha256(b).hexdigest()


class PrivateWitnessR122(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.dist = self.root / "dist"
        self.dist.mkdir()
        self.witnesses = self.root / "witnesses"
        self.witnesses.mkdir()
        self.review = self.root / "review.json"
        self.r9 = self.root / "r9.json"
        self.observation = self.root / "observation.txt"
        self.app = qa.FREE[0]
        self.check = qa.FREE_CHECKS[0]
        self.pin = sha(b"synthetic R9 raw bytes")
        self.hashes = {name: sha(name.encode()) for name in qa.ALL}
        self.report = {
            "schema": 1, "status": "windows_smoke_passed",
            "windows_executables_verified": True, "smoke_simulated": False,
            "release_authorized": False, "premium_entitlement_verified": False,
            "checksums_sha256": sha(b"synthetic checksums"),
            "artifacts": [
                {"name": name, "sha256": self.hashes[name],
                 "pe_machine": "AMD64", "smoke": "passed", "seconds": 0.1}
                for name in qa.ALL],
        }
        self.raw = b"synthetic R9 raw bytes"
        self.template = qa.make_template(self.report, self.hashes, self.raw)
        self.template["reviewer_id"] = "Human-reviewer01"
        self.template["windows11_build"] = 26100
        self.template["observed_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.review.write_text(json.dumps(self.template), encoding="utf-8")
        self.observation.write_text(
            "HUMAN OBSERVATION SYNTHETIC TEST ONLY: Used Tab and Shift+Tab "
            "to inspect the visible source-picker controls in a fake test fixture. "
            "This text is not a real accessibility or Windows 11 assertion.",
            encoding="utf-8")

    def one(self, **overrides):
        p = dict(dist=self.dist, r9_report=self.r9, expected_pin=self.pin,
                 review=self.review, witnesses=self.witnesses, app=self.app,
                 check=self.check, state="PASS", observation_file=self.observation)
        p.update(overrides)
        with patch.object(qa, "native_win11_build", return_value=26100), patch.object(
            qa, "load_custody", return_value=(self.report, self.hashes, self.raw)
        ) as custody:
            value = writer.record_one(**p)
        self.assertEqual(custody.call_args.args[2], self.pin)
        return value

    def path(self):
        return self.witnesses / (self.app.removesuffix(".exe") + "--" + self.check + ".json")

    def test_one_observed_pass_updates_exact_check_only(self):
        result = self.one()
        review = json.loads(self.review.read_text())
        self.assertEqual(result["state"], "PASS")
        self.assertIs(result["release_authorized"], False)
        self.assertEqual(result["witness_sha256"], sha(self.path().read_bytes()))
        self.assertEqual(qa.validate_review(review, self.template, self.witnesses)["counts"],
                         {"PASS": 1, "FAIL": 0, "NOT_RUN": 45})
        self.assertNotIn("release_authorized", review)

    def test_fail_state_remains_a_hold(self):
        result = self.one(state="FAIL")
        matrix = json.loads(self.review.read_text())
        self.assertEqual(result["state"], "FAIL")
        self.assertEqual(qa.validate_review(matrix, self.template, self.witnesses)["status"],
                         "REVIEW_HOLD_INCOMPLETE_OR_FAILED")

    def test_two_different_checks_are_reproducible(self):
        self.one()
        self.one(check=qa.FREE_CHECKS[1])
        matrix = json.loads(self.review.read_text())
        self.assertEqual(qa.validate_review(matrix, self.template, self.witnesses)["counts"],
                         {"PASS": 2, "FAIL": 0, "NOT_RUN": 44})

    def test_already_recorded_check_never_overwritten(self):
        self.one()
        old_review = self.review.read_bytes()
        old_note = self.path().read_bytes()
        with self.assertRaises(qa.ReviewHold):
            self.one(state="FAIL")
        self.assertEqual(old_review, self.review.read_bytes())
        self.assertEqual(old_note, self.path().read_bytes())

    def test_preexisting_unreferenced_note_is_not_overwritten(self):
        self.path().write_bytes(b"prior private evidence")
        with self.assertRaises(qa.ReviewHold): self.one()
        self.assertEqual(self.path().read_bytes(), b"prior private evidence")

    def test_short_observation_fails_before_witness(self):
        self.observation.write_text("short", encoding="utf-8")
        with self.assertRaises(qa.ReviewHold): self.one()
        self.assertFalse(self.path().exists())

    def test_bidi_observation_is_rejected(self):
        self.observation.write_text("human observation " * 10 + "\u202e", encoding="utf-8")
        with self.assertRaises(qa.ReviewHold): self.one()
        self.assertFalse(self.path().exists())

    def test_invalid_app_rejected(self):
        with self.assertRaises(qa.ReviewHold): self.one(app="Unknown.exe")
        self.assertFalse(self.path().exists())

    def test_invalid_check_rejected(self):
        with self.assertRaises(qa.ReviewHold): self.one(check="automatically_approve")

    def test_unperformed_conclusion_rejected(self):
        with self.assertRaises(qa.ReviewHold): self.one(state="NOT_RUN")

    def test_missing_external_pin_rejected_before_load(self):
        with patch.object(qa, "load_custody", side_effect=AssertionError("must not call")):
            with self.assertRaises(qa.ReviewHold):
                writer.record_one(dist=self.dist, r9_report=self.r9,
                                  expected_pin="", review=self.review,
                                  witnesses=self.witnesses, app=self.app,
                                  check=self.check, state="PASS",
                                  observation_file=self.observation)
        self.assertFalse(self.path().exists())

    def test_windows11_required_before_source_custody(self):
        # Do not use self.one(): it intentionally mocks the machine as Win11.
        with patch.object(qa, "native_win11_build", side_effect=qa.ReviewHold("not Win11")):
            with patch.object(qa, "load_custody", side_effect=AssertionError("must not load")):
                with self.assertRaises(qa.ReviewHold):
                    writer.record_one(
                        dist=self.dist, r9_report=self.r9, expected_pin=self.pin,
                        review=self.review, witnesses=self.witnesses, app=self.app,
                        check=self.check, state="PASS", observation_file=self.observation)
        self.assertFalse(self.path().exists())

    def test_reported_build_must_match_native_build(self):
        self.template["windows11_build"] = 22000
        self.review.write_text(json.dumps(self.template))
        with self.assertRaises(qa.ReviewHold): self.one()

    def test_invalid_existing_witness_blocks_additional_notes(self):
        self.one()
        self.path().write_bytes(b"tampered")
        with self.assertRaises(qa.ReviewHold): self.one(check=qa.FREE_CHECKS[1])

    def test_symlink_witness_folder_rejected(self):
        alt = self.root / "real-witness"
        alt.mkdir()
        link = self.root / "linked-witness"
        try:
            link.symlink_to(alt, target_is_directory=True)
        except (OSError, NotImplementedError):
            # GitHub-hosted Windows runners may not have symlink privilege;
            # still exercise the fail-closed symlink guard with a synthetic
            # platform response, rather than silently SKIP the mandatory gate.
            link.mkdir()
            original = Path.is_symlink
            def pretend_link(value):
                return value == link or original(value)
            with patch.object(Path, "is_symlink", pretend_link):
                with self.assertRaises(qa.ReviewHold):
                    self.one(witnesses=link)
        else:
            with self.assertRaises(qa.ReviewHold):
                self.one(witnesses=link)

    def test_witness_directory_inside_executables_rejected(self):
        inside = self.dist / "private"
        inside.mkdir()
        with self.assertRaises(qa.ReviewHold): self.one(witnesses=inside)

    def test_review_under_executable_directory_rejected(self):
        bad = self.dist / "review.json"
        bad.write_bytes(self.review.read_bytes())
        with self.assertRaises(qa.ReviewHold): self.one(review=bad)

    def test_duplicate_review_json_keys_rejected(self):
        self.review.write_text('{"schema":1,"schema":2}')
        with self.assertRaises(qa.ReviewHold): self.one()

    def test_cooperative_lock_existing_rejected(self):
        lock = self.review.with_name(self.review.name + ".r122.lock")
        lock.write_text("another reviewer")
        with self.assertRaises(FileExistsError): self.one()
        self.assertEqual(lock.read_text(), "another reviewer")

    def test_atomic_review_failure_removes_new_note(self):
        old = self.review.read_bytes()
        with patch.object(writer.os, "replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError): self.one()
        self.assertEqual(self.review.read_bytes(), old)
        self.assertFalse(self.path().exists())
        self.assertFalse(list(self.root.glob(".fv-r122-*")))

    def test_failed_write_releases_own_empty_lock(self):
        self.observation.write_text("short")
        with self.assertRaises(qa.ReviewHold): self.one()
        self.assertFalse((self.root / "review.json.r122.lock").exists())

    def test_do_not_clear_nonempty_modified_lock(self):
        self.observation.write_text("short")
        lock = self.root / "review.json.r122.lock"
        original = writer.qa._bytes
        def changed(path, maximum, **kwargs):
            if path == self.observation:
                lock.write_text("reviewer changed lock")
            return original(path, maximum, **kwargs)
        with patch.object(writer.qa, "_bytes", side_effect=changed):
            with self.assertRaises(qa.ReviewHold): self.one()
        self.assertEqual(lock.read_text(), "reviewer changed lock")

    def test_redacted_cli_failure_never_prints_observation(self):
        err = io.StringIO()
        self.observation.write_text("PRIVATE FINANCIAL TEXT")
        with redirect_stderr(err):
            status = writer.main(["--dist", str(self.dist), "--r9-report", str(self.r9),
                                  "--expected-r9-sha256", self.pin,
                                  "--review", str(self.review), "--witnesses", str(self.witnesses),
                                  "--app", self.app, "--check", self.check, "--state", "PASS",
                                  "--observation-file", str(self.observation)])
        self.assertEqual(status, 1)
        self.assertEqual(err.getvalue().strip(), qa.ERROR)
        self.assertNotIn("PRIVATE", err.getvalue())

    def test_no_asserts_in_production_gate(self):
        import ast
        tree = ast.parse((SCRIPTS / "windows11_witness_writer_r122.py").read_text())
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(tree)))


if __name__ == "__main__":
    unittest.main()
