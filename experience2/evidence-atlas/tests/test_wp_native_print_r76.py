"""R76 adversarial acceptance of real unmodified browser PDF pagination."""
import unittest
from unittest.mock import patch
import fitz
from wp_native_print_r76 import inspect_native_pdf


def pdf_from_pages(*kinds):
    with fitz.open() as doc:
        for kind in kinds:
            p = doc.new_page(width=595, height=842)
            if kind == 'text':
                p.insert_text((65,105), 'A verified source custody paragraph')
            elif kind == 'pale':
                p.draw_rect(fitz.Rect(0,0,595,30), color=None, fill=(.933,.933,.933))
            elif kind == 'drawing':
                p.draw_rect(fitz.Rect(45,70,550,470), color=(0,0,0), width=2)
        return doc.tobytes(no_new_id=True)


class TestNativePrint(unittest.TestCase):
    def test_terminal_gray_theme_spill_fails(self):
        raw=pdf_from_pages('text','pale')
        with patch('wp_native_print_r76.verify_rendered_pdf_bytes',return_value={'page_count':2,'catalog_ids':6,'nasa_urls':6}):
            with self.assertRaisesRegex(AssertionError, 'R76_NATIVE_TRAILING_DECORATIVE_PAGE'):
                inspect_native_pdf(raw)

    def test_real_terminal_text_preserved(self):
        raw=pdf_from_pages('text','text')
        with patch('wp_native_print_r76.verify_rendered_pdf_bytes',return_value={'page_count':2,'catalog_ids':6,'nasa_urls':6}):
            result=inspect_native_pdf(raw)
        self.assertEqual(result['native_pages'],2)
        self.assertFalse(result['terminal_decorative_only'])
        self.assertEqual(result['individual_rights_cleared'],0)

    def test_nontext_drawing_preserved(self):
        raw=pdf_from_pages('text','drawing')
        with patch('wp_native_print_r76.verify_rendered_pdf_bytes',return_value={'page_count':2,'catalog_ids':6,'nasa_urls':6}):
            self.assertEqual(inspect_native_pdf(raw)['native_pages'],2)

    def test_interior_decorative_page_fails(self):
        raw=pdf_from_pages('text','pale','text')
        with patch('wp_native_print_r76.verify_rendered_pdf_bytes',return_value={'page_count':3,'catalog_ids':6,'nasa_urls':6}):
            with self.assertRaisesRegex(AssertionError, 'R76_NATIVE_INTERIOR_DECORATIVE_PAGE'):
                inspect_native_pdf(raw)

    def test_source_pdf_rejects_unverified_blank(self):
        with self.assertRaisesRegex(AssertionError, 'R74_'):
            inspect_native_pdf(pdf_from_pages('text'))


if __name__ == '__main__':unittest.main()
