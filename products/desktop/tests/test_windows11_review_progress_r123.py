"""R123 read-only six-app reviewer queue synthetic contract tests (no real Win11)."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
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
import windows11_witness_writer_r122 as writer
import windows11_review_progress_r123 as progress

sha = lambda data: hashlib.sha256(data).hexdigest()


class PrivateProgressR123(unittest.TestCase):
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
        self.raw = b"synthetic six-EXE R9 evidence only"
        self.pin = sha(self.raw)
        self.hashes = {name: sha(name.encode()) for name in qa.ALL}
        self.report = {
            "schema": 1, "status": "windows_smoke_passed",
            "windows_executables_verified": True, "smoke_simulated": False,
            "release_authorized": False, "premium_entitlement_verified": False,
            "checksums_sha256": sha(b"synthetic inventory"),
            "artifacts": [
                {"name": name, "sha256": self.hashes[name],
                 "pe_machine": "AMD64", "smoke": "passed", "seconds": 0.1}
                for name in qa.ALL],
        }
        self.template = qa.make_template(self.report, self.hashes, self.raw)
        self.template["reviewer_id"] = "Synthetic-human01"
        self.template["windows11_build"] = 26100
        self.template["observed_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.review.write_text(json.dumps(self.template), encoding="utf-8")
        self.observation.write_text(
            "PRIVATE-OBSERVATION-SENTINEL: Synthetic keyboard and screen reader "
            "observation used only in a regression fixture. No physical Windows "
            "test or independent reviewer judgment was performed.",
            encoding="utf-8")

    def gates(self):
        # Two mocks are used only for synthetic CI tests; production never mocks
        # Win11 or actual R9 candidate custody.
        return (
            patch.object(qa, "native_win11_build", return_value=26100),
            patch.object(qa, "load_custody",
                         return_value=(self.report, self.hashes, self.raw)),
        )

    def inspect(self, **overrides):
        opts = dict(dist=self.dist, r9_report=self.r9,
                    expected_pin=self.pin, review=self.review,
                    witnesses=self.witnesses)
        opts.update(overrides)
        native, custody = self.gates()
        with native, custody as mocked_custody:
            result = progress.inspect(**opts)
        self.assertEqual(mocked_custody.call_args.args[2], self.pin)
        return result

    def record(self, app=None, check=None, state="PASS"):
        app = app or qa.ALL[0]
        check = check or qa._checks(app)[0]
        native, custody = self.gates()
        with native, custody:
            return writer.record_one(
                dist=self.dist, r9_report=self.r9, expected_pin=self.pin,
                review=self.review, witnesses=self.witnesses, app=app,
                check=check, state=state, observation_file=self.observation)

    def note(self, app, check):
        return self.witnesses / (app.removesuffix(".exe") + "--" + check + ".json")

    def test_zero_checks_is_hold_with_first_next_step(self):
        p = self.inspect()
        self.assertEqual(p["counts"], {"PASS": 0, "FAIL": 0, "NOT_RUN": 46})
        self.assertEqual(p["total_checks"], 46)
        self.assertEqual(p["per_app"][0]["next_check"], qa.FREE_CHECKS[0])
        self.assertEqual(len(p["per_app"]), 6)
        self.assertEqual(p["status"], "RELEASE_HOLD")
        self.assertIs(p["release_authorized"], False)

    def test_one_pass_moves_next_check_without_approval(self):
        self.record()
        p = self.inspect()
        self.assertEqual(p["counts"], {"PASS": 1, "FAIL": 0, "NOT_RUN": 45})
        self.assertEqual(p["per_app"][0]["next_check"], qa.FREE_CHECKS[1])
        self.assertIs(p["premium_editor_licensed"], False)

    def test_one_fail_remains_a_release_hold(self):
        self.record(state="FAIL")
        p = self.inspect()
        self.assertEqual(p["counts"]["FAIL"], 1)
        self.assertEqual(p["matrix_status"], "REVIEW_HOLD_INCOMPLETE_OR_FAILED")
        self.assertEqual(p["status"], "RELEASE_HOLD")

    def test_per_app_queue_preserves_six_product_order(self):
        for app in (qa.PREMIUM[1], qa.FREE[0]):
            self.record(app=app)
        p = self.inspect()
        self.assertEqual([a["app"] for a in p["per_app"]], list(qa.ALL))
        self.assertEqual([a["counts"]["PASS"] for a in p["per_app"]], [1, 0, 0, 0, 0, 1])

    def test_orphan_witness_blocks_even_empty_matrix(self):
        (self.witnesses / "unreferenced.json").write_text("leftover")
        with self.assertRaises(qa.ReviewHold):
            self.inspect()

    def test_extra_witness_blocks_even_with_valid_pass(self):
        self.record()
        (self.witnesses / "unknown-app.json").write_text("leftover")
        with self.assertRaises(qa.ReviewHold):
            self.inspect()

    def test_extra_directory_blocks_progress(self):
        (self.witnesses / "unknown-subfolder").mkdir()
        with self.assertRaises(qa.ReviewHold):
            self.inspect()

    def test_prior_witness_tampering_blocks_progress(self):
        self.record()
        path = self.note(qa.ALL[0], qa.FREE_CHECKS[0])
        path.write_bytes(path.read_bytes() + b"altered")
        with self.assertRaises(qa.ReviewHold):
            self.inspect()

    def test_changed_candidate_sha_blocks_progress(self):
        matrix = json.loads(self.review.read_text())
        matrix["apps"][qa.ALL[0]]["candidate_sha256"] = sha(b"wrong EXE")
        self.review.write_text(json.dumps(matrix))
        with self.assertRaises(qa.ReviewHold):
            self.inspect()

    def test_preexisting_writer_lock_blocks_even_if_empty(self):
        lock = self.review.with_name(self.review.name + ".r122.lock")
        lock.write_text("another review writer")
        with self.assertRaises(qa.ReviewHold):
            self.inspect()
        self.assertEqual(lock.read_text(), "another review writer")

    def test_wrong_native_windows_build_blocks_progress(self):
        matrix = json.loads(self.review.read_text())
        matrix["windows11_build"] = 22000
        self.review.write_text(json.dumps(matrix))
        with self.assertRaises(qa.ReviewHold):
            self.inspect()

    def test_missing_external_pin_fails_before_custody(self):
        with patch.object(qa, "load_custody", side_effect=AssertionError("not called")):
            with self.assertRaises(qa.ReviewHold):
                progress.inspect(dist=self.dist, r9_report=self.r9,
                                 expected_pin="", review=self.review,
                                 witnesses=self.witnesses)

    def test_non_windows_machine_fails_before_custody(self):
        with patch.object(qa, "native_win11_build",
                          side_effect=qa.ReviewHold("not a Win11 workstation")):
            with patch.object(qa, "load_custody", side_effect=AssertionError("not called")):
                with self.assertRaises(qa.ReviewHold):
                    progress.inspect(dist=self.dist, r9_report=self.r9,
                                     expected_pin=self.pin, review=self.review,
                                     witnesses=self.witnesses)

    def test_review_in_candidate_directory_rejected(self):
        inside = self.dist / "review.json"
        inside.write_bytes(self.review.read_bytes())
        with self.assertRaises(qa.ReviewHold):
            self.inspect(review=inside)

    def test_progress_never_exposes_private_observation_or_pin(self):
        self.record()
        p = self.inspect()
        output = json.dumps(p)
        self.assertNotIn("PRIVATE-OBSERVATION-SENTINEL", output)
        self.assertNotIn(self.pin, output)
        self.assertNotIn("Synthetic-human01", output)
        self.assertNotIn(str(self.root), output)

    def test_cli_failure_is_redacted(self):
        error = io.StringIO()
        with redirect_stderr(error):
            rc = progress.main([
                "--dist", str(self.dist), "--r9-report", str(self.r9),
                "--expected-r9-sha256", "PRIVATE-OBSERVATION-SENTINEL",
                "--review", str(self.review), "--witnesses", str(self.witnesses)])
        self.assertEqual(rc, 1)
        self.assertEqual(error.getvalue().strip(), qa.ERROR)
        self.assertNotIn("PRIVATE-OBSERVATION-SENTINEL", error.getvalue())

    def test_all_46_synthetic_pass_claims_still_uncertified(self):
        for app in qa.ALL:
            for check in qa._checks(app):
                self.record(app=app, check=check)
        result = self.inspect()
        self.assertEqual(result["counts"], {"PASS": 46, "FAIL": 0, "NOT_RUN": 0})
        self.assertEqual(result["matrix_status"], "MANUAL_MATRIX_COMPLETE_UNCERTIFIED")
        self.assertEqual(result["status"], "RELEASE_HOLD")
        self.assertIs(result["release_authorized"], False)
        self.assertTrue(all(app["next_check"] is None for app in result["per_app"]))


if __name__ == "__main__":
    unittest.main()
