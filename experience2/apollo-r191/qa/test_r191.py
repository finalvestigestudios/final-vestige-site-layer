#!/usr/bin/env python3
"""R191 proof: real PHP adapter output with print custody, integrity fail-open."""
import hashlib,json,subprocess,sys,tempfile,shutil,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from build_r191 import build,URLS,PINS,digest
DIST=ROOT/'dist'
class PrintedCustodyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.manifest=build()
 def render(self,alter=None,mode='normal'):
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp)/'plugin';shutil.copytree(DIST,folder)
   if alter=='css':(folder/'assets/atlas-scoped.css').write_text('tampered')
   if alter=='html':(folder/'templates/atlas-fragment.html').write_text('tampered')
   if alter=='js':(folder/'assets/campaign-handoff.js').write_text('tampered')
   p=subprocess.run(['php',str(ROOT/'qa/wp_render_shim.php'),str(folder/'fv-ex2-apollo-r191.php'),mode],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stderr)
   return json.loads(p.stdout)
 def test_r190_source_exact_pins(self):self.assertEqual(self.manifest['parent_pins'],PINS)
 def test_html_css_js_pins_in_php(self):
  p=(DIST/'fv-ex2-apollo-r191.php').read_text()
  for key in ('html','css','js'):self.assertIn(self.manifest['output_sha256'][key],p)
 def test_source_index_all_exact_urls_and_print_literal(self):
  text=(DIST/'templates/atlas-fragment.html').read_text()
  appendix=text.split('<!-- R191 print-only source custody')[1].split('<footer class="end">')[0]
  self.assertEqual(appendix.count('<li>'),8)
  for _,url in URLS:
   self.assertIn('href="'+url+'"',appendix);self.assertIn('>'+url+'</a>',appendix)
  self.assertIn('rel="noreferrer noopener"',appendix)
 def test_all_normal_historical_evidence_kept(self):
  r=self.render();self.assertFalse(r['fallback']);self.assertEqual(r['chronology'],4)
  self.assertEqual(r['details'],8);self.assertTrue(r['js']);self.assertEqual(r['css'],'enqueued')
 def test_printed_css_accepted(self):
  r=self.render(mode='printed');self.assertFalse(r['fallback']);self.assertEqual(r['css'],'done')
 def test_no_unstyled_late_render(self):self.assertTrue(self.render(mode='late')['fallback'])
 def test_missing_or_modified_core_falls_back(self):
  for t in ('css','html'):
   with self.subTest(t=t):self.assertTrue(self.render(alter=t)['fallback'])
 def test_optional_js_tampering_keeps_source_index(self):
  r=self.render(alter='js');self.assertFalse(r['fallback']);self.assertFalse(r['js'])
  self.assertIn('Archival source and rights index',r['html'])
 def test_no_scripts_or_merchant_links_added(self):
  h=(DIST/'templates/atlas-fragment.html').read_text()
  self.assertEqual(h.count('class="cta"'),1)
  self.assertNotIn('awin1.com',h);self.assertNotIn('payhip.com',h)
  self.assertNotIn('src="https://',h)
 def test_syntax(self):
  for cmd in (['php','-l',str(DIST/'fv-ex2-apollo-r191.php')],['php','-l',str(ROOT/'qa/wp_render_shim.php')],['node','--check',str(DIST/'assets/campaign-handoff.js')]):
   r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__':unittest.main(verbosity=2)
