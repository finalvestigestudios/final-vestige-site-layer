"""Run: python -m unittest discover -s qa -p test_contract.py -v"""
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED=['crew-training','capsule-processing','accident-record','hatch-memorial']
class GalleryContract(unittest.TestCase):
    def test_php_lint(self):
        for f in [ROOT/'gallery.php',ROOT/'qa/fixture.php']:
            x=subprocess.run(['php','-l',str(f)],capture_output=True,text=True)
            self.assertEqual(0,x.returncode,x.stderr)
    def test_manifest_identity(self):
        txt=(ROOT/'gallery.php').read_text()
        checksum=hashlib.sha256((ROOT/'manifest.json').read_bytes()).hexdigest()
        self.assertIn(checksum,txt)
    def test_exact_four_sorted(self):
        d=json.loads((ROOT/'manifest.json').read_text())
        self.assertEqual(EXPECTED,[r['id'] for r in d['records']])
        self.assertEqual(sorted(r['date'] for r in d['records']),[r['date'] for r in d['records']])
        self.assertEqual(['before','before','event','later'],[r['stage'] for r in d['records']])
    def test_no_img_payload(self):
        html=self.render()
        self.assertNotIn('<img',html.lower());self.assertNotIn('<iframe',html.lower());self.assertNotIn('<form',html.lower())
        self.assertNotIn('paypal.com',html.lower());self.assertNotIn('payhip.com',html.lower())
    def test_four_source_links(self):
        html=self.render()
        self.assertEqual(4,html.count('View original NASA record:'))
        self.assertEqual(1,html.count('Read the full Apollo 1 investigation</a>'))
    def test_visible_without_script(self):
        html=self.render()
        self.assertEqual(4,html.count('data-fv-r447-card data-era='))
        self.assertEqual(4,html.count('<details>'))
        self.assertIn('data-fv-r447-controls hidden',html)
    def test_no_false_rights_claim(self):
        d=json.loads((ROOT/'manifest.json').read_text())
        self.assertFalse(d['offer_release_approved'])
        self.assertEqual('NOT_GRANTED',d['media_use_approval'])
        self.assertTrue(all('RIGHTS_' in r['media_state'] or r['media_state']=='NO_IMAGE_PRESENT' for r in d['records']))
    def test_allowlisted_uris_and_rights(self):
        d=json.loads((ROOT/'manifest.json').read_text())
        self.assertTrue(all(r['source_url'].startswith(('https://www.nasa.gov/','https://images.nasa.gov/')) for r in d['records']))
        self.assertIn('CATALOG_LINK_RECORDED_NOT_RECHECKED', [r['source_state'] for r in d['records']])
    def test_manifest_tampering_fails_open(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);shutil.copy(ROOT/'gallery.php',p);shutil.copy(ROOT/'manifest.json',p)
            original=json.loads((p/'manifest.json').read_text());original['offer_release_approved']=True
            (p/'manifest.json').write_text(json.dumps(original))
            x=subprocess.run(['php','-r',f'require {json.dumps(str(p/"gallery.php"))};echo fv_r447_render();'],capture_output=True,text=True)
            self.assertEqual(0,x.returncode,x.stderr)
            self.assertIn('free Apollo 1 investigation',x.stdout)
            self.assertNotIn('<section',x.stdout)
    def test_missing_manifest_fails_open(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);shutil.copy(ROOT/'gallery.php',p)
            x=subprocess.run(['php','-r',f'require {json.dumps(str(p/"gallery.php"))};echo fv_r447_render();'],capture_output=True,text=True)
            self.assertIn('free Apollo 1 investigation',x.stdout)
    def test_no_shortcode_on_production(self):
        code='''define("ABSPATH",1);function add_shortcode($n,$c){echo "REGISTERED:".$n;} function wp_get_environment_type(){return "production";} define("FV_APOLLO_R447_ENABLE_STAGING",true);require %s;'''%json.dumps(str(ROOT/'gallery.php'))
        x=subprocess.run(['php','-r',code],capture_output=True,text=True)
        self.assertEqual('',x.stdout)
    def test_staging_registration_explicit(self):
        code='''define("ABSPATH",1);function add_shortcode($n,$c){echo "REGISTERED:".$n;} function wp_get_environment_type(){return "staging";} define("FV_APOLLO_R447_ENABLE_STAGING",true);require %s;'''%json.dumps(str(ROOT/'gallery.php'))
        x=subprocess.run(['php','-r',code],capture_output=True,text=True)
        self.assertEqual('REGISTERED:fv_apollo_rights_gallery',x.stdout)
    def test_no_pii_or_tracking_hooks(self):
        js=(ROOT/'assets/gallery.js').read_text()
        for forbidden in ['fetch(','XMLHttpRequest','localStorage','sessionStorage','navigator.sendBeacon','document.cookie']:
            self.assertNotIn(forbidden,js)
    def test_no_speculative_geography(self):
        html=self.render()
        for term in ['data-lat','data-long','mapbox','leaflet','geojson']:
            self.assertNotIn(term,html.lower())
    def test_multiple_instances_unique_ids(self):
        html=self.render('--duplicate')
        self.assertIn('fv-r447-1-title',html);self.assertIn('fv-r447-2-title',html)
    def test_compiled_browser_qa_exists(self):
        import ast
        ast.parse((ROOT/'qa/browser_qa.py').read_text())
    @staticmethod
    def render(*extra):
        x=subprocess.run(['php',str(ROOT/'qa/fixture.php'),*extra],capture_output=True,text=True)
        if x.returncode:raise RuntimeError(x.stderr)
        return x.stdout
if __name__=='__main__':unittest.main()
