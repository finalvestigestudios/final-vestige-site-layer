#!/usr/bin/env python3
"""R446 source-based PHP/adversarial contract. Synthetic campaigns are TEST FIXTURES, never published Grok assets."""
import hashlib, json, re, subprocess, unittest
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/'apollo-r445/bridge.php'
REAL='utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo_pilot_2026_11&utm_content=AbCdE_12345'
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def php(stmt):
    return subprocess.run(['php','-r',"require "+json.dumps(str(ROOT/'handoff.php'))+"; "+stmt],text=True,capture_output=True)

def render(query):
    r=php('echo fv_r446_render('+json.dumps(query)+');')
    if r.returncode:raise AssertionError(r.stderr)
    return BeautifulSoup(r.stdout,'html.parser')

def synthetic(post_url='https://www.youtube.com/watch?v=example',**patch):
    asset=dict(asset_id='AbCdE_12345',platform='youtube',medium='organic_social',campaign='apollo_pilot_2026_11',
        review_status='VERIFIED_PUBLISHED',rights_review='PASS',placement_review='PASS',landing_review='PASS',
        reviewer='TEST_ONLY',published_at='2026-11-17T20:00:00-08:00',post_url=post_url)
    asset.update(patch)
    return dict(schema='fv-apollo-creator-custody-v1',status='APPROVED_STAGING_ASSETS',
                production_release_approved=False,campaign_handoff_reviewed=True,assets=[asset])

def approved(query, data):
    r=php('require_once '+json.dumps(str(PARENT))+'; echo json_encode(fv_r446_authorized_campaign('+json.dumps(query)+',json_decode('+json.dumps(json.dumps(data))+',true)));')
    if r.returncode:raise AssertionError(r.stderr)
    return json.loads(r.stdout)

class Contract(unittest.TestCase):
    def test_syntax(self):
        for file in [ROOT/'handoff.php',ROOT/'qa/fixture.php']:
            r=subprocess.run(['php','-l',str(file)],text=True,capture_output=True)
            self.assertEqual(r.returncode,0,r.stderr)
    def test_pinned_parent(self):
        src=(ROOT/'handoff.php').read_text()
        expected=re.search(r"FV_R446_PARENT_SHA256 = '([0-9a-f]{64})'",src).group(1)
        self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),expected)
    def test_pinned_registry(self):
        src=(ROOT/'handoff.php').read_text()
        expected=re.search(r"FV_R446_REGISTRY_SHA256 = '([0-9a-f]{64})'",src).group(1)
        self.assertEqual(hashlib.sha256((ROOT/'registry.json').read_bytes()).hexdigest(),expected)
    def test_no_real_asset_registry(self):
        r=json.loads((ROOT/'registry.json').read_text())
        self.assertEqual(r['assets'],[])
        self.assertFalse(r['campaign_handoff_reviewed'])
        self.assertFalse(r['production_release_approved'])
    def test_untagged_when_qualifying_syntax_only(self):
        soup=render(REAL)
        self.assertEqual(soup.select_one('.fv-r444__next a')['href'],DEST)
    def test_existing_nasa_proof_preserved(self):
        soup=render(REAL)
        self.assertEqual(len(soup.select('[data-r444-record]')),5)
        self.assertEqual(len(soup.select('a[href^="https://www.nasa.gov/"]')),5)
        self.assertEqual(len(soup.select('.fv-r444__next a')),1)
        self.assertEqual(len(soup.select('details')),5)
    def test_no_trackers_checkout_or_geo(self):
        s=render(REAL)
        self.assertEqual(len(s.select('script,iframe,form,[data-lat],[data-long],[data-geo]')),0)
        self.assertNotIn('AbCdE_12345',str(s))
        self.assertFalse(any('checkout' in x.get('href','') for x in s.select('a')))
    def test_synthetic_approved_fixture_allows_tag(self):
        self.assertEqual(approved(REAL,synthetic())['utm_content'],'AbCdE_12345')
    def test_synthetic_provenance_not_in_live_registry(self):
        self.assertNotIn('TEST_ONLY',(ROOT/'registry.json').read_text())
    def test_partial_grok_handoff_denied(self):
        d=synthetic();d['campaign_handoff_reviewed']=False
        self.assertIsNone(approved(REAL,d))
    def test_status_held_denied(self):
        d=synthetic();d['status']='HOLD_NO_VERIFIED_GROK_APOLLO_ASSETS'
        self.assertIsNone(approved(REAL,d))
    def test_missing_rights_denied(self):self.assertIsNone(approved(REAL,synthetic(rights_review='PENDING')))
    def test_missing_landing_denied(self):self.assertIsNone(approved(REAL,synthetic(landing_review='UNKNOWN')))
    def test_missing_publish_proof_denied(self):self.assertIsNone(approved(REAL,synthetic(published_at='')))
    def test_spoofed_youtube_domain_denied(self):
        self.assertIsNone(approved(REAL,synthetic('https://www.youtube.com.evil.example/watch?v=x')))
    def test_non_https_denied(self):self.assertIsNone(approved(REAL,synthetic('http://www.youtube.com/watch?v=x')))
    def test_embedded_credentials_denied(self):self.assertIsNone(approved(REAL,synthetic('https://name:pw@www.youtube.com/watch?v=x')))
    def test_duplicate_asset_entries_denied(self):
        d=synthetic();d['assets'].append(d['assets'][0].copy())
        self.assertIsNone(approved(REAL,d))
    def test_mismatched_platform_denied(self):self.assertIsNone(approved(REAL,synthetic(platform='tiktok')))
    def test_mismatched_campaign_denied(self):self.assertIsNone(approved(REAL,synthetic(campaign='apollo_pilot_2026_10')))
    def test_malformed_utm_denied(self):self.assertIsNone(approved(REAL+'&utm_content=spoof',synthetic()))
    def test_malicious_xss_denied(self):
        s=render(REAL.replace('AbCdE_12345','%22%3E%3Cscript%3Eevil()%3C/script%3E'))
        self.assertEqual(len(s.select('script')),0)
        self.assertEqual(s.select_one('.fv-r444__next a')['href'],DEST)
    def test_no_query_pii_in_output(self):self.assertNotIn('privateemail',str(render(REAL+'&email=privateemail')))
    def test_manipulated_registry_does_not_tag(self):
        f=ROOT/'registry.json';original=f.read_bytes()
        try:
            f.write_bytes(original+b' ')
            self.assertEqual(render(REAL).select_one('.fv-r444__next a')['href'],DEST)
        finally:f.write_bytes(original)
    def test_tampered_parent_fails_open(self):
        b=PARENT.read_bytes()
        try:
            PARENT.write_bytes(b+b'\n/* modified */')
            soup=render(REAL)
            self.assertIn('preview unavailable',soup.get_text(' ').lower())
            self.assertEqual(soup.select_one('a')['href'],DEST)
        finally:PARENT.write_bytes(b)
    def test_wordpress_prod_never_registers(self):
        code=f"define('ABSPATH','/');function wp_get_environment_type(){{return 'production';}} function add_shortcode($a,$b){{echo 'REGISTERED';}} define('FV_APOLLO_R446_ENABLE_STAGING',true);require {json.dumps(str(ROOT/'handoff.php'))};echo 'SAFE';"
        r=subprocess.run(['php','-r',code],capture_output=True,text=True)
        self.assertEqual(r.stdout,'SAFE')
    def test_staging_optin_registers_one_shortcode(self):
        code=f"define('ABSPATH','/');function wp_get_environment_type(){{return 'staging';}} function add_shortcode($a,$b){{echo $a;}} function add_action($a,$b,$p=10){{echo '|HOOK:'.$a;}}define('FV_APOLLO_R446_ENABLE_STAGING',true);require {json.dumps(str(ROOT/'handoff.php'))};"
        r=subprocess.run(['php','-r',code],capture_output=True,text=True)
        self.assertEqual(r.stdout,'|HOOK:wp_enqueue_scriptsfv_apollo_verified_creator_bridge')
    def test_staging_no_optin_denied(self):
        code=f"define('ABSPATH','/');function wp_get_environment_type(){{return 'staging';}} function add_shortcode($a,$b){{echo 'BAD';}} require {json.dumps(str(ROOT/'handoff.php'))};echo 'SAFE';"
        r=subprocess.run(['php','-r',code],capture_output=True,text=True)
        self.assertEqual(r.stdout,'SAFE')

if __name__=='__main__':unittest.main(verbosity=2)
