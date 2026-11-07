#!/usr/bin/env python3
"""Source custody, no-JS content and regression acceptance for R188."""
import subprocess,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r188 import build,sha,PINS,OUT,PREV
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.receipt=build()
  cls.html=(OUT/'templates/atlas-fragment.html').read_text()
  cls.php=(OUT/'fv-ex2-apollo-r188.php').read_text()
 def test_source_sha(self):
  self.assertEqual(sha((PREV/'fv-ex2-apollo-r187.php').read_bytes()),PINS['php'])
  self.assertEqual(sha((OUT/'templates/atlas-fragment.html').read_bytes()),PINS['html'])
  self.assertEqual(sha((OUT/'assets/atlas-scoped.css').read_bytes()),PINS['css'])
 def test_primary_records(self):
  for token in ('S66-58038','S67-15717','S67-21294','No conclusively identified ignition source'):
   self.assertIn(token,self.html)
 def test_single_free_cta(self):
  self.assertEqual(self.html.count('class="cta"'),1)
  self.assertIn('Read original investigation',self.html)
 def test_php_has_only_one_handoff(self):
  self.assertEqual(self.php.count('function fv_ex2_r188_campaign_handoff('),1)
  self.assertEqual(self.php.count('return fv_ex2_r188_campaign_handoff($html);'),1)
 def test_no_new_monitoring_or_commerce(self):
  for token in ('gtag(','fbq(','checkout','wp_insert_post(','update_option('):
   self.assertNotIn(token,self.php.lower())
 def test_php_syntax(self):
  p=subprocess.run(['php','-l',str(OUT/'fv-ex2-apollo-r188.php')],capture_output=True,text=True)
  self.assertEqual(p.returncode,0,p.stderr)
 def test_false_revenue_never_claimed(self):
  self.assertFalse(self.receipt['paid_orders_verified'])
  self.assertFalse(self.receipt['grok_asset_verified'])
if __name__=='__main__':unittest.main(verbosity=2)
