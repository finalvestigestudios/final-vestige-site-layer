"""Source/integration governance for inquiry chapter."""
from pathlib import Path
from html.parser import HTMLParser
import re
import unittest
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'inquiry.html').read_text(encoding='utf-8')
CSS=(ROOT/'inquiry.css').read_text(encoding='utf-8')
INDEX=(ROOT/'index.html').read_text(encoding='utf-8')
class Parser(HTMLParser):
 def __init__(self):
  super().__init__();self.tags=[];self.ids=[];self.links=[];self.details=0;self.summaries=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag not in ('br','hr','img','meta','link','input'):self.tags.append(tag)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a':self.links.append(a.get('href'))
  if tag=='details':self.details+=1
  if tag=='summary':self.summaries+=1
 def handle_endtag(self,tag):
  if tag in ('br','hr','img','meta','link','input'):return
  if not self.tags or self.tags[-1]!=tag:raise ValueError((tag,self.tags[-3:]))
  self.tags.pop()
class InquirySourceContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=Parser();cls.p.feed(HTML)
 def test_nesting(self):self.assertFalse(self.p.tags)
 def test_native_disclosures(self):self.assertEqual((self.p.details,self.p.summaries),(3,3))
 def test_unique_anchor(self):self.assertEqual(self.p.ids.count('fv-hf-inquiry'),1)
 def test_direct_sources(self):self.assertEqual(len(self.p.links),7);self.assertTrue(all(urlparse(x).scheme=='https' for x in self.p.links))
 def test_zero_images_or_scripts(self):self.assertNotRegex(HTML,r'<(?:img|script|iframe|video|form)\b')
 def test_claim_boundaries(self):
  for s in ['does not establish what happened to every person','did not establish one definitive ignition source','cannot be treated as a surveyed diagram']:self.assertIn(s,HTML)
 def test_actual_sources(self):
  for s in ['www.rmg.co.uk','www.historymuseum.ca','www.nasa.gov','digitalcollections.nypl.org']:self.assertIn(s,HTML)
 def test_no_affiliate_claims(self):self.assertNotRegex(HTML.lower(),r'inspire3|zen12|hypnosis live|guaranteed|reprogram|buy now')
 def test_no_js_needed(self):self.assertIn('<details',HTML);self.assertNotIn('onclick=',HTML)
 def test_mobile_and_motion(self):self.assertIn('max-width:600px',CSS);self.assertIn('prefers-reduced-motion',CSS);self.assertIn('min-height:44px',CSS)
 def test_one_integration_and_six_chapters(self):
  self.assertEqual(INDEX.count('id="fv-hf-inquiry"'),1)
  self.assertEqual(INDEX.count('href="#fv-hf-inquiry"'),1)
  self.assertEqual(INDEX.count('<link rel="stylesheet" href="./inquiry.css">'),1)
  self.assertLess(INDEX.index('id="fv-hf-evidence"'),INDEX.index('id="fv-hf-inquiry"'))
  self.assertLess(INDEX.index('id="fv-hf-inquiry"'),INDEX.index('class="fv-hf__method"'))
  self.assertIn('07</span> The observer',INDEX)
 def test_focus_paths_preserved(self):
  for url in ['https://finalvestige.com/focus/','https://finalvestige.com/blog/','https://finalvestige.com/editorial-standards/']:self.assertIn(url,INDEX)
  self.assertNotIn('inspire3.com',INDEX)
 def test_original_scoped_style(self):
  self.assertNotIn('@import',CSS);self.assertIn('.fv-hf__inquiry',CSS)
if __name__=='__main__':unittest.main()
