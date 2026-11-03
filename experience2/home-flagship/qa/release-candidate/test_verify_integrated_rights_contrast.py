"""Adversarial qualification for two unmerged fixes working in ONE actual-host page."""
import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_integrated_rights_contrast import (
    WIDTHS, AXE_WIDTHS, HOST, CONTRAST_CSS, css_checked, grade, refuse_request
)


def healthy():
    rows = []
    for width in WIDTHS:
        row = {
            "width": width, "http_status": 200, "host": HOST,
            "chapters": 7, "margins": 72, "focus_links": 5,
            "nypl_source_links": 2, "images_before": 3,
            "images_after": 2, "nypl_transferred_bytes": 0,
            "blocked_nypl_requests": 1, "blocked_non_get_requests": 0,
            "non_get_requests_allowed": 0, "overflow_after": False,
            "nypl": {
                "nypl_file_absent": True,
                "original_claim_absent": True,
                "corrected_credit_present": True,
                "fallback_text_visible": True,
                "fallback_within_case": True,
                "frame_label_single_line": True,
                "frame_date_single_line": True,
                "source_details_retained": True,
            },
            "margins_candidate": {
                "records_total": 72, "visible_count": 1,
                "visible_index": 0, "visible_opacity": 1,
                "visible_filter": "none", "contrast_css_applied": True,
            },
        }
        if width in AXE_WIDTHS:
            row.update({
                "axe_executed": True,
                "axe_color_contrast_violations": 0,
                "axe_color_contrast_incomplete": 0,
                "candidate_screenshot_sha256": "c" * 64,
            })
        rows.append(row)
    return rows


class IntegratedQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.digest = hashlib.sha256(css_checked().encode("utf-8")).hexdigest()

    def accept(self, rows):
        return grade(rows, self.digest)

    def test_complete_synthetic_receipt_remains_release_hold(self):
        r = self.accept(healthy())
        self.assertEqual(r["combined_hosted_ephemeral_candidate"], "PASS")
        self.assertEqual(r["production_release"], "HOLD")
        self.assertEqual(r["manual_wcag22_aa"], "HOLD")

    def test_pinned_source_stylesheet_is_real(self):
        self.assertTrue(CONTRAST_CSS.is_file())
        self.assertIn("fvMarginContrastSafe", css_checked())

    def test_invalid_stylesheet_never_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "unsafe.css"
            p.write_text(css_checked() + "\n@import url('https://example.org/x.css');")
            with self.assertRaises(ValueError):
                css_checked(p)

    def test_css_drift_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "missing.css"
            p.write_text(".fv-margin-strip__item {opacity: .42;}")
            with self.assertRaises(ValueError):
                css_checked(p)

    def test_missing_case_rejected(self):
        with self.assertRaisesRegex(ValueError, "WIDTH"):
            self.accept(healthy()[:-1])

    def test_duplicate_width_rejected(self):
        rows = healthy()
        rows[4]["width"] = 390
        with self.assertRaisesRegex(ValueError, "WIDTH"):
            self.accept(rows)

    def test_incorrect_source_count_rejected(self):
        rows = healthy()
        rows[0]["nypl_source_links"] = 1
        with self.assertRaisesRegex(ValueError, "WIDTH_320"):
            self.accept(rows)

    def test_record_loss_rejected(self):
        rows = healthy()
        rows[1]["margins"] = 71
        with self.assertRaisesRegex(ValueError, "WIDTH_390"):
            self.accept(rows)

    def test_low_opacity_rejected(self):
        rows = healthy()
        rows[1]["margins_candidate"]["visible_opacity"] = .42
        with self.assertRaisesRegex(ValueError, "WIDTH_390"):
            self.accept(rows)

    def test_two_simultaneously_visible_records_rejected(self):
        rows = healthy()
        rows[0]["margins_candidate"]["visible_count"] = 2
        with self.assertRaisesRegex(ValueError, "WIDTH_320"):
            self.accept(rows)

    def test_opaque_but_blurred_rejected(self):
        rows = healthy()
        rows[1]["margins_candidate"]["visible_filter"] = "blur(7px)"
        with self.assertRaisesRegex(ValueError, "WIDTH_390"):
            self.accept(rows)

    def test_nypl_image_not_withheld_rejected(self):
        rows = healthy()
        rows[2]["nypl"]["nypl_file_absent"] = False
        with self.assertRaisesRegex(ValueError, "WIDTH_768"):
            self.accept(rows)

    def test_nypl_bytes_rejected(self):
        rows = healthy()
        rows[-1]["nypl_transferred_bytes"] = 12
        with self.assertRaisesRegex(ValueError, "WIDTH_1920"):
            self.accept(rows)

    def test_unreadable_frame_rejected(self):
        rows = healthy()
        rows[0]["nypl"]["frame_date_single_line"] = False
        with self.assertRaisesRegex(ValueError, "WIDTH_320"):
            self.accept(rows)

    def test_missing_axe_rejected(self):
        rows = healthy()
        rows[1]["axe_executed"] = False
        with self.assertRaisesRegex(ValueError, "AXE"):
            self.accept(rows)

    def test_axe_incomplete_is_not_pass(self):
        rows = healthy()
        rows[3]["axe_color_contrast_incomplete"] = 1
        with self.assertRaisesRegex(ValueError, "AXE"):
            self.accept(rows)

    def test_contrast_violations_rejected(self):
        rows = healthy()
        rows[1]["axe_color_contrast_violations"] = 1
        with self.assertRaisesRegex(ValueError, "AXE"):
            self.accept(rows)

    def test_screenshot_custody_rejected(self):
        rows = healthy()
        rows[3]["candidate_screenshot_sha256"] = "missing"
        with self.assertRaisesRegex(ValueError, "SCREENSHOT"):
            self.accept(rows)

    def test_root_overflow_rejected(self):
        rows = healthy()
        rows[0]["overflow_after"] = True
        with self.assertRaisesRegex(ValueError, "WIDTH_320"):
            self.accept(rows)

    def test_no_nonget_requests_or_nypl_bytes_allowed(self):
        self.assertTrue(refuse_request("POST", "https://finalvestige.com/wp-json/"))
        self.assertTrue(refuse_request("GET", "https://i0.wp.com/finalvestige.com/wp-content/uploads/edit-017-v02-nypl-5003296-original.jpg"))
        self.assertTrue(refuse_request("GET", "http://finalvestige.com/"))
        self.assertFalse(refuse_request("GET", "https://finalvestige.com/"))


if __name__ == "__main__":
    unittest.main()
