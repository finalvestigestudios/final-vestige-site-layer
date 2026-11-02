"""Source-level integration gates for source-controlled Observer Lab."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[1]
class ObserverIntegration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.i=(R/'index.html').read_text(encoding='utf-8')
  cls.h=(R/'observer-lab.html').read_text(encoding='utf-8')
  cls.c=(R/'observer-lab.css').read_text(encoding='utf-8')
  cls.j=(R/'observer-lab.js').read_text(encoding='utf-8')
 def test_navigation(self):
  self.assertEqual(self.i.count('id="fv-hf-observer"'),1)
  self.assertEqual(self.i.count('href="#fv-hf-observer"'),1)
  self.assertIn('<span>07</span> The observer',self.i)
 def test_asset_load_once(self):
  self.assertEqual(self.i.count('href="./observer-lab.css"'),1)
  self.assertEqual(self.i.count('src="./observer-lab.js"'),1)
 def test_existing_chapters_survive(self):
  for n in ('fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-mind-title','https://finalvestige.com/focus/'):
   self.assertIn(n,self.i)
 def test_nojs_and_aria(self):
  self.assertIn('<details class="fv-hf__observer-reveal"',self.h)
  self.assertEqual(self.h.count('data-fv-observer-frame='),2)
  self.assertIn('data-fv-observer-controls hidden',self.h)
  self.assertIn('frame.hidden = false',self.j)
  self.assertIn('aria-pressed',self.j)
 def test_sources_and_scope(self):
  self.assertIn('10.1111/j.1467-9280.1997.tb00427.x',self.h)
  self.assertIn('10.3758/BF03208840',self.h)
  self.assertIn('NOT ARCHIVAL RECORDS',self.h)
  self.assertIn('prefers-reduced-motion',self.c)
  self.assertIn('focus-visible',self.c)
  self.assertNotIn('https://inspire3.com/',self.i)
if __name__=='__main__':unittest.main()
