"""Strict local source custody and fail-open integration contracts, not installed WP acceptance."""
import hashlib, re, shutil, subprocess, tempfile, unittest
from pathlib import Path

THIS=Path(__file__).resolve()
ROOT=THIS.parents[2]
JOURNEY=THIS.parents[1]
ENTRY=THIS.parent/'fixture.php'
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
DEPENDENCIES={
 'apollo-r440/staging-educator-intent.php',
 'apollo-r440/assets/educator-intent.css',
 'apollo-r440/assets/educator-intent.js',
 'apollo-r440/product_evidence.json',
 'apollo-r448/crosswalk.php',
 'apollo-r448/assets/crosswalk.css',
 'apollo-r448/assets/crosswalk.js',
 'apollo-r448/manifest.json',
}
def php(path,mode='staging'):
    p=subprocess.run(['php',str(path),mode],capture_output=True,text=True,check=False,timeout=15)
    if p.returncode: raise AssertionError(p.stderr[:1000]);return p.stdout

def output(path,mode='staging'):
    p=subprocess.run(['php',str(path),mode],capture_output=True,text=True,timeout=15)
    assert p.returncode==0, p.stderr[:1000]
    return p.stdout

class Integration(unittest.TestCase):
    def test_php_lint(self):
        for f in [JOURNEY/'journey.php',ENTRY]:
            q=subprocess.run(['php','-l',str(f)],capture_output=True,text=True)
            self.assertEqual(q.returncode,0,q.stderr)
    def test_exact_eight_dependencies_and_pins(self):
        source=(JOURNEY/'journey.php').read_text()
        self.assertEqual(len(DEPENDENCIES),8)
        for path in DEPENDENCIES:
            content=(ROOT/path).read_bytes()
            self.assertIn(hashlib.sha256(content).hexdigest(),source,path)
            self.assertTrue(content)
        self.assertIn(hashlib.sha256((JOURNEY/'assets/journey.css').read_bytes()).hexdigest(),source)
    def test_composition_single_cta_and_sources(self):
        html=output(ENTRY)
        self.assertEqual(html.count(f'href="{ARTICLE}"'),1)
        self.assertEqual(html.count('data-fv-r448-card data-era='),4)
        self.assertEqual(html.count('<section class="fv-r440" data-r440-root'),1)
        self.assertIn('Download original classroom exercise',html)
        for target in ('report-of-the-apollo-204-review-board/','50-years-ago-apollo-flammability-tests/','nasa-brand-center/images-and-media/'):
            self.assertIn(target,html)
        self.assertNotIn('data-fv-r447',html)
        self.assertNotRegex(html,r'<form\b|<iframe\b|paypal|payhip|stripe\.com')
    def test_staging_page_and_release_gates(self):
        for mode in ('production','not-enabled','wrong-page'):
            with self.subTest(mode=mode):
                html=output(ENTRY,mode)
                self.assertNotIn('data-fv-r449',html)
                self.assertEqual(html.count(f'href="{ARTICLE}"'),1)
    def test_multi_instance_ids_unique(self):
        html=output(ENTRY,'double')
        self.assertEqual(html.count('data-fv-r449'),2)
        self.assertEqual(html.count('data-fv-r448-card data-era='),8)
        self.assertEqual(html.count(f'href="{ARTICLE}"'),2)
        ids=re.findall(r'\bid="([^"]+)"',html)
        self.assertEqual(len(ids),len(set(ids)))
    def test_each_mutation_fails_open(self):
        # Mutate every individually pinned file in an isolated temporary copy.
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'experience2'
            for folder in ('apollo-r440','apollo-r448','apollo-r449'):
                shutil.copytree(ROOT/folder,base/folder)
            self.assertIn('data-fv-r449',output(base/'apollo-r449/qa/fixture.php'))
            for relative in sorted(DEPENDENCIES|{'apollo-r449/assets/journey.css'}):
                with self.subTest(relative=relative):
                    p=base/relative;original=p.read_bytes();p.write_bytes(original+b'\nTAMPER')
                    html=output(base/'apollo-r449/qa/fixture.php')
                    self.assertNotIn('data-fv-r449',html)
                    self.assertEqual(html.count(f'href="{ARTICLE}"'),1)
                    p.write_bytes(original)
    def test_missing_dependency_fails_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'experience2'
            for folder in ('apollo-r440','apollo-r448','apollo-r449'):
                shutil.copytree(ROOT/folder,base/folder)
            path=base/'apollo-r448/manifest.json'; path.unlink()
            self.assertNotIn('data-fv-r449',output(base/'apollo-r449/qa/fixture.php'))
    def test_staging_url_preflight_rejects_unsafe_targets(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('r449_staging_gate',JOURNEY/'qa/staging_gate.py')
        gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
        good='https://staging.finalvestige.com/fv-apollo-preview/'
        origin='https://staging.finalvestige.com'
        self.assertTrue(gate.approved(good,origin))
        for bad in (
            'https://finalvestige.com/fv-apollo-preview/',
            'https://www.finalvestige.com/fv-apollo-preview/',
            'http://staging.finalvestige.com/fv-apollo-preview/',
            'https://staging.finalvestige.com:8080/fv-apollo-preview/',
            'https://staging.finalvestige.com:bad/fv-apollo-preview/',
            'https://staging.finalvestige.com@evil.example/fv-apollo-preview/',
            'https://staging.finalvestige.com/fv-apollo-preview/?checkout=1',
            'https://staging.finalvestige.com/',
            'https://staging.finalvestige.com.evil.example/fv-apollo-preview/',
        ):
            with self.subTest(url=bad):self.assertFalse(gate.approved(bad,origin))
    def test_commercial_status_hard_hold(self):
        import json
        offer=json.loads((ROOT/'apollo-r440/product_evidence.json').read_text())
        self.assertEqual(offer['verification_status'],'HOLD_NOT_SELLABLE')
        for k in ('merchant_seller_identity_verified','specific_paid_sku_verified','payment_checkout_verified',
                  'deliverable_fulfillment_verified','original_content_rights_verified','founder_approved_paid_launch'):
            self.assertIs(offer[k],False)
        self.assertIsNone(offer['paid_checkout_url'])

if __name__=='__main__':unittest.main(verbosity=2)
