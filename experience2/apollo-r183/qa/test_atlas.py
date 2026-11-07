"""R183 source contract, exact reconstructed HTML and negative controls. No network or CMS writes."""
import importlib.util, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from bs4 import BeautifulSoup
P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r183_reconstruct',P/'reconstruct_atlas.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class AtlasContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.p=Path(cls.tmp.name)/'atlas.html'
  assert mod.reconstruct(cls.p)==mod.EXPECTED_SHA256
  cls.s=BeautifulSoup(cls.p.read_text(), 'html.parser')
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_four_dates_and_order(self):
  ts=[x['datetime'] for x in self.s.select('.rail time')]
  self.assertEqual(ts,['1966-10-18','1967-01-03','1967-01-27','1967-01-28'])
 def test_evidence_and_gallery(self):
  self.assertEqual((len(self.s.select('.plate')),len(self.s.select('.source-card'))),(4,4))
 def test_native_nojs_details(self):self.assertEqual(len(self.s.select('details summary')),8)
 def test_no_external_scripts_images_maps(self):
  self.assertFalse(self.s.select('script,iframe,img,video,audio,[data-lat],[data-map-pin],form'))
 def test_exact_one_reading_cta(self):
  links=[a.get('href') for a in self.s.select('a[href]')]
  self.assertEqual(links.count('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'),1)
  self.assertEqual(len(self.s.select('a.cta')),1)
 def test_photo_source_links_nasa(self):
  for c in self.s.select('.source-card'):
   self.assertTrue(c.select('a[href]'))
   for a in c.select('a[href]'):self.assertTrue(a['href'].startswith('https://www.nasa.gov/'))
 def test_limitations_present(self):
  text=self.s.get_text(' ',strip=True).lower()
  for required in ('not conclusively','unverified match','not certified for','no purchase'):
   self.assertIn(required,text)
 def test_bad_checksum_rejected(self):
  with patch.object(mod,'EXPECTED_SHA256','0'*64):
   with tempfile.TemporaryDirectory() as d:
    dst=Path(d)/'bad.html'
    with self.assertRaises(ValueError):mod.reconstruct(dst)
    self.assertFalse(dst.exists())
 def test_bad_payload_rejected(self):
  with patch.object(mod,'PAYLOAD','corrupted'):
   with tempfile.TemporaryDirectory() as d:
    with self.assertRaises(Exception):mod.reconstruct(Path(d)/'bad.html')
 def test_no_offtopic_checkout_or_merchant(self):
  urls=[a['href'] for a in self.s.select('a[href]')]
  self.assertFalse(any(any(x in u for x in ('payhip.com','awin1.com','amazon.com')) for u in urls))
if __name__=='__main__':unittest.main()
