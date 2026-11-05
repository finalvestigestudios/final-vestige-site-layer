"""Offline structural checks for R145 HTML/plaintext review-only assets."""
import re
import unittest
from pathlib import Path
D=Path(__file__).parent
class PreviewGuards(unittest.TestCase):
    def html(self,i):return (D/(i+'-OFFLINE-REVIEW-ONLY.html')).read_text('utf-8')
    def txt(self,i):return (D/(i+'-OFFLINE-REVIEW-ONLY.txt')).read_text('utf-8')
    def test_lang(self):
        for i in ('03','05'):self.assertIn('<html lang="en">',self.html(i))
    def test_viewport(self):
        for i in ('03','05'):self.assertIn('name="viewport"',self.html(i))
    def test_table_layout(self):
        for i in ('03','05'):self.assertIn('role="presentation"',self.html(i))
    def test_mobile_breaking(self):
        for i in ('03','05'):self.assertIn('overflow-wrap:anywhere;word-break:break-word',self.html(i))
    def test_single_heading(self):
        for i in ('03','05'):self.assertEqual(self.html(i).count('<h1 '),1)
    def test_not_an_active_merchant_link(self):
        for i in ('03','05'):self.assertNotRegex(self.html(i),r'<a\s+[^>]*href=')
    def test_no_script_or_images(self):
        for i in ('03','05'):self.assertNotRegex(self.html(i),r'<script|<iframe|<img|onclick\s*=')
    def test_source_disclosure(self):
        for i in ('03','05'):self.assertIn('Commercial disclosure',self.html(i))
    def test_one_blocked_offer(self):
        for i in ('03','05'):self.assertEqual(self.html(i).count('GUIDE NOT APPROVED'),1)
    def test_legal_release_block(self):
        for i in ('03','05'):
            self.assertIn('POSTAL_ADDRESS_REQUIRED',self.html(i))
            self.assertIn('UNSUBSCRIBE_REQUIRED',self.html(i))
    def test_text_never_mail(self):
        for i in ('03','05'):
            self.assertIn('NEVER MAIL',self.txt(i))
            self.assertIn('APPROVED_LIVE_',self.txt(i))
    def test_no_fake_revenue(self):
        for i in ('03','05'):self.assertNotRegex(self.html(i),r'(?i)realized net revenue\s*=\s*\$')
if __name__=='__main__': unittest.main()
