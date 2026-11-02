"""R75 adversarial print-regression tests (no license assertions)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import fitz
from pypdf import PdfReader
from wp_pdf_custody_r74 import verify_rendered_pdf_bytes
from wp_pdf_pagination_r75 import visual_page_classification, prepare_review_pdf


class VisualPrintPageTests(unittest.TestCase):
    def test_empty_and_light_decoration_detected(self):
        with fitz.open() as doc:
            page = doc.new_page(width=595, height=842)
            self.assertTrue(visual_page_classification(page)["decorative_only"])
            page.draw_rect(fitz.Rect(0, 0, 595, 18),
                           fill=(.93, .93, .93), color=None)
            self.assertTrue(visual_page_classification(page)["decorative_only"])

    def test_dark_diagram_without_text_cannot_be_trimmed(self):
        with fitz.open() as doc:
            page = doc.new_page()
            page.draw_line((10, 100), (400, 100), color=(0, 0, 0), width=5)
            self.assertFalse(visual_page_classification(page)["decorative_only"])

    def test_text_and_links_cannot_be_trimmed(self):
        with fitz.open() as doc:
            page = doc.new_page()
            page.insert_text((35, 50), "NASA source-custody legend")
            self.assertFalse(visual_page_classification(page)["decorative_only"])
            page2 = doc.new_page()
            page2.insert_link({"kind": fitz.LINK_URI,
                               "from": fitz.Rect(10, 10, 80, 30),
                               "uri": "https://www.nasa.gov/"})
            # MuPDF materializes link dictionaries after serialization.
            with fitz.open(stream=doc.tobytes(), filetype="pdf") as saved:
                self.assertFalse(visual_page_classification(saved[1])["decorative_only"])

    def test_non_source_pdf_rejected(self):
        with fitz.open() as doc:
            doc.new_page()
            with self.assertRaisesRegex(
                AssertionError, "R74_(NOT_A_REAL_PDF|PRINT_PDF_CATALOG_MISSING)"
            ):
                prepare_review_pdf(doc.tobytes())

    def test_original_r74_pdf_deterministic_source_safe_review(self):
        # The original binary is an independently verified CI artifact, not a
        # fixture committed into this source repository. Absence is explicit.
        fixture = Path(__file__).resolve().parents[3] / "R74_AUTHENTIC_WP_PRINT_1440.pdf"
        if not fixture.is_file():
            self.skipTest("Original R74 CI PDF unavailable locally")
        raw = fixture.read_bytes()
        self.assertEqual(verify_rendered_pdf_bytes(raw)["page_count"], 21)
        with tempfile.TemporaryDirectory() as tmp:
            clean, report = prepare_review_pdf(raw, Path(tmp) / "R75_REVIEW.pdf")
            clean2, report2 = prepare_review_pdf(raw)
            self.assertEqual(clean, clean2)
            self.assertEqual(report, report2)
            self.assertEqual(report["original_pages"], 21)
            self.assertEqual(report["review_pages"], 20)
            self.assertEqual(report["trimmed_terminal_decorative_pages"], 1)
            self.assertTrue(report["source_custody_reverified"])
            self.assertFalse(report["original_browser_print_defect_resolved"])
            self.assertEqual(len(PdfReader(Path(tmp) / "R75_REVIEW.pdf").pages), 20)


if __name__ == "__main__":
    unittest.main()
