#!/usr/bin/env python3
"""R190 optional JS regression tests; PHP WP-shim is NOT WordPress staging."""
import hashlib, json, subprocess, sys, tempfile, shutil, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r190 import build, EXPECTED
SRC=ROOT/'dist'
SHIM=ROOT/'qa/wp_lifecycle_mock.php'

class FailOpenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=build(reuse=True)
    def scenario(self,kind='normal',revision=190,state='normal'):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            if revision==190:
                shutil.copytree(SRC,folder/'plugin')
                plugin=folder/'plugin'
            else:
                shutil.copytree(ROOT.parent/'apollo-r189/dist',folder/'plugin')
                plugin=folder/'plugin'
            if kind=='missing-js': (plugin/'assets/campaign-handoff.js').unlink()
            elif kind=='bad-js': (plugin/'assets/campaign-handoff.js').write_text('/* tampered */')
            elif kind=='missing-css': (plugin/'assets/atlas-scoped.css').unlink()
            elif kind=='bad-html': (plugin/'templates/atlas-fragment.html').write_text('<p>tampered</p>')
            path=plugin/f'fv-ex2-apollo-r{revision}.php'
            p=subprocess.run(['php',str(SHIM),str(path),state],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            return json.loads(p.stdout)
    def test_build_is_pinned_to_historical_html(self):
        self.assertEqual(self.manifest['input_sha256'],EXPECTED)
        self.assertEqual(hashlib.sha256((SRC/'templates/atlas-fragment.html').read_bytes()).hexdigest(),EXPECTED['html'])
    def test_R189_negative_control_old_optional_js_not_optional(self):
        a=self.scenario('missing-js',revision=189)
        self.assertTrue(a['is_fallback'])
    def test_R190_normal_with_optional_context(self):
        a=self.scenario()
        self.assertTrue(a['is_evidence'])
        self.assertTrue(a['js_enqueued'])
        self.assertEqual(a['chronology_count'],4)
        self.assertEqual(a['source_details'],8)
    def test_R190_missing_js_retains_evidence_no_script(self):
        a=self.scenario('missing-js')
        self.assertTrue(a['is_evidence'])
        self.assertFalse(a['js_enqueued'])
        self.assertEqual(a['css_state'],'enqueued')
        self.assertTrue(a['campaign_not_embedded'])
    def test_R190_tampered_js_retains_evidence_no_script(self):
        a=self.scenario('bad-js')
        self.assertTrue(a['is_evidence'])
        self.assertFalse(a['js_enqueued'])
        self.assertEqual(a['chronology_count'],4)
    def test_R190_printed_stylesheet_remains_usable(self):
        for kind in ('normal','missing-js','bad-js'):
            with self.subTest(kind=kind):
                a=self.scenario(kind,state='printed')
                self.assertTrue(a['is_evidence'])
                self.assertEqual(a['css_state'],'done')
    def test_R190_missing_css_fallback(self):
        self.assertTrue(self.scenario('missing-css')['is_fallback'])
    def test_R190_tampered_html_fallback(self):
        self.assertTrue(self.scenario('bad-html')['is_fallback'])
    def test_unanticipated_late_render_fallback(self):
        self.assertTrue(self.scenario(state='late')['is_fallback'])
    def test_campaign_not_server_generated(self):
        p=(SRC/'fv-ex2-apollo-r190.php').read_text()
        self.assertNotIn('$_GET',p)
        self.assertNotIn('wp_insert_post(',p)
        self.assertNotIn('update_option(',p)
    def test_syntax(self):
        for args in (['php','-l',str(SRC/'fv-ex2-apollo-r190.php')],['php','-l',str(SHIM)],['node','--check',str(SRC/'assets/campaign-handoff.js')]):
            with self.subTest(args=args):
                p=subprocess.run(args,capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr+p.stdout)

if __name__=='__main__': unittest.main(verbosity=2)
