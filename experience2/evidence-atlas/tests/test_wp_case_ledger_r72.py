"""Adversarial, no-network contracts for the R72 authentic WordPress receipt."""
import json
import tempfile
import unittest
from pathlib import Path

from wp_case_ledger_r72 import CaseLedger, WIDTHS


class R72LedgerTests(unittest.TestCase):
    def make(self, root):
        return CaseLedger(Path(root) / "R72_CASE_LEDGER.json")

    def test_initial_gate_is_never_a_success(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            receipt = json.loads(gate.destination.read_text())
            self.assertEqual(receipt["completed"], 0)
            self.assertFalse(receipt["all_cases_accepted"])
            self.assertEqual(receipt["release"], "STAGING_HOLD")
            self.assertFalse(receipt["production_wordpress_written"])
            self.assertFalse(receipt["field_cwv_verified"])

    def test_stopped_after_http_never_claims_success(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.begin(320, False)
            gate.advance("HTTP_200")
            gate.hold("ASSERTION")
            receipt = json.loads(gate.destination.read_text())
            self.assertEqual(receipt["cases"][0]["milestone"], "HTTP_200")
            self.assertEqual(receipt["failure_class"], "ASSERTION")
            self.assertFalse(receipt["all_cases_accepted"])

    def test_full_14_case_sequence(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            for width in WIDTHS:
                for js in (False, True):
                    gate.begin(width, js)
                    for stage in ("HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN"):
                        gate.advance(stage)
                    if js:
                        gate.advance("INTERACTION")
                        if width in (390, 1440):
                            gate.advance("AXE")
                        gate.advance("LAB_METRICS")
                        gate.advance("PRINT")
                    else:
                        gate.advance("NO_JS_CONTENT")
                    gate.pass_case()
            self.assertEqual(gate.require_complete()["completed"], 14)

    def test_missing_js_print_does_not_pass(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.begin(320, False)
            gate.advance("NO_JS_CONTENT")
            gate.pass_case()
            gate.begin(320, True)
            for stage in ("HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN", "INTERACTION"):
                gate.advance(stage)
            with self.assertRaisesRegex(ValueError, "INCOMPLETE_CASE"):
                gate.pass_case()

    def test_missing_axe_may_only_be_certified_by_separate_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            self.assertFalse(json.loads(gate.destination.read_text())["axe_verified_all_required"])

    def test_rejects_out_of_order_and_extra_records(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            with self.assertRaisesRegex(ValueError, "UNEXPECTED_CASE_ORDER"):
                gate.begin(360, False)
            gate.begin(320, False)
            with self.assertRaisesRegex(ValueError, "CASE_NOT_CLOSED"):
                gate.begin(320, True)

    def test_enforces_strict_boolean_not_int(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            with self.assertRaisesRegex(ValueError, "INVALID_CASE_TYPES"):
                gate.begin(320, 0)

    def test_js_only_stages_rejected_when_disabled(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.begin(320, False)
            with self.assertRaisesRegex(ValueError, "JAVASCRIPT_ONLY_MILESTONE"):
                gate.advance("AXE")

    def test_unknown_stage_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.begin(320, False)
            with self.assertRaisesRegex(ValueError, "UNEXPECTED_MILESTONE"):
                gate.advance("LICENSE_CLEARED")

    def test_cannot_regress_progress_or_rewrite_history(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.begin(320, False)
            gate.advance("HTTP_200")
            gate.advance("SOURCE_CUSTODY")
            with self.assertRaisesRegex(ValueError, "MILESTONE_NOT_MONOTONIC"):
                gate.advance("HTTP_200")

    def test_untrusted_error_detail_never_serialized(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.begin(320, False)
            gate.hold("PASSWORD=SECRET https://example.org/wp-admin/")
            content = gate.destination.read_text()
            self.assertNotIn("PASSWORD", content)
            self.assertNotIn("example.org", content)
            self.assertEqual(json.loads(content)["failure_class"], "UNKNOWN")

    def test_wrong_filename_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "UNEXPECTED_LEDGER_DESTINATION"):
                CaseLedger(Path(d) / "other.json")

    def test_atomic_update_no_tmp_leaks(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.begin(320, False)
            gate.advance("HTTP_200")
            self.assertFalse((Path(d) / "R72_CASE_LEDGER.json.tmp").exists())
            self.assertTrue(gate.destination.is_file())

    def test_skipped_source_and_network_gates_refused(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.begin(320, False)
            with self.assertRaisesRegex(ValueError, "MILESTONE_SKIPPED_OR_UNEXPECTED"):
                gate.advance("SOURCE_CUSTODY")
            gate.advance("HTTP_200")
            with self.assertRaisesRegex(ValueError, "MILESTONE_SKIPPED_OR_UNEXPECTED"):
                gate.advance("NO_JS_CONTENT")

    def test_axe_cannot_be_skipped_at_390(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            for width in (320,):
                for js in (False, True):
                    gate.begin(width, js)
                    for stage in ("HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN"):
                        gate.advance(stage)
                    if js:
                        gate.advance("INTERACTION")
                        gate.advance("LAB_METRICS")
                        gate.advance("PRINT")
                    else:
                        gate.advance("NO_JS_CONTENT")
                    gate.pass_case()
            gate.begin(360, False)
            for stage in ("HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN", "NO_JS_CONTENT"):
                gate.advance(stage)
            gate.pass_case()
            gate.begin(360, True)
            for stage in ("HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN", "INTERACTION", "LAB_METRICS", "PRINT"):
                gate.advance(stage)
            gate.pass_case()
            gate.begin(390, False)
            for stage in ("HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN", "NO_JS_CONTENT"):
                gate.advance(stage)
            gate.pass_case()
            gate.begin(390, True)
            for stage in ("HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN", "INTERACTION"):
                gate.advance(stage)
            with self.assertRaisesRegex(ValueError, "MILESTONE_SKIPPED_OR_UNEXPECTED"):
                gate.advance("LAB_METRICS")
            gate.advance("AXE")
            gate.advance("LAB_METRICS")

    def test_axe_not_accepted_at_unreviewed_320_width(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.begin(320, False)
            for stage in ("HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN", "NO_JS_CONTENT"):
                gate.advance(stage)
            gate.pass_case()
            gate.begin(320, True)
            for stage in ("HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN", "INTERACTION"):
                gate.advance(stage)
            with self.assertRaisesRegex(ValueError, "MILESTONE_SKIPPED_OR_UNEXPECTED"):
                gate.advance("AXE")
            gate.advance("LAB_METRICS")

    def test_failure_cannot_be_resumed(self):
        with tempfile.TemporaryDirectory() as d:
            gate = self.make(d)
            gate.hold("BROWSER")
            with self.assertRaisesRegex(ValueError, "CASE_NOT_CLOSED"):
                gate.begin(320, False)

if __name__ == "__main__":
    unittest.main()
