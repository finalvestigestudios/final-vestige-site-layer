"""Fail-closed source tests for hosted first-screen founder visual review."""
import unittest

from capture_hosted_margins_visual import denied, grade, valid_css, WIDTHS


def healthy_cases():
    return [
        {
            "width": w, "http": 200, "host": "finalvestige.com",
            "flagship": True, "margins": 72, "chapters": 7, "focus_links": 3,
            "candidate_active": True, "overflow_before": False,
            "overflow_after": False,
            "screenshots": {"before": "a" * 64, "after": "b" * 64},
        }
        for w in WIDTHS
    ]


class BrowserVisualEvidenceTests(unittest.TestCase):
    def test_hosted_capture_is_always_release_hold(self):
        got = grade(healthy_cases())
        self.assertEqual(got["anonymous_visual_capture"], "PASS")
        self.assertEqual(got["production_release"], "HOLD")
        self.assertEqual(got["actual_browser_zoom_certification"], "NOT_TESTED")

    def test_truncated_or_duplicated_matrix_rejected(self):
        for rows in (healthy_cases()[:2], healthy_cases() + [healthy_cases()[0]],
                     [healthy_cases()[0]] * 3):
            with self.assertRaises(ValueError):
                grade(rows)

    def test_known_content_markers_are_strict(self):
        for key, value in [
            ("http", 404), ("host", "evil.example"), ("flagship", False),
            ("margins", 71), ("chapters", 6), ("focus_links", 0),
            ("candidate_active", False), ("overflow_before", True),
            ("overflow_after", True),
        ]:
            with self.subTest(key=key):
                rows = healthy_cases()
                rows[0][key] = value
                self.assertEqual(grade(rows)["anonymous_visual_capture"], "FAIL")

    def test_receipt_hashes_must_be_real_sha256_shapes(self):
        for payload in ("", "bad", "x" * 64, "A" * 64, None):
            with self.subTest(payload=str(payload)[:5]):
                rows = healthy_cases()
                rows[1]["screenshots"]["before"] = payload
                self.assertEqual(grade(rows)["anonymous_visual_capture"], "FAIL")

    def test_no_network_or_script_injection_css(self):
        css = """.fv-margin-strip--rotator .fv-margin-strip__item {
 animation-name: fvMarginContrastSafe; visibility: hidden; opacity: 1;
 filter: none;
}
@keyframes fvMarginContrastSafe { 0% { visibility: visible } }
@media (prefers-reduced-motion: reduce) { .fv-margin-strip__item { visibility: hidden; }}"""
        self.assertTrue(valid_css(css))
        for injection in ("@import url(https://evil.example);", "<script>", "!important",
                          "@font-face", "url(data:image/svg+xml,ABC)"):
            with self.subTest(injection=injection):
                self.assertFalse(valid_css(css + injection))

    def test_request_guard_denies_writes_and_rights_unverified_binaries(self):
        self.assertTrue(denied("POST", "https://finalvestige.com/"))
        self.assertTrue(denied("PATCH", "https://finalvestige.com/wp-json/wp/v2/pages/6"))
        self.assertTrue(denied("GET", "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg?resize=320"))
        self.assertTrue(denied("GET", "ftp://example.com/file"))
        self.assertFalse(denied("GET", "https://finalvestige.com/"))
        self.assertFalse(denied("GET", "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/franklin.jpg"))


if __name__ == "__main__":
    unittest.main()
