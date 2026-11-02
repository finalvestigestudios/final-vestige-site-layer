"""R130 strict private Win11 R9/matrix/witness JSON and smoke-duration regressions.

Synthetic evidence only. This is not a physical Windows 11 acceptance test.
"""
from __future__ import annotations

import ast
import io
import json
import math
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import windows11_manual_acceptance_r109 as qa
import test_windows11_witness_writer_r122 as fixtures


class NonfiniteEvidenceR130(unittest.TestCase):
    def setUp(self):
        self.fx = fixtures.PrivateWitnessR122(
            methodName="test_one_observed_pass_updates_exact_check_only")
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)

    def rehashed_note(self, bad_token: str):
        """Mutate an otherwise valid private note, then deliberately reseal its hash."""
        self.fx.one()
        previous = self.fx.path().read_bytes()
        # Add one nested nonfinite number. An ordinary JSON loader would accept
        # this before the separate witness-schema field checks reject it.
        updated = previous.rstrip()[:-1] + b',"untrusted_metadata":' + bad_token.encode("ascii") + b'}'
        self.fx.path().write_bytes(updated)
        matrix = json.loads(self.fx.review.read_text(encoding="utf-8"))
        matrix["apps"][self.fx.app]["checks"][self.fx.check]["witness_sha256"] = qa._sha(updated)
        return matrix

    def test_valid_r9_json_is_accepted(self):
        raw = json.dumps(self.fx.report, allow_nan=False).encode("utf-8")
        report = qa._strict_json(raw)
        self.assertEqual(qa.verify_r9(report, self.fx.hashes), self.fx.hashes)

    def test_valid_fraction_and_exponent_json_are_finite(self):
        self.assertEqual(qa._strict_json(b'{"x":1.25e2}')["x"], 125.0)
        self.assertTrue(math.isfinite(qa._strict_json(b'{"x":1e-12}')["x"]))

    def test_r9_nan_constant_is_rejected(self):
        with self.assertRaises(qa.ReviewHold):
            qa._strict_json(b'{"seconds":NaN}')

    def test_r9_positive_infinity_constant_is_rejected(self):
        with self.assertRaises(qa.ReviewHold):
            qa._strict_json(b'{"seconds":Infinity}')

    def test_r9_negative_infinity_constant_is_rejected(self):
        with self.assertRaises(qa.ReviewHold):
            qa._strict_json(b'{"seconds":-Infinity}')

    def test_scientific_overflow_is_rejected(self):
        with self.assertRaises(qa.ReviewHold):
            qa._strict_json(b'{"seconds":1e9999}')

    def test_negative_scientific_overflow_is_rejected(self):
        with self.assertRaises(qa.ReviewHold):
            qa._strict_json(b'{"seconds":-1e9999}')

    def test_nested_nonfinite_token_is_rejected(self):
        with self.assertRaises(qa.ReviewHold):
            qa._strict_json(b'{"outer":{"inner":[0,NaN]}}')

    def test_matrix_nonfinite_token_is_rejected(self):
        matrix = json.loads(self.fx.review.read_text(encoding="utf-8"))
        matrix["extra"] = float("nan")
        raw = json.dumps(matrix).encode("utf-8")
        with self.assertRaises(qa.ReviewHold):
            qa._strict_json(raw)

    def test_duplicate_key_rejection_is_preserved(self):
        with self.assertRaises(qa.ReviewHold):
            qa._strict_json(b'{"schema":1,"schema":1}')

    def test_direct_r9_nan_duration_is_rejected(self):
        self.fx.report["artifacts"][0]["seconds"] = float("nan")
        with self.assertRaises(qa.ReviewHold):
            qa.verify_r9(self.fx.report, self.fx.hashes)

    def test_direct_r9_positive_infinity_duration_is_rejected(self):
        self.fx.report["artifacts"][0]["seconds"] = float("inf")
        with self.assertRaises(qa.ReviewHold):
            qa.verify_r9(self.fx.report, self.fx.hashes)

    def test_direct_r9_negative_infinity_duration_is_rejected(self):
        self.fx.report["artifacts"][0]["seconds"] = float("-inf")
        with self.assertRaises(qa.ReviewHold):
            qa.verify_r9(self.fx.report, self.fx.hashes)

    def test_direct_r9_valid_int_and_float_durations(self):
        self.fx.report["artifacts"][0]["seconds"] = 0
        self.fx.report["artifacts"][1]["seconds"] = 1.125
        self.assertEqual(qa.verify_r9(self.fx.report, self.fx.hashes), self.fx.hashes)

    def test_rehashed_witness_nan_token_fails_closed(self):
        matrix = self.rehashed_note("NaN")
        with self.assertRaises(qa.ReviewHold):
            qa.validate_review(matrix, self.fx.template, self.fx.witnesses)

    def test_rehashed_witness_overflow_number_fails_closed(self):
        matrix = self.rehashed_note("1e9999")
        with self.assertRaises(qa.ReviewHold):
            qa.validate_review(matrix, self.fx.template, self.fx.witnesses)

    def test_six_app_pending_and_one_witness_still_hold(self):
        pending = qa.validate_review(self.fx.template, self.fx.template, self.fx.witnesses)
        self.assertEqual(pending["counts"]["NOT_RUN"], 46)
        self.assertIs(pending["release_authorized"], False)
        self.fx.one(app=qa.PREMIUM[0], check=qa.PREMIUM_CHECKS[0])
        matrix = json.loads(self.fx.review.read_text(encoding="utf-8"))
        status = qa.validate_review(matrix, self.fx.template, self.fx.witnesses)
        self.assertEqual(status["counts"], {"PASS": 1, "FAIL": 0, "NOT_RUN": 45})
        self.assertIs(status["release_authorized"], False)
        self.assertIs(status["premium_editor_licensed"], False)

    def test_cli_errors_are_redacted_no_assert_bypass(self):
        tree = ast.parse((SCRIPTS / "windows11_manual_acceptance_r109.py").read_text(encoding="utf-8"))
        for fn in ("_strict_json", "verify_r9", "load_custody"):
            defs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == fn]
            self.assertEqual(len(defs), 1)
            self.assertFalse(any(isinstance(n, ast.Assert) for n in ast.walk(defs[0])))
        err = io.StringIO()
        with redirect_stderr(err), patch.object(
                qa, "load_custody", side_effect=qa.ReviewHold(
                    "PRIVATE EXE directory: synthetic-financial-customer.csv")):
            result = qa.main(["verify", "--dist", str(self.fx.dist),
                              "--r9-report", str(self.fx.r9),
                              "--expected-r9-sha256", self.fx.pin,
                              "--review", str(self.fx.review),
                              "--witnesses", str(self.fx.witnesses)])
        self.assertEqual(result, 1)
        self.assertEqual(err.getvalue().strip(), qa.ERROR)
        self.assertNotIn("synthetic-financial-customer", err.getvalue())


if __name__ == "__main__":
    unittest.main()
