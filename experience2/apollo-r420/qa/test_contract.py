"""R420 exact PHP source / educator activity guard tests (no WP writes)."""
from pathlib import Path
import hashlib, os, subprocess, unittest
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PINS={
 ROOT.parent/'apollo-r419/staging-evidence-concordance.php':'0d300360c6614be9c189ef5d555e1f497c844582',
 ROOT/'assets/educator-lab.css':'f1a9a99571589697d313002b0daab534a93b305d',
}
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def render(mode='staging'):
 p=subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],env=dict(os.environ,FV_R420_MODE=mode),capture_output=True,text=True,check=True)
 return BeautifulSoup(p.stdout,'html.parser')
class Contracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.doc=render();cls.root=cls.doc.select_one('[data-fv-r420-lab]')
 def test_01_php_lint(self):
  for p in [ROOT/'staging-educator-source-lab.php', ROOT/'qa/render_fixture.php']:
   self.assertEqual(subprocess.run(['php','-l',str(p)],capture_output=True).returncode,0)
 def test_02_pinned_upstream_git_blobs(self):
  for p, expected in PINS.items():self.assertEqual(blob(p.read_bytes()),expected)
 def test_03_has_three_source_reasoning_cases(self):
  self.assertIsNotNone(self.root)
  cards=self.root.select('ol.fv-r420__questions > li')
  self.assertEqual(len(cards),3)
  self.assertEqual([c['id'].split('-')[-1] for c in cards],['01','02','03'])
 def test_04_three_distinct_questions_and_visible_boundaries(self):
  cards=self.root.select('.fv-r420__card')
  for c in cards:
   self.assertIn('Historical finding:',c.get_text(' ',strip=True))
   self.assertIn('Evidence limitation:',c.get_text(' ',strip=True))
   self.assertIn('Why the photo cannot settle this:',c.get_text(' ',strip=True))
   self.assertIn('Write your own source-grounded answer:',c.get_text(' ',strip=True))
   self.assertEqual(len(c.select('details > summary')),1)
 def test_05_exact_nasa_text_and_archive_records(self):
  cards=self.root.select('.fv-r420__card')
  self.assertEqual([a['href'] for a in cards[0].select('a[href]')],['https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','https://www.nasa.gov/image-detail/amf-s67-21294/'])
  self.assertEqual([a['href'] for a in cards[1].select('a[href]')],['https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/'])
  self.assertEqual([a['href'] for a in cards[2].select('a[href]')],['https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/'])
 def test_06_historical_uncertainty(self):
  c=self.root.select('.fv-r420__card')[0]
  self.assertIn('could not conclusively identify',c.get_text(' ',strip=True))
  self.assertIn('not a conclusively established cause',c.get_text(' ',strip=True))
 def test_07_later_tests_are_not_accident_data(self):
  c=self.root.select('.fv-r420__card')[2]
  self.assertIn('102 deliberate ignitions',c.get_text(' ',strip=True))
  self.assertIn('months after the accident',c.get_text(' ',strip=True))
  self.assertIn('24 January 2017',c.get_text(' ',strip=True))
 def test_08_museum_cannot_prove_1967_hatch(self):
  c=self.root.select('.fv-r420__card')[1]
  self.assertIn('24 January 2017',c.get_text(' ',strip=True))
  self.assertIn('cannot show the hatch being operated',c.get_text(' ',strip=True))
 def test_09_one_noncommercial_cta(self):
  self.assertEqual(len(self.root.select('.fv-r420__next')),1)
  self.assertEqual(self.root.select_one('.fv-r420__next')['href'],ARTICLE)
  self.assertEqual(len(self.root.select('a[href="'+ARTICLE+'"]')),1)
 def test_10_no_forms_scripts_media_invented_maps_or_tracking(self):
  for tag in ['img','picture','script','iframe','video','audio','canvas','svg','form','input','map','button']:
   self.assertFalse(self.root.select(tag),tag)
  links=[x['href'] for x in self.root.select('a[href]')]
  self.assertFalse(any('utm_' in x or 'payhip' in x or 'checkout' in x for x in links))
 def test_11_all_fragment_targets_and_ids_unique(self):
  ids=[x['id'] for x in self.root.select('[id]')]
  self.assertEqual(len(set(ids)),len(ids))
  for a in self.root.select('nav a'):
   self.assertEqual(len(self.root.select('[id="'+a['href'][1:]+'"]')),1)
 def test_12_unauthorized_contexts_fail_open_to_existing_article(self):
  for mode in ['production','archive','wrong-page','disabled']:
   d=render(mode)
   self.assertFalse(d.select('[data-fv-r420-lab]'),mode)
   self.assertEqual(len(d.select('a[href="'+ARTICLE+'"]')),1,mode)
 def test_13_duplicate_instances_unique_ids(self):
  d=render('double');self.assertEqual(len(d.select('[data-fv-r420-lab]')),2)
  ids=[x['id'] for x in d.select('[id]')]
  self.assertEqual(len(ids),len(set(ids)))
  self.assertEqual(len(d.select('.fv-r420__next')),2)
 def test_14_mutated_css_falls_back(self):
  p=ROOT/'assets/educator-lab.css';raw=p.read_bytes()
  try:
   p.write_bytes(raw+b'\n/* tamper */')
   self.assertFalse(render().select('[data-fv-r420-lab]'))
  finally:p.write_bytes(raw)
  self.assertEqual(blob(p.read_bytes()),PINS[p])
 def test_15_mutated_r419_source_falls_back(self):
  p=ROOT.parent/'apollo-r419/staging-evidence-concordance.php';raw=p.read_bytes()
  try:
   p.write_bytes(raw+b'\n// tamper')
   self.assertFalse(render().select('[data-fv-r420-lab]'))
  finally:p.write_bytes(raw)
  self.assertEqual(blob(p.read_bytes()),PINS[p])
if __name__=='__main__':unittest.main(verbosity=2)
