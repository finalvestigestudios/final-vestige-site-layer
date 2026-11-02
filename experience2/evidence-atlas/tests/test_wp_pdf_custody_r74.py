"""R74 hostile PDF checks for silent suppression of closed SourceDrawers."""
import io
import unittest
from pypdf import PdfWriter
from wp_pdf_custody_r74 import verify_rendered_pdf_bytes


class TestRenderedCustody(unittest.TestCase):
    def test_rejects_non_pdf(self):
        with self.assertRaisesRegex(AssertionError, 'R74_NOT_A_REAL_PDF'):
            verify_rendered_pdf_bytes(b'<html><h1>not a PDF</h1></html>')

    def test_rejects_valid_but_empty_pdf(self):
        writer = PdfWriter()
        for _ in range(2):
            writer.add_blank_page(width=595, height=842)
        data = io.BytesIO()
        writer.write(data)
        with self.assertRaisesRegex(AssertionError, r'R74_(NOT_A_REAL_PDF|PRINT_PDF_CATALOG_MISSING)'):
            verify_rendered_pdf_bytes(data.getvalue())

    def test_catalog_and_url_custody_pins_have_six_distinct_items(self):
        from wp_pdf_custody_r74 import NASA_CATALOGS, NASA_LINKS
        self.assertEqual(len(NASA_CATALOGS), 6)
        self.assertEqual(len(set(NASA_CATALOGS)), 6)
        self.assertEqual(len(NASA_LINKS), 6)
        self.assertEqual(len(set(NASA_LINKS)), 6)
        self.assertTrue(all(u.startswith('https://www.nasa.gov/image-detail/') for u in NASA_LINKS))


if __name__ == '__main__':
    unittest.main()
