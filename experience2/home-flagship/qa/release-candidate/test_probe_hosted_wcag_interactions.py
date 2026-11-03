"""Adversarial no-network checks for hosted axe/interaction release-HOLD observer."""
import unittest

from probe_hosted_wcag_interactions import (
    WIDTHS, compact_axe, deny_request, evaluate,
)


def fixture():
    cases = []
    for width in WIDTHS:
        cases.append({
            "case": f"js_{width}", "host": "finalvestige.com",
            "http_status": 200, "blocked_non_get": 0,
            "document_horizontal_overflow": False,
            "interactions": {}, "axe": None,
        })
    cases[1]["interactions"] = {
        "chronicle_click": True, "chronicle_keyboard": True,
        "case_switch": True, "observer_switch": True,
        "chapter_anchor": True,
    }
    for ix in (1, 3):
        cases[ix]["axe"] = {"violation_rules": 0, "incomplete_rules": 1}
    cases.append({
        "case": "nojs_390", "host": "finalvestige.com",
        "http_status": 200, "blocked_non_get": 0,
        "document_horizontal_overflow": False, "nojs_fallback": True,
    })
    cases.append({
        "case": "reduced_390", "host": "finalvestige.com",
        "http_status": 200, "blocked_non_get": 0,
        "document_horizontal_overflow": False, "prefers_reduced_motion": True,
    })
    return cases


class HostedAxeInteractionAdmissionTests(unittest.TestCase):
    def test_read_only_guard_blocks_post_and_archival_photo(self):
        self.assertTrue(deny_request("POST", "https://finalvestige.com/"))
        self.assertTrue(deny_request("PATCH", "https://finalvestige.com/"))
        self.assertTrue(deny_request("GET", "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg?resize=123"))
        self.assertTrue(deny_request("GET", "https://finalvestige.com/wp-content/uploads/nypl-5003296-original.jpg"))
        self.assertFalse(deny_request("GET", "https://finalvestige.com/"))
        self.assertFalse(deny_request("GET", "https://finalvestige.com/focus/"))
        self.assertFalse(deny_request("GET", "https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp"))
        self.assertFalse(deny_request("GET", "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg?fit=500"))
        self.assertFalse(deny_request("GET", "https://nypl.org/catalog/some-source-link"))

    def test_axe_receipt_strips_dom_and_html(self):
        raw = {
            "violations": [{
                "id": "color-contrast", "impact": "serious",
                "nodes": [{"html": "<secret>foo</secret>", "target": [".private"]}],
            }],
            "incomplete": [{"html": "other"}], "passes": [{}],
        }
        report = compact_axe(raw)
        self.assertEqual(report["violation_rules"], 1)
        self.assertEqual(report["violations"][0]["affected_elements"], 1)
        self.assertEqual(report["incomplete_rules"], 1)
        self.assertNotIn("secret", str(report))
        self.assertNotIn("private", str(report))

    def test_missing_axe_must_fail_closed(self):
        for bad in (None, {}, {"violations": [], "incomplete": []},
                    {"violations": [{"id": "color-contrast"}],
                     "incomplete": [], "passes": []}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                compact_axe(bad)

    def test_success_is_still_release_hold(self):
        receipt = evaluate(fixture())
        self.assertEqual(receipt["anonymous_read_only_gate"], "PASS")
        self.assertEqual(receipt["hosted_interaction_and_reflow_gate"], "PASS")
        self.assertEqual(receipt["axe_instrumentation_gate"], "PASS")
        self.assertEqual(receipt["axe_automated_violation_gate"], "PASS")
        self.assertEqual(receipt["manual_accessibility_gate"], "HOLD")
        self.assertEqual(receipt["release_gate"], "HOLD")
        # Browser telemetry POST may be attempted; route guard aborts it.
        # Denied attempts are not allowed production writes.
        cases = fixture()
        cases[0]["blocked_non_get"] = 3
        self.assertEqual(evaluate(cases)["anonymous_read_only_gate"], "PASS")

    def test_missing_width_or_duplicate_case_is_error(self):
        cases = fixture()
        for variant in (cases[:-1], cases + [cases[0]],
                        cases[:-1] + [dict(cases[0])]):
            with self.subTest(n=len(variant)), self.assertRaises(ValueError):
                evaluate(variant)

    def test_forged_host_or_http_403_denied(self):
        cases = fixture()
        cases[0]["host"] = "finalvestige.com.evil.invalid"
        self.assertEqual(evaluate(cases)["anonymous_read_only_gate"], "FAIL")
        cases = fixture()
        cases[0]["http_status"] = 403
        self.assertEqual(evaluate(cases)["anonymous_read_only_gate"], "FAIL")

    def test_interaction_failure_or_no_js_failure_is_detected(self):
        cases = fixture()
        cases[1]["interactions"]["observer_switch"] = False
        self.assertEqual(evaluate(cases)["hosted_interaction_and_reflow_gate"], "FAIL")
        cases = fixture()
        cases[-2]["nojs_fallback"] = False
        self.assertEqual(evaluate(cases)["hosted_interaction_and_reflow_gate"], "FAIL")

    def test_reflow_and_reduced_motion_fail_closed(self):
        cases = fixture()
        cases[0]["document_horizontal_overflow"] = True
        self.assertEqual(evaluate(cases)["hosted_interaction_and_reflow_gate"], "FAIL")
        cases = fixture()
        cases[-1]["prefers_reduced_motion"] = False
        self.assertEqual(evaluate(cases)["hosted_interaction_and_reflow_gate"], "FAIL")

    def test_axe_violation_is_a_fail_not_hidden_by_ci(self):
        cases = fixture()
        cases[1]["axe"]["violation_rules"] = 1
        result = evaluate(cases)
        self.assertEqual(result["axe_automated_violation_gate"], "FAIL")
        self.assertEqual(result["release_gate"], "HOLD")

    def test_missing_axe_scan_fails_instrumentation(self):
        cases = fixture()
        cases[3]["axe"] = None
        result = evaluate(cases)
        self.assertEqual(result["axe_instrumentation_gate"], "FAIL")
        self.assertEqual(result["axe_automated_violation_gate"], "FAIL")


if __name__ == "__main__":
    unittest.main()
