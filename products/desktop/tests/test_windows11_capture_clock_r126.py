"""R126 synthetic Windows 11 witness capture-time provenance, NOT physical acceptance."""
from __future__ import annotations

import ast
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))
import windows11_manual_acceptance_r109 as qa
import test_windows11_witness_writer_r122 as fixtures

writer = fixtures.writer


class PrivateCaptureClockR126(unittest.TestCase):
    def setUp(self):
        self.fx = fixtures.PrivateWitnessR122(
            methodName="test_one_observed_pass_updates_exact_check_only")
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)

    def session(self, stamp):
        self.fx.template["observed_utc"] = stamp
        self.fx.review.write_text(json.dumps(self.fx.template), encoding="utf-8")

    def read(self):
        review = json.loads(self.fx.review.read_text(encoding="utf-8"))
        note = json.loads(self.fx.path().read_text(encoding="utf-8"))
        return review, note

    def rewrite_note(self, mutate):
        review, note = self.read()
        mutate(note)
        raw = (json.dumps(note, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False) + "\n").encode("utf-8")
        self.fx.path().write_bytes(raw)
        review["apps"][self.fx.app]["checks"][self.fx.check]["witness_sha256"] = qa._sha(raw)
        self.fx.review.write_text(json.dumps(review), encoding="utf-8")

    def validate(self):
        matrix = json.loads(self.fx.review.read_text(encoding="utf-8"))
        return qa.validate_review(matrix, self.fx.template, self.fx.witnesses)

    def test_writer_records_v2_capture_utc_and_no_release(self):
        result = self.fx.one()
        _, note = self.read()
        self.assertEqual(note["schema"], qa.WITNESS_SCHEMA_V2)
        self.assertRegex(note["recorded_utc"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertIs(result["release_authorized"], False)
        self.assertEqual(self.validate()["counts"]["PASS"], 1)

    def test_capture_time_distinct_from_session_anchor(self):
        start = (datetime.now(timezone.utc) - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.session(start)
        self.fx.one()
        _, note = self.read()
        self.assertNotEqual(note["recorded_utc"], start)
        self.assertEqual(note["observed_utc"], start)
        self.assertEqual(self.validate()["counts"]["NOT_RUN"], 45)

    def test_capture_time_of_two_checks_can_differ(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        self.session((now - timedelta(minutes=8)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        with patch.object(writer, "datetime") as fake_clock:
            fake_clock.now.return_value = now - timedelta(minutes=3)
            self.fx.one()
            first = self.read()[1]["recorded_utc"]
            fake_clock.now.return_value = now - timedelta(minutes=1)
            self.fx.one(check=qa.FREE_CHECKS[1])
        other_path = self.fx.witnesses / (
            self.fx.app.removesuffix(".exe") + "--" + qa.FREE_CHECKS[1] + ".json")
        second = json.loads(other_path.read_text(encoding="utf-8"))["recorded_utc"]
        self.assertNotEqual(first, second)
        self.assertEqual(self.validate()["counts"]["PASS"], 2)

    def test_v2_missing_capture_time_holds(self):
        self.fx.one()
        self.rewrite_note(lambda note: note.pop("recorded_utc"))
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_v2_unexpected_field_holds(self):
        self.fx.one()
        self.rewrite_note(lambda note: note.update(extra_clock="synthetic"))
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_v2_backdated_before_session_holds_even_if_resealed(self):
        self.fx.one()
        self.rewrite_note(lambda note: note.update(recorded_utc="2026-01-01T00:00:00Z"))
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_v2_future_capture_holds_even_if_resealed(self):
        self.fx.one()
        future = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.rewrite_note(lambda note: note.update(recorded_utc=future))
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_v2_offset_timezone_holds(self):
        self.fx.one()
        self.rewrite_note(lambda note: note.update(recorded_utc="2026-11-01T12:00:00+00:00"))
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_v2_invalid_calendar_date_holds(self):
        self.fx.one()
        self.rewrite_note(lambda note: note.update(recorded_utc="2026-02-30T12:00:00Z"))
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_v2_nonstring_capture_holds(self):
        self.fx.one()
        self.rewrite_note(lambda note: note.update(recorded_utc=123456789))
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_v2_future_session_anchor_prevents_write(self):
        future = (datetime.now(timezone.utc) + timedelta(minutes=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.session(future)
        with self.assertRaises(qa.ReviewHold):
            self.fx.one()
        self.assertFalse(self.fx.path().exists())
        self.assertEqual(self.fx.review.read_text(encoding="utf-8"),
                         json.dumps(self.fx.template))

    def test_v2_capture_mutation_without_resigning_holds(self):
        self.fx.one()
        _, note = self.read()
        note["recorded_utc"] = "2026-01-01T00:00:00Z"
        self.fx.path().write_text(json.dumps(note), encoding="utf-8")
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_v1_legacy_note_remains_verifiable(self):
        self.fx.one()
        def older(note):
            note["schema"] = qa.WITNESS_SCHEMA
            note.pop("recorded_utc", None)
        self.rewrite_note(older)
        self.assertEqual(self.validate()["counts"]["PASS"], 1)

    def test_v1_rejects_injected_v2_field(self):
        self.fx.one()
        self.rewrite_note(lambda note: note.update(schema=qa.WITNESS_SCHEMA))
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_unknown_witness_version_holds(self):
        self.fx.one()
        self.rewrite_note(lambda note: note.update(schema="fv-labs-unknown"))
        with self.assertRaises(qa.ReviewHold):
            self.validate()

    def test_no_asserts_in_witness_admission_code(self):
        for name in ("windows11_manual_acceptance_r109.py",
                     "windows11_witness_writer_r122.py"):
            source = (SCRIPTS / name).read_text(encoding="utf-8")
            self.assertFalse(any(isinstance(node, ast.Assert)
                                 for node in ast.walk(ast.parse(source))))


if __name__ == "__main__":
    unittest.main()
