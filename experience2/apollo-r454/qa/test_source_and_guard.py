#!/usr/bin/env python3
"""Offline source contract: no claims of WordPress staging/paid publication/real revenue."""
from pathlib import Path
from subprocess import run
from html.parser import HTMLParser
import unittest, re, json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'apollo_evidence_lab.php'
class Gather(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.details=0;self.buttons=[];self.cards=0
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='a': self.links.append(d.get('href',''))
  if t=='details':self.details+=1
  if t=='button':self.buttons.append(d.get('data-fv454-filter',''))
  if t=='li' and 'data-fv454-group' in d:self.cards+=1

def render():
 p=run(['php','-r',f'require {json.dumps(str(SOURCE))}; echo fv454_render();'],capture_output=True,text=True,check=True)
 return p.stdout
class SourceGuard(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.html=render();cls.p=Gather();cls.p.feed(cls.html)
 def test_php_syntax(self):self.assertEqual(run(['php','-l',str(SOURCE)],capture_output=True).returncode,0)
 def test_four_evidence_records(self):self.assertEqual(self.p.cards,4)
 def test_four_native_disclosures(self):self.assertEqual(self.p.details,4)
 def test_three_source_filters(self):self.assertEqual(self.p.buttons,['all','primary','later'])
 def test_single_free_cta(self):self.assertEqual(sum('finalvestige.com' in x for x in self.p.links),1)
 def test_official_sources(self):self.assertEqual(sum(x.startswith('https://www.nasa.gov/') for x in self.p.links),4)
 def test_no_fabricated_map(self):self.assertNotIn('data-lat=',self.html);self.assertNotIn('data-lon=',self.html)
 def test_no_nasa_image(self):self.assertNotIn('<img',self.html);self.assertNotIn('<iframe',self.html)
 def test_no_payment_or_tracking(self):
  self.assertNotRegex(self.html,r'<form|<input|payhip\.com|stripe\.com|googletagmanager|gtag\(')
 def test_historical_limits(self):
  self.assertIn('No single ignition source was conclusively identified',self.html)
  self.assertIn('cannot prove the original spark',self.html)
 def test_no_js_meaning(self):self.assertEqual(self.html.count('data-fv454-group='),4)
 def test_staging_gate_present(self):
  t=SOURCE.read_text();self.assertIn("wp_get_environment_type() !== 'staging'",t);self.assertIn('FV_R454_STAGING_PAGE_ID',t)
 def test_registration_only_when_staging(self):
  s=f'''$shortcodes=[];function add_action($hook,$callback){{$callback();}} function add_shortcode($name,$callback){{global $shortcodes;$shortcodes[$name]=$callback;}} function wp_get_environment_type(){{return 'production';}} require {json.dumps(str(SOURCE))};echo count($shortcodes);'''
  self.assertEqual(run(['php','-r',s],capture_output=True,text=True,check=True).stdout,'0')
 def test_staging_registration_exact_page(self):
  s=f'''define('FV_R454_ENABLE_STAGING',true);define('FV_R454_STAGING_PAGE_ID',999);$shortcodes=[];function add_action($hook,$callback){{$callback();}} function add_shortcode($name,$callback){{global $shortcodes;$shortcodes[$name]=$callback;}} function wp_get_environment_type(){{return 'staging';}}function get_queried_object_id(){{return 22;}}require {json.dumps(str(SOURCE))};echo count($shortcodes).'|'.strlen($shortcodes['fv_apollo_evidence_lab_r454']());'''
  self.assertEqual(run(['php','-r',s],capture_output=True,text=True,check=True).stdout,'1|0')
if __name__=='__main__':unittest.main(verbosity=2)
