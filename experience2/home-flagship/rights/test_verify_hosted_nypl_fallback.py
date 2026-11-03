"""Adversarial release-gate tests; browser integration runs only in CI."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_hosted_nypl_fallback import WIDTHS, HOST, NYPL_FILE, grade, refuse_request


def case(width: int) -> dict:
    return {
        "width": width,
        "status": 200,
        "host": HOST,
        "chapters": 7,
        "margins": 72,
        "focus_links": 4,
        "catalog_links_after": 2,
        "images_before": 4,
        "images_after": 3,
        "horizontal_overflow_after": False,
        "candidate": {
            "image_count_before": 1,
            "image_count_after": 0,
            "nypl_file_absent": True,
            "original_claim_absent": True,
            "corrected_credit_present": True,
            "fallback_text_visible": True,
            "fallback_within_case": True,
            "frame_relabelled": True,
            "source_heading_retained": True,
            "source_details_retained": True,
            "catalog_links_in_case": 1,
        },
        "screenshots": {"before": "a" * 64, "after": "b" * 64},
    }


class HostedRightsSafeCandidateTests(unittest.TestCase):
    def setUp(self):
        self.cases = [case(w) for w in WIDTHS]

    def test_pass_is_scope_limited(self):
        g = grade(self.cases)
        self.assertEqual(g["read_only_hosted_candidate_visual"], "PASS")
        self.assertEqual(g["production_release"], "HOLD")
        self.assertEqual(g["complete_wcag_22_aa"], "HOLD")
        self.assertEqual(g["exact_wordpress_raw_python_transformer_execution"], "NOT_TESTED")

    def test_missing_width_is_not_success(self):
        with self.assertRaises(ValueError):
            grade(self.cases[:-1])

    def test_duplicate_width_is_not_success(self):
        broken = copy.deepcopy(self.cases)
        broken[1]["width"] = broken[0]["width"]
        with self.assertRaises(ValueError):
            grade(broken)

    def test_missing_archival_image_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[1]["images_before"] = 3
        with self.assertRaises(ValueError):
            grade(broken)

    def test_lost_72_margins_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[0]["margins"] = 71
        with self.assertRaises(ValueError):
            grade(broken)

    def test_lost_focus_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[2]["focus_links"] = 0
        with self.assertRaises(ValueError):
            grade(broken)

    def test_lost_chapter_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[0]["chapters"] = 6
        with self.assertRaises(ValueError):
            grade(broken)

    def test_missing_catalog_links_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[3]["catalog_links_after"] = 1
        with self.assertRaises(ValueError):
            grade(broken)

    def test_unverified_public_domain_claim_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[-1]["candidate"]["original_claim_absent"] = False
        with self.assertRaises(ValueError):
            grade(broken)

    def test_fallback_clipping_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[0]["candidate"]["fallback_within_case"] = False
        with self.assertRaises(ValueError):
            grade(broken)

    def test_unsafe_screenshot_manifest_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[0]["screenshots"]["before"] = "garbage"
        with self.assertRaises(ValueError):
            grade(broken)

    def test_unexpected_host_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[4]["host"] = "evil.example"
        with self.assertRaises(ValueError):
            grade(broken)

    def test_overflow_is_blocked(self):
        broken = copy.deepcopy(self.cases)
        broken[0]["horizontal_overflow_after"] = True
        with self.assertRaises(ValueError):
            grade(broken)

    def test_nypl_binary_is_blocked_at_route(self):
        self.assertTrue(refuse_request("GET", f"https://i0.wp.com/foo/{NYPL_FILE}?fit=768"))
        self.assertTrue(refuse_request("GET", f"https://finalvestige.com/foo/{NYPL_FILE}"))

    def test_server_writes_are_refused(self):
        self.assertTrue(refuse_request("POST", "https://finalvestige.com/wp-json/wp/v2/pages/6"))
        self.assertTrue(refuse_request("PATCH", "https://finalvestige.com/"))
        self.assertTrue(refuse_request("DELETE", "https://finalvestige.com/"))

    def test_untrusted_protocol_refused(self):
        self.assertTrue(refuse_request("GET", "javascript:alert(1)"))
        self.assertTrue(refuse_request("GET", "http://finalvestige.com/"))
        self.assertTrue(refuse_request("GET", "not a url"))

    def test_normal_public_media_allowed(self):
        self.assertFalse(refuse_request("GET", "https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp"))


if __name__ == "__main__":
    unittest.main()
