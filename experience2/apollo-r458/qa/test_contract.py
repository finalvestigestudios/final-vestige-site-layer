#!/usr/bin/env python3
"""R458 deterministic, offline PHP source/rights/offer contract with adversarial mutations."""
import json,re,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'apollo_custody_bridge.php'
def php(code):
    result=subprocess.run(['php','-r',f'require {json.dumps(str(PHP))}; {code}'],capture_output=True,text=True,timeout=12)
    if result.returncode: raise RuntimeError(result.stderr)
    return result.stdout
class SourceContract(unittest.TestCase):
 def test_php_lint(self):self.assertIn('No syntax errors',subprocess.check_output(['php','-l',str(PHP)],text=True))
 def test_records_valid(self):self.assertEqual(php('echo fv458_valid(fv458_records(),fv458_placement())?"pass":"fail";'),'pass')
 def test_chronology_count(self):self.assertEqual(php('echo count(fv458_records());'),'5')
 def test_distinct_roles(self):self.assertEqual(php('echo count(array_filter(fv458_records(),fn($r)=>$r["period"]==="historical"));'),'3')
 def test_urls_spoof_blocked(self):
  for url in ['https://www.nasa.gov.evil.test/anything','http://www.nasa.gov/a','https://evil.test/a','https://x@www.nasa.gov/a','https://www.nasa.gov:444/a','https://www.nasa.gov/a?x=1','https://www.nasa.gov/a#z']:
   self.assertEqual(php('$r=fv458_records();$r[0]["url"]='+json.dumps(url)+';echo fv458_valid($r,fv458_placement())?"BAD":"SAFE";'),'SAFE',url)
 def test_duplicate_ids_fail(self):self.assertEqual(php('$r=fv458_records();$r[1]["id"]=$r[0]["id"];echo fv458_valid($r,fv458_placement())?"BAD":"SAFE";'),'SAFE')
 def test_bad_dates_fail(self):self.assertEqual(php('$r=fv458_records();$r[1]["date"]="1967-02-30";echo fv458_valid($r,fv458_placement())?"BAD":"SAFE";'),'SAFE')
 def test_reverse_dates_fail(self):self.assertEqual(php('$r=fv458_records();$r[3]["date"]="1967-01-01";echo fv458_valid($r,fv458_placement())?"BAD":"SAFE";'),'SAFE')
 def test_missing_limit_fails(self):self.assertEqual(php('$r=fv458_records();unset($r[0]["limit"]);echo fv458_valid($r,fv458_placement())?"BAD":"SAFE";'),'SAFE')
 def test_status_mutation_fails(self):self.assertEqual(php('$p=fv458_placement();$p["status"]="LICENSED";echo fv458_valid(fv458_records(),$p)?"BAD":"SAFE";'),'SAFE')
 def test_source_count(self):self.assertEqual(php('echo substr_count(fv458_render(),"<a data-fv458-source");'),'5')
 def test_single_contextual_cta(self):self.assertEqual(php('echo substr_count(fv458_render(),"Read the complete free investigation");'),'1')
 def test_plaintext_study_no_form(self):
  s=php('echo fv458_render();');self.assertNotIn('<form',s.lower());self.assertNotIn('<img',s.lower());self.assertNotIn('<iframe',s.lower());self.assertNotIn('payhip',s.lower())
 def test_factual_rights_language(self):
  s=php('echo fv458_render();');self.assertIn('not a licensing judgment',s);self.assertIn('not permission',s);self.assertIn('commercial',s)
 def test_staging_registration_only(self):
  s=PHP.read_text();self.assertIn("wp_get_environment_type()!=='staging'",s);self.assertIn('FV_R458_STAGING_PAGE_ID',s);self.assertIn('FV_R458_ENABLE_STAGING',s)
 def test_asset_hashes_and_fallback(self):
  self.assertEqual(php('echo fv458_assets()!==null?"pass":"fail";'),'pass')
  self.assertIn('temporarily unavailable',php('echo fv458_fallback();'))
 def test_escape_injection(self):self.assertEqual(php('echo fv458_e("<script>alert(1)</script>");'),'&lt;script&gt;alert(1)&lt;/script&gt;')
 def test_isolated_namespace(self):self.assertNotIn('fv457_',PHP.read_text())
 def test_no_geo_or_network_scripts(self):
  s=PHP.read_text()+ (ROOT/'assets/bridge.js').read_text();
  for banned in ['fetch(', 'XMLHttpRequest','google-analytics','gtag(', 'latitude','longitude','localStorage','sessionStorage']:
   self.assertNotIn(banned,s)
if __name__=='__main__':unittest.main(verbosity=2)
