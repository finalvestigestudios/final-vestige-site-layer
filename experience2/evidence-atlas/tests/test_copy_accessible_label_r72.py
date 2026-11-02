"""R72 WCAG 2.5.3 six-button actual HTML source acceptance.

The visible Copy citation NN label must occur in that exact order at the
beginning of its programmatic accessible name. No NASA source record is
reworded or asserted cleared by this accessibility-only repair.
"""
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import build_atlas

class CopyButtons(HTMLParser):
    def __init__(self):
        super().__init__();self.open=None;self.buttons=[]
    def handle_starttag(self,tag,attrs):
        attributes=dict(attrs)
        if tag=='button' and 'data-fva-copy' in attributes:
            self.open={'label':attributes.get('aria-label',''),'visible':''}
    def handle_data(self,data):
        if self.open is not None:self.open['visible']+=data
    def handle_endtag(self,tag):
        if tag=='button' and self.open is not None:
            self.buttons.append(self.open);self.open=None

class R72CopyAccessibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html=build_atlas.make_html(build_atlas.validate_custody(),'','')
        cls.parser=CopyButtons();cls.parser.feed(html)
    def test_six_copy_buttons_have_visible_label_in_accessible_name(self):
        self.assertEqual(len(self.parser.buttons),6)
        for i,button in enumerate(self.parser.buttons,start=1):
            with self.subTest(index=i):
                expected=f'Copy citation {i:02d}'
                self.assertEqual(button['visible'].strip(),expected)
                self.assertTrue(button['label'].startswith(expected),button['label'])
                self.assertIn('NASA source',button['label'])
    def test_full_citations_remain_rights_pending(self):
        html=build_atlas.make_html(build_atlas.validate_custody(),'','')
        self.assertEqual(html.count('image reuse: individual review required.'),6)
        self.assertNotIn('rights-cleared',html)
        self.assertNotIn('<img ',html)
if __name__=='__main__':unittest.main()
