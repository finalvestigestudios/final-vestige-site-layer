"""Offline bounded assertions for a proposal fixture, not WordPress/CI certification."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
HTML = (HERE / 'observer_bridge_review.html').read_text(encoding='utf-8')

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set(); self.scripts=[]; self.forms=0; self.items=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs); self.items.append((tag,d))
        if tag=='a': self.links.append(d)
        if tag=='script': self.scripts.append(d)
        if tag=='form': self.forms+=1
        if 'id' in d:
            if d['id'] in self.ids: raise AssertionError('duplicate id')
            self.ids.add(d['id'])

class Gate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=Scan(); cls.p.feed(HTML)
    def test_no_external_scripts_or_forms(self): self.assertFalse(self.p.scripts); self.assertEqual(self.p.forms,0)
    def test_free_cta_is_canonical(self):
        a=[x for x in self.p.links if x.get('data-fv-destination')=='focus']; self.assertEqual(len(a),1); self.assertEqual(a[0]['href'],'https://finalvestige.com/focus/')
    def test_existing_history_path_preserved(self): self.assertEqual(sum('/free-resources/puysegurs-animal-magnetism-files/' in x['href'] for x in self.p.links),2)
    def test_primary_sources_accessible(self):
        self.assertTrue(any('10.1111/j.1467-9280.1997.tb00427.x' in a['href'] for a in self.p.links)); self.assertTrue(any('10.3758/BF03208840' in a['href'] for a in self.p.links))
    def test_no_affiliate_or_checkout(self): self.assertNotIn('payhip.com',HTML.lower());self.assertNotIn('inspire3.com',HTML.lower());self.assertNotIn('utm_',HTML.lower())
    def test_no_duplicate_subscription(self): self.assertNotIn('jetpack/subscriptions',HTML.lower())
    def test_aria_titles(self): self.assertIn('variant-title',self.p.ids); self.assertIn('control-label',self.p.ids)
    def test_motion_and_contrast(self): self.assertIn('prefers-reduced-motion:reduce',HTML);self.assertIn('forced-colors:active',HTML);self.assertIn(':focus-visible',HTML)
    def test_noindex_fixture(self): self.assertIn('noindex,nofollow',HTML)
    def test_no_claims_of_sales(self): self.assertIn('not be counted as paid conversion',HTML)

if __name__=='__main__':unittest.main()
