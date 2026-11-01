#!/usr/bin/env python3
"""R50 isolated PHP co-host contract tests; no live WordPress claims."""
import hashlib,json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PLUGIN=ROOT/'integration/fv-ex2-apollo-suite.php'
PROBE=ROOT/'tests/php_suite_r50_probe.php'

def git_blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def fixture():
    desk='<section data-fvx-ledger><h2 id="fv-ex2-ledger-apollo1-title">Desk</h2>'+''.join(
        f'<article data-fvx-record data-fvx-search="NASA {i}" id="fv-ex2-ledger-apollo1-record-{i:02}"></article>' for i in range(1,7))+'</section>'
    atlas='<section data-fva-atlas><h2 id="fva-title">Atlas</h2>'+''.join(
        f'<article data-fva-record data-fva-id="{i:02}"></article>' for i in range(1,7))+'</section>'
    return desk,atlas

def probe(desk,atlas):
    run=subprocess.run(['php',str(PROBE)],input=json.dumps({'desk':desk,'atlas':atlas}),text=True,capture_output=True)
    if run.returncode:raise AssertionError(run.stderr)
    return json.loads(run.stdout)
class SuiteTests(unittest.TestCase):
    def test_syntax(self):
        self.assertIn('No syntax errors',subprocess.run(['php','-l',str(PLUGIN)],capture_output=True,text=True,check=True).stdout)
    def test_exact_approved_sources_pinned(self):
        s=PLUGIN.read_text()
        for sha in ('d1879a90101b5475990132369178f42743f4b57c','403d128c57b9bc82dac7c619651689070edef86c','b8cf00afeceba115a9e9d19044fc11dcf2890cbe','32e757cc4dc8708397ff65ac21e89dd319781d78'):
            self.assertIn(sha,s)
        self.assertEqual(git_blob((ROOT/'tests/fixtures/source-ledger.pr158.js').read_bytes()),'32e757cc4dc8708397ff65ac21e89dd319781d78')
    def test_render_content_unchanged(self):
        r=probe(*fixture())
        for k in ('has_markup','research_link','atlas_link','desk_unmodified','atlas_unmodified','missing_plugin_guard','safe_fallback'):
            self.assertTrue(r[k],(k,r))
        self.assertEqual(r['heading_count'],1)
        self.assertEqual(r['git_blob_hello'],git_blob(b'hello\n'))
    def test_missing_records_fail_closed(self):
        d,a=fixture()
        self.assertFalse(probe(d.replace('data-fvx-record ', '',1),a)['has_markup'])
        self.assertFalse(probe(d,a.replace('data-fva-record ', '',1))['has_markup'])
    def test_duplicate_collection_fail_closed(self):
        d,a=fixture()
        self.assertFalse(probe(d+d,a)['has_markup'])
        self.assertFalse(probe(d,a+a)['has_markup'])
    def test_out_of_scope_features_absent(self):
        s=PLUGIN.read_text()
        for forbidden in ('wp_insert_post(', 'wp_update_post(', 'update_option(', 'wp_remote_get(', 'wp_remote_post('):
            self.assertNotIn(forbidden,s)
        self.assertIn("has_shortcode($post->post_content, 'fv_ex2_apollo_suite')",s)
        self.assertIn("plugins_url('apollo-suite.css', __FILE__)",s)
if __name__=='__main__':unittest.main()
