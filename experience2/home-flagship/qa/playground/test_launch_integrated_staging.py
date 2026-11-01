import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from launch_integrated_staging import (
    Hold, check_axe, check_blueprint, check_manifest,
    check_runner, local_ready, MEDIA_SOURCES, SITE_PREFIX, THEME_URL,
)

ASSETS=('wordpress-page-fragment.review-only.html','flagship.css','chronicle.css',
        'chronicle-lens.css','inquiry.css','observer-lab.css','reading-trail.css',
        'flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js')

def fixture():
    steps=[{'step':'defineWpConfigConsts', 'consts':{
        'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_LOCAL_REVIEW':True}},
           {'step':'installTheme','themeData':{'resource':'url','url':THEME_URL},
            'options':{'activate':True}},
           {'step':'writeFile','path':SITE_PREFIX+'fv-ex2-playground.php',
            'data':"<?php function fv_ex2_ready(){} function fv_ex2_integrity(){} add_filter('render_block');"}]
    for name in ASSETS:
        steps.append({'step':'writeFile','path':SITE_PREFIX+'assets/'+name,
                      'data':'x'*45})
    for name,(url,_) in MEDIA_SOURCES.items():
        steps.append({'step':'writeFile','path':SITE_PREFIX+'media/'+name,
                      'data':{'resource':'url','url':url}})
    steps.extend([
        {'step':'activatePlugin','pluginPath':'fv-ex2-playground/fv-ex2-playground.php'},
        {'step':'runPHP','code':"<?php $raw=base64_decode('abc',true); "
         "if(get_stylesheet() !== 'assembler' || wp_get_environment_type() !== 'local') throw Exception(); "
         "if(substr_count($raw,'--i:') !== 72 || substr_count($raw,'<!-- wp:jetpack/subscriptions') !== 1) throw Exception(); "
         "wp_insert_post(array('post_content'=>$raw)); update_option('page_on_front',12); "
         "if(strpos($raw,'data-fv-home-flagship') === false) throw Exception();"}
    ])
    return {'steps':steps}

class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.blue=self.root/'blueprint.json'
        self.spec=fixture()
        self.save_blue()
    def save_blue(self):
        b=json.dumps(self.spec,indent=2).encode()
        self.blue.write_bytes(b)
        if os.name=='posix':self.blue.chmod(0o600)
        self.digest=hashlib.sha256(b).hexdigest()
    def assert_closed(self, f, phrase):
        with self.assertRaises(Hold) as e:f()
        self.assertIn(phrase,str(e.exception))
    def test_valid_integrated_blueprint_preflight(self):
        out=check_blueprint(self.blue,self.digest)
        self.assertEqual((out['steps'],out['media_count']),(19,3))
    def test_rejects_unintegrated_seven_chapter_only_blueprint(self):
        self.spec['steps'][18]['code']="<?php wp_insert_post(array('post_content'=>'[fv_ex2_stage_home]'));"
        self.save_blue()
        self.assert_closed(lambda:check_blueprint(self.blue,self.digest),'integrated Gutenberg identity guard missing')
    def test_rejects_old_or_wrong_reviewed_digest(self):
        self.assert_closed(lambda:check_blueprint(self.blue,'0'*64),'changed since approved')
    def test_rejects_external_or_prod_wp_config(self):
        self.spec['steps'][0]['consts']['WP_ENVIRONMENT_TYPE']='production';self.save_blue()
        self.assert_closed(lambda:check_blueprint(self.blue,self.digest),'local-only')
    def test_rejects_nonassembler_theme(self):
        self.spec['steps'][1]['themeData']['url']='https://example.org/not-assembler.zip';self.save_blue()
        self.assert_closed(lambda:check_blueprint(self.blue,self.digest),'official Assembler')
    def test_rejects_unreviewed_source_write(self):
        self.spec['steps'][2]['path']='/wordpress/wp-config.php';self.save_blue()
        self.assert_closed(lambda:check_blueprint(self.blue,self.digest),'path traversal')
    def test_rejects_cdn_original_substitution(self):
        self.spec['steps'][14]['data']['url']='https://i0.wp.com/example.com/forged.jpg';self.save_blue()
        self.assert_closed(lambda:check_blueprint(self.blue,self.digest),'expected original download URL')
    def test_rejects_unsafe_wp_import_steps(self):
        self.spec['steps'][14]['step']='runSql';self.save_blue()
        self.assert_closed(lambda:check_blueprint(self.blue,self.digest),'unreviewed WordPress writes')
    def test_rejects_missing_renderer_block_identity(self):
        self.spec['steps'][2]['data']='<?php '+('fv_ex2_ready() '*5);self.save_blue()
        self.assert_closed(lambda:check_blueprint(self.blue,self.digest),'plugin does not guard')
    def test_rejects_world_readable_private_page(self):
        if os.name=='posix':
            self.blue.chmod(0o644)
            self.assert_closed(lambda:check_blueprint(self.blue,self.digest),'group/other access')
    def test_rejects_blueprint_symlink(self):
        other=self.root/'linked-blueprint.json';other.symlink_to(self.blue)
        self.assert_closed(lambda:check_blueprint(other,self.digest),'non-symlink')
    def test_media_manifest_requires_three_independent_origins(self):
        p=self.root/'manifest.json'
        media={'purpose':'isolated-staging-media-review','images':{
            n:{'source_url':url,'bytes':size,'sha256':'a'*64} for n,(url,size) in MEDIA_SOURCES.items()}}
        p.write_text(json.dumps(media));p.chmod(0o600)
        self.assertEqual(len(check_manifest(p)['images']),3)
        media['images']['nypl.jpg']['bytes']-=1
        p.write_text(json.dumps(media))
        self.assert_closed(lambda:check_manifest(p),'nypl.jpg')
    def test_axe_digest_and_bundle_presence(self):
        p=self.root/'axe.min.js';p.write_bytes(b'var axe={run:function(){}};'+b' '*11000);p.chmod(0o600)
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertTrue(check_axe(p,h)['axe_local_bytes']>10000)
        self.assert_closed(lambda:check_axe(p,'0'*64),'axe-core source incomplete')
    def test_requires_integrated_browser_runner(self):
        p=self.root/'verify_playground_browser.py';p.write_text('from integrated_admission_checks import X\naudit_archive_gallery BrowserEvidencePage axe.run\n')
        self.assertEqual(len(check_runner(p)['browser_runner_sha256']),64)
        p.write_text('print("pretend test passed")')
        self.assert_closed(lambda:check_runner(p),'browser harness does not include')
    def test_readiness_timeout_does_not_accept_unavailable_localhost(self):
        self.assert_closed(lambda:local_ready(59999,.1),'never reached 200')

if __name__=='__main__':unittest.main(verbosity=2)
