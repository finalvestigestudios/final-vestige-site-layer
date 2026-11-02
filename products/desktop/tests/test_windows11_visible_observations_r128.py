"""R128 privacy-safe synthetic manual-observation Unicode evidence regressions."""
from __future__ import annotations

import ast
import hashlib
import io
import json
import sys
import unittest
from contextlib import redirect_stderr
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS.parent / "scripts"))
sys.path.insert(0, str(TESTS))
import windows11_manual_acceptance_r109 as qa
import test_windows11_witness_writer_r122 as fixtures

writer = fixtures.writer


class VisibleObservationR128(unittest.TestCase):
    def setUp(self):
        self.fx = fixtures.PrivateWitnessR122(
            methodName="test_one_observed_pass_updates_exact_check_only")
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.original = self.fx.review.read_bytes()
        self.safe = self.fx.observation.read_text(encoding="utf-8")

    def witness(self, text, *, legacy=False, app=None, check=None):
        review = json.loads(self.fx.review.read_text(encoding="utf-8"))
        app = app or self.fx.app
        check = check or self.fx.check
        note = {
            "schema": qa.WITNESS_SCHEMA if legacy else qa.WITNESS_SCHEMA_V2,
            "app": app, "check": check, "state": "PASS",
            "candidate_sha256": review["apps"][app]["candidate_sha256"],
            "r9_report_sha256": review["r9_report_sha256"],
            "reviewer_id": review["reviewer_id"],
            "windows11_build": review["windows11_build"],
            "observed_utc": review["observed_utc"], "observation": text,
        }
        if not legacy:
            note["recorded_utc"] = review["observed_utc"]
        raw = json.dumps(note, ensure_ascii=True, sort_keys=True).encode("utf-8")
        return raw, review, app, check

    def accepted(self, text, *, legacy=False, app=None, check=None):
        raw, review, app, check = self.witness(
            text, legacy=legacy, app=app, check=check)
        qa._bound_witness(raw, review, app, check, "PASS",
                          now=datetime.now(timezone.utc))

    def refused(self, text, *, legacy=False):
        raw, review, app, check = self.witness(text, legacy=legacy)
        with self.assertRaises(qa.ReviewHold):
            qa._bound_witness(raw, review, app, check, "PASS",
                              now=datetime.now(timezone.utc))

    def test_plain_legacy_witness_remains_valid(self):
        self.accepted(self.safe, legacy=True)

    def test_multilingual_visible_text_combining_accents_preserved(self):
        self.accepted(self.safe + " Résumé, e\u0301cole, العربية, עברית, हिन्दी.")

    def test_tabs_newlines_and_ascii_spaces_remain_valid(self):
        self.accepted(self.safe + "\n\n   Checked field labels.\tNo issue observed.")

    def test_c1_controls_rejected(self):
        for cp in (0x00, 0x0d, 0x7f, 0x80, 0x85, 0x9f):
            with self.subTest(codepoint=cp):
                self.refused(self.safe + chr(cp))

    def test_bidirectional_and_zero_width_formats_rejected(self):
        for cp in (0x061c, 0x200b, 0x200c, 0x200d, 0x200e, 0x200f,
                   0x202e, 0x2060, 0x2066, 0x2069, 0xfeff):
            with self.subTest(codepoint=cp):
                self.refused(self.safe + chr(cp), legacy=True)

    def test_nonstandard_whitespace_rejected(self):
        for cp in (0xa0, 0x1680, 0x2007, 0x2009, 0x2028, 0x2029, 0x3000):
            with self.subTest(codepoint=cp):
                self.refused(self.safe + chr(cp))

    def test_variation_selectors_rejected(self):
        for cp in (0x180b, 0x180f, 0xfe00, 0xfe0f, 0xe0100, 0xe01ef):
            with self.subTest(codepoint=cp):
                self.refused(self.safe + chr(cp))

    def test_blank_filler_glyphs_rejected(self):
        for cp in (0x034f, 0x115f, 0x1160, 0x2800, 0x3164, 0xffa0):
            with self.subTest(codepoint=cp):
                self.refused(self.safe + chr(cp), legacy=True)

    def test_surrogate_and_tag_controls_rejected(self):
        for cp in (0xd800, 0xdbff, 0xe0001, 0xe0020, 0xe007f):
            with self.subTest(codepoint=cp):
                self.refused(self.safe + chr(cp))

    def test_writer_refuses_invisible_input_without_new_evidence(self):
        for cp in (0x200b, 0x85, 0xfe0f, 0x3164):
            with self.subTest(codepoint=cp):
                self.fx.observation.write_text(
                    self.safe + chr(cp), encoding="utf-8")
                with self.assertRaises(qa.ReviewHold):
                    self.fx.one()
                self.assertEqual(self.fx.review.read_bytes(), self.original)
                self.assertFalse(self.fx.path().exists())
                self.assertFalse(self.fx.review.with_name(
                    self.fx.review.name + ".r122.lock").exists())

    def test_rehashed_existing_witness_cannot_hide_invisible_input(self):
        self.fx.one()
        source = self.fx.path()
        for legacy in (False, True):
            with self.subTest(legacy=legacy):
                raw, review, app, check = self.witness(
                    self.safe + "\u200b", legacy=legacy)
                source.write_bytes(raw)
                review["apps"][app]["checks"][check] = {
                    "state": "PASS",
                    "witness_sha256": hashlib.sha256(raw).hexdigest()}
                with self.assertRaises(qa.ReviewHold):
                    qa.validate_review(review, self.fx.template, self.fx.witnesses)

    def test_premium_locked_witness_uses_same_guard(self):
        app = qa.PREMIUM[0]
        check = qa.PREMIUM_CHECKS[0]
        self.accepted(self.safe, app=app, check=check)
        raw, review, app, check = self.witness(
            self.safe + "\u2060", app=app, check=check)
        with self.assertRaises(qa.ReviewHold):
            qa._bound_witness(raw, review, app, check, "PASS")

    def test_privacy_safe_cli_error_on_invisible_witness(self):
        self.fx.observation.write_text(self.safe + "\u200b", encoding="utf-8")
        captured = io.StringIO()
        with patch.object(writer.qa, "native_win11_build", return_value=26100), \
             patch.object(writer.qa, "load_custody",
                          return_value=(self.fx.report, self.fx.hashes, self.fx.raw)), \
             redirect_stderr(captured):
            rc = writer.main([
                "--dist", str(self.fx.dist), "--r9-report", str(self.fx.r9),
                "--expected-r9-sha256", self.fx.pin, "--review", str(self.fx.review),
                "--witnesses", str(self.fx.witnesses), "--app", self.fx.app,
                "--check", self.fx.check, "--state", "PASS",
                "--observation-file", str(self.fx.observation)])
        self.assertEqual(rc, 1)
        self.assertEqual(captured.getvalue().strip(), qa.ERROR)
        self.assertNotIn(str(self.fx.root), captured.getvalue())

    def test_no_asserts_in_validator(self):
        source = (TESTS.parent / "scripts" /
                  "windows11_manual_acceptance_r109.py").read_text(encoding="utf-8")
        for node in ast.parse(source).body:
            if isinstance(node, ast.FunctionDef) and node.name in (
                    "_ambiguous_observation_char", "_bound_witness"):
                self.assertFalse(any(isinstance(child, ast.Assert)
                                     for child in ast.walk(node)))


if __name__ == "__main__":
    unittest.main()
