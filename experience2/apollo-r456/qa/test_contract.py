#!/usr/bin/env python3
"""Source integrity and safe staging contract; runs without WordPress or network."""
from pathlib import Path
import subprocess, tempfile, shutil, json, unittest
R=Path(__file__).resolve().parent.parent
PHP=R/'apollo_claim_review.php'

def php(code,base=PHP):
    return subprocess.run(['php','-r',f'require {json.dumps(str(base))};'+code],capture_output=True,text=True)

class Contract(unittest.TestCase):
    def test_php_lint(self):self.assertEqual(subprocess.run(['php','-l',str(PHP)],capture_output=True).returncode,0)
    def test_output(self):
        p=php('echo fv456_render();');self.assertEqual(p.returncode,0,p.stderr)
        html=p.stdout
        self.assertEqual(html.count('data-fv456-case='),3)
        self.assertEqual(html.count('https://www.nasa.gov/'),3)
        self.assertEqual(html.count('href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"'),1)
        self.assertEqual(html.count('<details>'),3)
        self.assertNotIn('<img',html)
        self.assertNotIn('<iframe',html)
        self.assertNotIn('dataLayer.push',html)
    def test_date_roles(self):
        p=php("echo json_encode(fv456_cases());");self.assertEqual(p.returncode,0)
        records=json.loads(p.stdout)
        self.assertEqual([x['date'] for x in records],['1967-01-27','2017-01-27','2018-02-14'])
        self.assertTrue(all('NASA' in x['role'] or 'NASA' in x['source'] for x in records))
    def test_no_claim_of_certain_wire(self):
        h=php('echo fv456_render();').stdout
        self.assertIn('did not identify one ignition source conclusively',h)
        self.assertIn('later experiments cannot identify the original spark',h)
    def test_bad_domain(self):
        for url in ['https://nasa.gov/fake','https://www.nasa.gov.evil.test/a','https://evil.test@www.nasa.gov/a','http://www.nasa.gov/a','https://www.nasa.gov/a?leak=1','https://www.nasa.gov/a#test']:
            p=php('''$a=fv456_cases();$a[0]['url']=%s;echo fv456_valid($a)?'YES':'NO';'''%json.dumps(url))
            self.assertEqual(p.stdout,'NO',url)
    def test_duplicates(self):
        p=php("$a=fv456_cases();$a[1]['id']=$a[0]['id'];echo fv456_valid($a)?'YES':'NO';")
        self.assertEqual(p.stdout,'NO')
    def test_out_of_order(self):
        p=php("$a=fv456_cases();$a[1]['date']='1966-04-01';echo fv456_valid($a)?'YES':'NO';")
        self.assertEqual(p.stdout,'NO')
    def test_impossible_date(self):
        p=php("$a=fv456_cases();$a[1]['date']='2017-02-30';echo fv456_valid($a)?'YES':'NO';")
        self.assertEqual(p.stdout,'NO')
    def test_failed_assets_fail_open(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);(t/'assets').mkdir();shutil.copy2(PHP,t/PHP.name)
            for asset in (R/'assets').iterdir():shutil.copy2(asset,t/'assets'/asset.name)
            self.assertIn('data-fv456-root',php('echo fv456_render();',t/PHP.name).stdout)
            (t/'assets'/'claims.js').write_text('/* corrupted */')
            h=php('echo fv456_render();',t/PHP.name).stdout
            self.assertIn('Read the free Apollo 1 investigation',h)
            self.assertNotIn('data-fv456-root',h)
    def test_environment_gate_is_staging_explicit(self):
        s=PHP.read_text()
        for token in ('FV_R456_ENABLE_STAGING','FV_R456_STAGING_PAGE_ID',"wp_get_environment_type()!=='staging'",'get_queried_object_id()','add_shortcode'):
            self.assertIn(token,s)
    def test_no_external_assets(self):
        s=PHP.read_text()
        self.assertNotIn('wp_remote_get(',s);self.assertNotIn('wp_insert_post(',s);self.assertNotIn('setcookie(',s)
        self.assertIn('hash_equals(',s)

if __name__=='__main__':unittest.main(verbosity=2)
