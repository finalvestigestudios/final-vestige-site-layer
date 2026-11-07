#!/usr/bin/env python3
"""R186 structural regression tests; not a substitute for axe or installed WP."""
from pathlib import Path
import unittest, sys, hashlib, json, subprocess
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r186 import repair,source_verify,EXPECTED_R185_HTML,EXPECTED_R185_CSS,LANDMARKS,sha
BASE=ROOT.parent/'apollo-r185/dist'
OUT=ROOT/'dist'
class LandmarkTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(BASE/'templates/atlas-fragment.html').read_bytes()
  cls.css=(BASE/'assets/atlas-scoped.css').read_bytes()
  cls.fixed=(OUT/'templates/atlas-fragment.html').read_bytes()
  cls.soup=BeautifulSoup(cls.fixed,'html.parser')
 def test_pinned_parent(self):
  self.assertEqual(sha(self.raw),EXPECTED_R185_HTML)
  self.assertEqual(sha(self.css),EXPECTED_R185_CSS)
  source_verify(self.raw,self.css)
 def test_unchanged_evidence_and_urls(self):
  old=BeautifulSoup(self.raw,'html.parser'); new=self.soup
  self.assertEqual([(a.get('href'),a.get_text(' ',strip=True)) for a in old.select('a')],[(a.get('href'),a.get_text(' ',strip=True)) for a in new.select('a')])
  for sel,expected in [('.rail li',4),('.plate',4),('.source-card',4),('details',8),('a.cta',1)]:
   self.assertEqual(len(new.select(sel)),expected,sel)
  self.assertEqual(old.get_text(' ',strip=True),new.get_text(' ',strip=True))
  self.assertFalse(new.select('script,iframe,img,form'))
 def test_all_accessible_names_resolve(self):
  ids=[node['id'] for node in self.soup.select('[id]')]
  self.assertEqual(len(ids),len(set(ids)))
  for item in self.soup.select('[aria-labelledby]'):
   for ref in item['aria-labelledby'].split():self.assertIn(ref,ids,ref)
  self.assertEqual(len(self.soup.select('section[aria-labelledby]')),4)
 def test_exact_four_delta_only(self):
  old=self.raw.decode();actual=self.fixed.decode()
  for old_id,new_id in LANDMARKS.items():
   marker=f'aria-labelledby="{old_id}"'
   self.assertEqual(old.count(marker),1)
   old=old.replace(marker,f'aria-labelledby="{new_id}"',1)
  self.assertEqual(actual,old)
  self.assertEqual(repair(self.raw),self.fixed)
 def test_negative_controls_fail_closed(self):
  with self.assertRaises(ValueError):source_verify(self.raw+b'X',self.css)
  with self.assertRaises(ValueError):source_verify(self.raw,self.css+b'X')
  with self.assertRaises(ValueError):repair(self.raw.replace(b'aria-labelledby="page-title"',b'aria-labelledby="other"'))
 def test_php_and_asset_manifest(self):
  php=OUT/'fv-ex2-apollo-r186.php'
  subprocess.run(['php','-l',str(php)],capture_output=True,text=True,check=True)
  m=json.loads((OUT/'manifest.json').read_text())
  self.assertEqual(m['r186_fragment_sha256'],sha(self.fixed))
  self.assertEqual(m['r186_php_sha256'],sha(php.read_bytes()))
  self.assertIn(sha(self.fixed),php.read_text())
  self.assertIn('fv_ex2_r186_render',php.read_text())
 def test_new_shortcode_unchanged(self):
  php=(OUT/'fv-ex2-apollo-r186.php').read_text()
  self.assertIn("add_shortcode('fv_ex2_apollo_atlas'",php)
  self.assertNotIn('fv_ex2_r185_',php)
  self.assertIn('Read the original investigation',php)
  self.assertIn('wp_enqueue_scripts',php)
  self.assertIn("did_action('wp_head')",php)
if __name__=='__main__':unittest.main()
