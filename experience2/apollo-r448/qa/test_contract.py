"""R448 fail-open source custody and WordPress staging guards. Run: python -m unittest discover -s qa -p 'test_*.py'."""
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def php(code):
    return subprocess.run(['php','-r',code],text=True,capture_output=True,check=True).stdout

class Contract(unittest.TestCase):
    def test_lint(self):
        for x in ('crosswalk.php','qa/fixture.php'):
            p=subprocess.run(['php','-l',str(ROOT/x)],text=True,capture_output=True)
            self.assertEqual(0,p.returncode,p.stderr)
    def test_signed_source_and_assets(self):
        s=(ROOT/'crosswalk.php').read_text()
        for rel in ('manifest.json','assets/crosswalk.css','assets/crosswalk.js'):
            self.assertIn(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),s)
    def test_curated_source_types(self):
        d=json.loads((ROOT/'manifest.json').read_text())
        self.assertEqual(['training','review-board','memorial','flammability'],[r['id'] for r in d['claims']]);self.assertEqual(4,len(d['claims']))
        self.assertEqual(['before','event','later','later'],[r['era'] for r in d['claims']])
        self.assertTrue(all(r['source_url'].startswith('https://www.nasa.gov/') for r in d['claims']))
        self.assertEqual('PENDING_INDEPENDENT_QD',d['editorial_approval']);self.assertFalse(d['release_approved'])
    def test_1967_not_confused_with_2017(self):
        d=json.loads((ROOT/'manifest.json').read_text())['claims']
        self.assertIn('Board report written afterward',d[1]['date_context'])
        self.assertIn('fifty years later',d[2]['title'].lower())
        self.assertIn('not 1967 accident footage',d[2]['not_supported'])
        self.assertIn('do not isolate',d[3]['not_supported'])
    def test_claims_have_limits_and_custody(self):
        d=json.loads((ROOT/'manifest.json').read_text())
        self.assertTrue(all(len(c['not_supported'])>35 and len(c['rights'])>35 for c in d['claims']))
    def test_exact_cta_and_all_records_rendered(self):
        out=subprocess.check_output(['php',str(ROOT/'qa/fixture.php')],text=True)
        self.assertEqual(1,out.count('Read the full Apollo 1 investigation</a>'))
        self.assertEqual(4,out.count('data-fv-r448-card data-era='))
        self.assertEqual(4,out.count('Open source and custody notes'))
        self.assertEqual(0,out.lower().count('<img'))
        self.assertEqual(0,out.lower().count('<iframe'))
        self.assertEqual(0,out.lower().count('<form'))
        self.assertEqual(4,out.count('Read source:'))
    def test_no_staging_registration_in_production(self):
        p=json.dumps(str(ROOT/'crosswalk.php'))
        code=f'''define("ABSPATH",true);function add_shortcode($n,$c){{echo $n;}}function wp_get_environment_type(){{return "production";}}define("FV_APOLLO_R448_ENABLE_STAGING",true);require {p};'''
        self.assertEqual('',php(code))
    def test_staging_must_optin(self):
        p=json.dumps(str(ROOT/'crosswalk.php'))
        code=f'''define("ABSPATH",true);function add_shortcode($n,$c){{echo $n;}}function wp_get_environment_type(){{return "staging";}}require {p};'''
        self.assertEqual('',php(code))
    def test_staging_registration(self):
        p=json.dumps(str(ROOT/'crosswalk.php'))
        code=f'''define("ABSPATH",true);function add_shortcode($n,$c){{echo $n;}}function wp_get_environment_type(){{return "staging";}}define("FV_APOLLO_R448_ENABLE_STAGING",true);require {p};'''
        self.assertEqual('fv_apollo_claim_crosswalk',php(code))
    def test_duplicate_instances(self):
        out=subprocess.check_output(['php',str(ROOT/'qa/fixture.php'),'--duplicate'],text=True)
        self.assertIn('fv-r448-1-title',out);self.assertIn('fv-r448-2-title',out)
    def test_no_external_telemetry_or_geo(self):
        js=(ROOT/'assets/crosswalk.js').read_text();phptext=(ROOT/'crosswalk.php').read_text().lower()
        for s in ['fetch(', 'XMLHttpRequest','sendBeacon','localStorage','sessionStorage','document.cookie','new Image(']:self.assertNotIn(s,js)
        for s in ['mapbox','leaflet','geojson','data-lat','data-long','payhip','stripe','checkout'] :self.assertNotIn(s,phptext)
    def test_tampered_manifest_fails_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);shutil.copy(ROOT/'crosswalk.php',d);shutil.copy(ROOT/'manifest.json',d)
            m=json.loads((d/'manifest.json').read_text());m['release_approved']=True;(d/'manifest.json').write_text(json.dumps(m))
            out=php(f'require {json.dumps(str(d/"crosswalk.php"))};echo fv_r448_render();')
            self.assertIn('free Apollo 1 investigation',out);self.assertNotIn('<section',out)
    def test_missing_manifest_fails_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);shutil.copy(ROOT/'crosswalk.php',d)
            out=php(f'require {json.dumps(str(d/"crosswalk.php"))};echo fv_r448_render();')
            self.assertIn('free Apollo 1 investigation',out)
    def test_tampered_css_fails_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);shutil.copy(ROOT/'crosswalk.php',d);shutil.copy(ROOT/'manifest.json',d)
            (d/'assets').mkdir();shutil.copy(ROOT/'assets/crosswalk.js',d/'assets/crosswalk.js')
            (d/'assets/crosswalk.css').write_text('malicious new CSS')
            out=php(f'require {json.dumps(str(d/"crosswalk.php"))};echo fv_r448_render();')
            self.assertIn('free Apollo 1 investigation',out)
    def test_approved_origin_not_redirectable(self):
        s=(ROOT/'qa/staging_gate.py').read_text()
        self.assertIn('approved-origin',s);self.assertIn('redirect',s)
    def test_source_policy_in_readme(self):
        s=(ROOT/'README.md').read_text()
        self.assertIn('HARD HOLD',s);self.assertIn('#150',s);self.assertIn('#820',s)

if __name__=='__main__':unittest.main()
