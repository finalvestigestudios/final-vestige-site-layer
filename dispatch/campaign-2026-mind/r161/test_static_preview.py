"""R161 offline static email-safety QA: NO network, no sends, no subscribers."""
from pathlib import Path
from html.parser import HTMLParser
import unittest

HTML = Path(__file__).with_name('issue03-static-review-preview.html')

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]; self.props=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag); self.props.append((tag,dict(attrs)))

class StaticHTMLGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=HTML.read_text(encoding='utf-8')
        cls.dom=Parser();cls.dom.feed(cls.html)

    def test_no_active_email_or_tracking_actions(self):
        for banned in ('script','iframe','form','input','img','a','video','audio'):
            self.assertNotIn(banned,self.dom.tags)
        self.assertNotIn('utm_source=',self.html)
        self.assertNotIn('clickbank',self.html.lower())

    def test_real_holds_and_pricing_removed(self):
        for term in ('HOLD UNSENT','NOT JETPACK RENDERING','[[APPROVED_LIVE_ZEN12_PRESELL_GUIDE_URL_REQUIRED]]','[[VALID_POSTAL_ADDRESS_REQUIRED]]','[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'):
            self.assertIn(term,self.html)
        self.assertNotIn('$87',self.html)
        self.assertNotIn('91% off',self.html)
        self.assertEqual(self.html.count('CTA RESERVED — NOT ACTIVE'),1)

    def test_semantics(self):
        self.assertEqual(self.dom.tags.count('h1'),1)
        self.assertIn('html',self.dom.tags)
        self.assertTrue(any(tag=='html' and att.get('lang')=='en' for tag,att in self.dom.props))
        self.assertTrue(any(tag=='table' and att.get('role')=='presentation' for tag,att in self.dom.props))
        self.assertIn('table-layout:fixed',self.html)
        self.assertIn('overflow-wrap:anywhere',self.html)

    def test_offline_chromium_four_viewports(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
            try:
                for width in (320,390,768,1440):
                    page=browser.new_page(viewport={'width':width,'height':800})
                    page.set_content(self.html,wait_until='load')
                    self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'),width)
                    self.assertEqual(page.locator('a,script,form,input,img').count(),0,width)
                    self.assertEqual(page.get_by_text('CTA RESERVED — NOT ACTIVE').count(),1,width)
                    page.close()
            finally:
                browser.close()

if __name__ == '__main__':
    unittest.main(verbosity=2)
