"""Unit gates for the SAME native WordPress admission used by the CLI runner.

These unit tests intentionally do not claim WordPress, axe or network acceptance.
"""
import unittest
from verify_integrated_playground import assert_semantics, verify_image_bytes
from verify_archival_provenance import classify_source, verify_receipt, MEDIA, ORIGIN, BASE


def passing_semantics():
    return {
        "wordpress_shell": True, "root": True, "chapters": [True] * 7,
        "record_count": 72, "focus_links": 5,
        "focus_first_screen": [{"in_first_screen": True, "hit_clear": True}],
        "image_count": 2, "overflow": 0, "has_review_label": True,
        "source_actions": 3,
        "archive_sources": [
            {"src": "https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp", "alt": "Apollo crew"},
            {"src": "https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg", "alt": "Franklin note"},
        ],
    }


class NativeAcceptanceControls(unittest.TestCase):
    def test_valid_semantics_and_contextual_focus_action(self):
        self.assertEqual(assert_semantics(passing_semantics()), [])

    def test_covered_focus_cta_fail_closed(self):
        m = passing_semantics()
        m["focus_first_screen"] = [{"in_first_screen": True, "hit_clear": False}]
        self.assertIn("no visible, unobstructed first-screen Focus CTA", assert_semantics(m))

    def test_offscreen_focus_cta_fail_closed(self):
        m = passing_semantics()
        m["focus_first_screen"] = [{"in_first_screen": False, "hit_clear": True}]
        self.assertIn("no visible, unobstructed first-screen Focus CTA", assert_semantics(m))

    def test_missing_focus_geometry_fail_closed(self):
        m = passing_semantics()
        del m["focus_first_screen"]
        self.assertIn("no visible, unobstructed first-screen Focus CTA", assert_semantics(m))

    def test_approved_source_and_approved_responsive_cdn(self):
        src = "https://" + ORIGIN + BASE + MEDIA[0]["file"]
        canonical = classify_source(src, src, 0)
        cdn = classify_source(src, "https://i0.wp.com/" + ORIGIN + BASE + MEDIA[0]["file"] + "?fit=300%2C233&ssl=1", 0)
        self.assertTrue(canonical["first_party"])
        self.assertFalse(cdn["first_party"])
        self.assertEqual(canonical["media_id"], 473)
        self.assertEqual(cdn["selected_size"], (300, 233))

    def test_substituted_archival_url_rejected(self):
        src = "https://" + ORIGIN + BASE + MEDIA[0]["file"]
        with self.assertRaises(ValueError):
            classify_source(src, "https://finalvestige.com/wp-content/uploads/2026/08/other.webp", 0)

    def test_real_transfer_receipt_requires_approved_metadata(self):
        src = "https://" + ORIGIN + BASE + MEDIA[0]["file"]
        approved = classify_source(src, src, 0)
        observation = {"format": "WEBP", "width": 1041, "height": 810, "bytes": 78346, "sha256": "a" * 64}
        receipt = verify_receipt(approved, observation, 200, "image/webp")
        self.assertEqual(receipt["transfer_bytes"], 78346)
        self.assertTrue(receipt["first_party"])
        for status, kind, payload in [
            (404, "image/webp", observation),
            (200, "text/html", observation),
            (200, "image/webp", {**observation, "width": 400}),
            (200, "image/webp", {**observation, "bytes": 0}),
        ]:
            with self.subTest(status=status,kind=kind,payload=payload), self.assertRaises(ValueError):
                verify_receipt(approved, payload, status, kind)

    def test_seven_chapters_and_margins_still_required(self):
        for key, invalid in (("chapters", [True] * 6), ("record_count", 71), ("image_count", 1)):
            with self.subTest(key=key):
                m = passing_semantics()
                m[key] = invalid
                self.assertNotEqual(assert_semantics(m), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
