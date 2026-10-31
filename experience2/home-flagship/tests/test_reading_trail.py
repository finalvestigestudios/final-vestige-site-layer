"""Reading Trail source-contract regressions for exact Experience 2.0 checkout."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
IDS=['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']

class ReadingTrailRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=(ROOT/'index.html').read_text()
        cls.css=(ROOT/'reading-trail.css').read_text()
        cls.js=(ROOT/'reading-trail.js').read_text()
    def test_canonical_seven_chapter_route_preserved(self):
        for chapter in IDS:
            self.assertIn('href="#'+chapter+'"',self.index)
            self.assertIn(chapter,self.js)
    def test_script_and_css_loaded_locally(self):
        self.assertIn('href="./reading-trail.css"',self.index)
        self.assertIn('src="./reading-trail.js" defer',self.index)
        self.assertNotIn('@import',self.css)
        self.assertNotIn('https://',self.js+self.css)
    def test_no_js_story_not_hidden(self):
        self.assertIn('data-fv-trail-enhanced',self.css)
        self.assertNotIn('display:none',self.css.replace(' ',''))
        self.assertNotIn('innerHTML',self.js)
    def test_keyboard_focus_and_navigation(self):
        self.assertIn('event.detail !== 0',self.js)
        self.assertIn('target.focus({ preventScroll: true })',self.js)
        self.assertIn('aria-current',self.js)
        self.assertIn('tabindex',self.js)
    def test_motion_and_privacy(self):
        self.assertIn('prefers-reduced-motion: reduce',self.css)
        self.assertIn('requestAnimationFrame',self.js)
        self.assertNotIn('localStorage',self.js)
        self.assertNotIn('sendBeacon',self.js)
        self.assertNotIn('fetch(',self.js)
    def test_contract_builder_includes_new_assets(self):
        checker=(ROOT/'qa/integration/check_contract.py').read_text()
        self.assertIn('"reading-trail.css"',checker)
        self.assertIn('"reading-trail.js"',checker)
if __name__=='__main__':unittest.main()
