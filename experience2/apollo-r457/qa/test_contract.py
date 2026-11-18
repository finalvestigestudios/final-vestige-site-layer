#!/usr/bin/env python3
"""R457 source custody and no-promotion guard contract. No network use."""
import json, re, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'apollo_rights_gallery.php'
def php(code):
  p=subprocess.run(['php','-r',f'require {json.dumps(str(PHP))}; {code}'],capture_output=True,text=True)
  if p.returncode:raise RuntimeError(p.stderr)
  return p.stdout
class Contract(unittest.TestCase):
 def test_lint(self):self.assertIn('No syntax errors',subprocess.check_output(['php','-l',str(PHP)],text=True))
 def test_valid_records(self):self.assertEqual(php('echo fv457_valid(fv457_records())?"yes":"no";'),'yes')
 def test_exact_six(self):self.assertEqual(php('echo count(fv457_records());'),'6')
 def test_exact_three_shown(self):self.assertEqual(php('echo count(array_filter(fv457_records(),fn($r)=>$r["shown"]));'),'3')
 def test_duplicate_invalid(self):self.assertEqual(php('$r=fv457_records();$r[1]["id"]=$r[0]["id"];echo fv457_valid($r)?"bad":"safe";'),'safe')
 def test_bad_date_invalid(self):self.assertEqual(php('$r=fv457_records();$r[1]["date"]="1967-02-30";echo fv457_valid($r)?"bad":"safe";'),'safe')
 def test_fake_nasa_invalid(self):self.assertEqual(php('$r=fv457_records();$r[1]["source_url"]="https://www.nasa.gov.evil.example/x";echo fv457_valid($r)?"bad":"safe";'),'safe')
 def test_credentials_invalid(self):self.assertEqual(php('$r=fv457_records();$r[1]["source_url"]="https://hacker@www.nasa.gov/x";echo fv457_valid($r)?"bad":"safe";'),'safe')
 def test_query_invalid(self):self.assertEqual(php('$r=fv457_records();$r[1]["source_url"].="?track=1";echo fv457_valid($r)?"bad":"safe";'),'safe')
 def test_no_fake_day(self):self.assertIn('January 1967 (day not established here)',php('echo fv457_render();'))
 def test_unverified_2017_catalogue(self):self.assertIn('could not be independently retrieved',php('echo fv457_render();'))
 def test_no_embedded_image(self):self.assertNotRegex(php('echo fv457_render();'),r'<img\b')
 def test_one_article_cta(self):self.assertEqual(php('echo substr_count(fv457_render(),"https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/");'),'1')
 def test_unique_instances(self):
  x=php('echo fv457_render().fv457_render();')
  self.assertIn('id="fv457-1"',x);self.assertIn('id="fv457-2"',x)
 def test_all_six_sources_linked(self):self.assertEqual(php('echo substr_count(fv457_render(),"NASA record for ");'),'6')
 def test_different_images_status_not_clearance(self):self.assertIn('Page placement is not image-use permission',php('echo fv457_render();'))
 def test_no_analytics(self):self.assertNotRegex(php('echo fv457_render();').lower(),r'google-analytics|gtag\(|facebook\.com/tr|checkout|stripe\.com|paypal\.com')
 def test_homepage_confirmation_is_one_only(self):
  self.assertEqual(php('echo count(array_filter(fv457_records(),fn($r)=>($r["homepage_confirmed"]??false)));'),'1')
 def test_cannot_claim_homepage_is_atlas(self):
  self.assertEqual(php('$r=fv457_records();$r[2]["shown"]=true;echo fv457_valid($r)?"bad":"safe";'),'safe')
 def test_filters_distinguish_scope(self):
  html=php('echo fv457_render();')
  self.assertIn('Confirmed homepage (1)',html)
  self.assertIn('Not in Atlas (3)',html)
  self.assertIn('Homepage presence or absence not independently established',html)
  self.assertNotIn('Withheld on live Atlas',html)
 def test_scripts_pinned_and_fallback(self):
  html=php('echo fv457_render();')
  self.assertIn('Six archival records across two published surfaces',html)
  p=ROOT/'assets/gallery.js';old=p.read_bytes()
  try:
   p.write_bytes(old+b'\n/* unexpected modification */')
   self.assertIn('temporarily unavailable',php('echo fv457_render();'))
  finally:p.write_bytes(old)
 def test_shortcode_disabled_default(self):self.assertNotIn('add_shortcode(',php('echo function_exists("add_shortcode")?"yes":"no";'))
if __name__=='__main__':unittest.main(verbosity=1)
