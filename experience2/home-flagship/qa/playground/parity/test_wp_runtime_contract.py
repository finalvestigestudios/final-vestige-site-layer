"""Exercise actual local parity importer logic with isolated WordPress API stubs.

Only two absolute filesystem paths (bootstrap and manifest) are substituted in
a temporary COPY. These are contract tests, NOT a running WordPress instance.
No production CMS, browser, subscriber data, network, or settings are accessed.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
IMPORTER = HERE / 'apply_local_parity.php'

WP_STUB = r'''<?php
$mode = getenv('FV_STUB_MODE') ?: 'ok';
$GLOBALS['fv_stub'] = ['posts'=>[], 'meta'=>[], 'terms'=>[], 'created'=>0, 'updated'=>0, 'attempts'=>0];
function seed_post($id, $type, $slug, $owned) {
    $s =& $GLOBALS['fv_stub'];
    $s['posts'][$id] = (object)['ID'=>$id, 'post_type'=>$type, 'post_name'=>$slug,
        'post_status'=>'publish', 'post_content'=>'old local content'];
    if ($owned) $s['meta'][$id]['_fv_ex2_local_parity'] = '1';
}
if ($mode === 'nonfv_header') seed_post(41, 'wp_template_part', 'header', false);
if ($mode === 'duplicate_header') {
    seed_post(41, 'wp_template_part', 'header', true);
    seed_post(42, 'wp_template_part', 'header', true);
}
if ($mode === 'all_owned') {
    $slugs = [['wp_template','page'],['wp_template_part','header'],
        ['wp_template_part','footer'],['wp_template_part','fv-archive-index-overlay'],
        ['wp_global_styles','wp-global-styles-assembler']];
    foreach ($slugs as $i=>$pair) seed_post(41+$i, $pair[0], $pair[1], true);
}
register_shutdown_function(function() {
    $s=$GLOBALS['fv_stub'];
    file_put_contents(getenv('FV_STUB_OUTPUT'), json_encode([
        'created'=>$s['created'], 'updated'=>$s['updated'], 'attempts'=>$s['attempts'],
        'posts'=>array_map(function($p) use($s) {return [
            'id'=>$p->ID, 'type'=>$p->post_type, 'slug'=>$p->post_name,
            'status'=>$p->post_status, 'content'=>$p->post_content,
            'owned'=>$s['meta'][$p->ID]['_fv_ex2_local_parity'] ?? null,
            'terms'=>$s['terms'][$p->ID] ?? []];}, array_values($s['posts']))
    ], JSON_UNESCAPED_SLASHES));
});
function home_url($path) {return (getenv('FV_STUB_HOST') ?: 'http://localhost').$path;}
function wp_get_environment_type() {return getenv('FV_STUB_ENV') ?: 'local';}
function wp_get_theme() {return new class {
    function get_stylesheet() {return 'assembler';}
    function get($key) {return getenv('FV_STUB_THEME') ?: '0.0.126';}
};}
function get_posts($q) {
    $s=$GLOBALS['fv_stub'];
    return array_slice(array_values(array_filter($s['posts'],function($p)use($q){
        return $p->post_type === $q['post_type'] && $p->post_name === $q['name'];
    })),0, $q['posts_per_page'] ?? 10);
}
function get_post_meta($id,$key,$single) {return $GLOBALS['fv_stub']['meta'][$id][$key] ?? '';}
function get_post($id) {
    $p = $GLOBALS['fv_stub']['posts'][$id] ?? null;
    if (!$p) return null;
    $copy = clone $p;
    if ((getenv('FV_STUB_MODE') ?: '') === 'corrupt_readback') $copy->post_content .= ' [filtered]';
    return $copy;
}
function wp_insert_post($a,$return_error) {
    $s =& $GLOBALS['fv_stub'];
    $s['attempts']++;
    $id = $a['ID'] ?? (100 + $s['created']);
    if (isset($a['ID'])) $s['updated']++; else $s['created']++;
    $s['posts'][$id]=(object)['ID'=>$id,'post_type'=>$a['post_type'],
        'post_name'=>$a['post_name'],'post_status'=>$a['post_status'],
        'post_content'=>$a['post_content']];
    return $id;
}
function wp_set_object_terms($id,$term,$taxonomy) {
    $GLOBALS['fv_stub']['terms'][$id][$taxonomy] = [$term]; return [$term];
}
function wp_get_object_terms($id,$taxonomy,$args=[]) {
    if ((getenv('FV_STUB_MODE') ?: '') === 'lost_theme_term' && $taxonomy === 'wp_theme') return [];
    return $GLOBALS['fv_stub']['terms'][$id][$taxonomy] ?? [];
}
function taxonomy_exists($taxonomy) {return true;}
function update_post_meta($id,$key,$value) {$GLOBALS['fv_stub']['meta'][$id][$key]=$value;return true;}
function is_wp_error($v) {return false;}
function wp_json_encode($v) {return json_encode($v, JSON_UNESCAPED_SLASHES);}
'''

def manifest(tracker=False, outbound_css=False):
    css = '.fv{color:#f4efe6}' + ('.fv a{color:#cda75d}\n' * 40)
    if outbound_css: css += '@import "https://third-party.invalid/tracker.css";'
    template = '<!-- wp:group --><header>FINAL VESTIGE</header><!-- /wp:group -->'
    if tracker: template += '<script src="https://example.invalid/analytics.js"></script>'
    return {'schema':'fv-local-assembler-parity-v1', 'release':'HOLD',
        'local_only':True, 'source_theme':{'stylesheet':'assembler','version':'0.0.126'},
        'template_content':{k:template for k in ('page','header','footer','overlay')},
        'global_styles':{'settings':{'layout':{'contentSize':'760px','wideSize':'1440px'}},
                         'styles':{'css':css}}}

def run_importer(*, importer=IMPORTER, mode='ok', host=None, env=None, theme=None,
                 tracker=False, outbound_css=False):
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        wp_stub=td/'wp_stub.php';wp_stub.write_text(WP_STUB)
        man=td/'assembler-public-safe.json';man.write_text(json.dumps(manifest(tracker,outbound_css)))
        real=Path(importer).read_text()
        bootstrap="require_once '/wordpress/wp-load.php';"
        manifest_path="$path = '/wordpress/wp-content/uploads/fv-ex2-parity/assembler-public-safe.json';"
        if real.count(bootstrap)!=1 or real.count(manifest_path)!=1:
            raise AssertionError('Test refused: unexpected importer bootstrap/manifest source')
        adjusted=real.replace(bootstrap, "require_once "+json.dumps(str(wp_stub))+";")
        adjusted=adjusted.replace(manifest_path, "$path = "+json.dumps(str(man))+";")
        runner=td/'importer.php';runner.write_text(adjusted)
        output=td/'state.json'
        environ=dict(os.environ, FV_STUB_MODE=mode, FV_STUB_OUTPUT=str(output))
        for key,value in [('FV_STUB_HOST',host),('FV_STUB_ENV',env),('FV_STUB_THEME',theme)]:
            if value is not None:environ[key]=value
            else:environ.pop(key,None)
        result=subprocess.run(['php',str(runner)],env=environ,capture_output=True,text=True,timeout=12)
        return result, json.loads(output.read_text())

class ImportContract(unittest.TestCase):
    def test_healthy_import_creates_exact_five_public_presentation_records(self):
        result, state=run_importer()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('RELEASE HOLD',result.stdout)
        self.assertEqual(state['created'],5)
        self.assertEqual(state['attempts'],5)
        self.assertEqual([p['slug'] for p in state['posts']],
          ['page','header','footer','fv-archive-index-overlay','wp-global-styles-assembler'])
        for p in state['posts']:
            self.assertEqual(p['owned'],'1')
            self.assertEqual(p['status'],'publish')
            self.assertEqual(p['terms'].get('wp_theme'),['assembler'])
        self.assertEqual(json.loads(state['posts'][4]['content'])['version'],2)

    def test_nonfv_late_collision_rejected_before_any_insert(self):
        result,state=run_importer(mode='nonfv_header')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('existing non-FV local override',result.stderr)
        self.assertEqual(state['attempts'],0,'Two-pass preflight required')

    def test_duplicate_tagged_override_rejected_before_any_insert(self):
        result,state=run_importer(mode='duplicate_header')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('duplicate local override',result.stderr)
        self.assertEqual(state['attempts'],0)

    def test_repeat_owned_import_updates_only_five_existing_records(self):
        result,state=run_importer(mode='all_owned')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(state['created'],0)
        self.assertEqual(state['updated'],5)
        self.assertEqual(len(state['posts']),5)

    def test_wordpress_readback_content_corruption_fails_closed(self):
        result,state=run_importer(mode='corrupt_readback')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('readback differs',result.stderr)
        self.assertEqual(state['attempts'],1)

    def test_missing_theme_taxonomy_association_fails_closed(self):
        result,state=run_importer(mode='lost_theme_term')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('theme association absent',result.stderr)
        self.assertEqual(state['attempts'],1)

    def test_nonlocal_host_refused_before_writes(self):
        result,state=run_importer(host='https://finalvestige.com')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('not explicitly local',result.stderr)
        self.assertEqual(state['attempts'],0)

    def test_production_environment_refused_before_writes(self):
        result,state=run_importer(env='production')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(state['attempts'],0)

    def test_theme_version_mismatch_refused(self):
        result,state=run_importer(theme='0.0.125')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Assembler 0.0.126',result.stderr)
        self.assertEqual(state['attempts'],0)

    def test_executable_tracker_in_public_template_refused(self):
        result,state=run_importer(tracker=True)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(state['attempts'],0)

    def test_external_stylesheet_refused(self):
        result,state=run_importer(outbound_css=True)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(state['attempts'],0)

if __name__=='__main__': unittest.main(verbosity=2)
