import hashlib
import json
import os
import socket
import subprocess
from types import SimpleNamespace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from launch_integrated_staging import (
    Hold, check_axe, check_blueprint, check_manifest,
    check_runner, local_ready, port_vacant, measured_lighthouse,
    check_executable, write_receipt, MEDIA_SOURCES, SITE_PREFIX, THEME_URL,
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
        self.assertEqual(len(check_runner(p,hashlib.sha256(p.read_bytes()).hexdigest())['browser_runner_sha256']),64)
        p.write_text('print("pretend test passed")')
        self.assert_closed(lambda:check_runner(p,hashlib.sha256(p.read_bytes()).hexdigest()),'browser harness does not include')
    def test_readiness_timeout_does_not_accept_unavailable_localhost(self):
        self.assert_closed(lambda:local_ready(59999,.1),'never reached 200')

    def test_browser_runner_token_comments_not_enough_without_approved_hash(self):
        p=self.root/'verify_playground_browser.py'
        p.write_text('# from integrated_admission_checks import\n'
                     '# audit_archive_gallery BrowserEvidencePage axe.run\n'
                     'print("FAKE PASS")\n')
        self.assert_closed(lambda:check_runner(p,'0'*64),'differs from independently approved')
        self.assert_closed(lambda:check_runner(p,''),'reviewed browser-runner SHA-256 required')

    def test_browser_runner_mutation_rejected_after_independent_review(self):
        p=self.root/'verify_playground_browser.py'
        p.write_text('from integrated_admission_checks import X\n'
                     'audit_archive_gallery BrowserEvidencePage axe.run\n')
        reviewed=hashlib.sha256(p.read_bytes()).hexdigest()
        p.write_text(p.read_text()+'\nprint("altered")\n')
        self.assert_closed(lambda:check_runner(p,reviewed),'differs from independently approved')

    def test_occupied_local_staging_port_rejected(self):
        with socket.socket() as held:
            held.bind(('127.0.0.1',0))
            port=held.getsockname()[1]
            self.assert_closed(lambda:port_vacant(port),'stage port occupied')
        port_vacant(port)

    def test_dead_playground_process_fails_immediately(self):
        class Dead:
            def poll(self):return 1
        self.assert_closed(lambda:local_ready(59999,.1,Dead()),'process exited before ready')

    def test_executable_fingerprint_required_and_enforced(self):
        p=self.root/'wp-playground'
        p.write_text('#!/bin/sh\nexit 0\n')
        p.chmod(0o700)
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(check_executable(p,digest,'Playground CLI'),p.resolve())
        self.assert_closed(lambda:check_executable(p,'0'*64,'Playground CLI'),'differs from approved')
        linked=self.root/'symlink';linked.symlink_to(p)
        self.assert_closed(lambda:check_executable(linked,digest,'Playground CLI'),'symlinked')

    def test_lighthouse_requires_real_audits_not_empty_json(self):
        p=self.root/'lighthouse.json';url='http://127.0.0.1:19400/'
        p.write_text('{}')
        self.assert_closed(lambda:measured_lighthouse(p,url,'mobile'),'report incomplete')
        p.write_text(json.dumps({'lighthouseVersion':'13.0.0',
                                 'requestedUrl':url,'finalDisplayedUrl':url,
                                 'audits':{},'categories':{'performance':{'score':1}}}))
        self.assert_closed(lambda:measured_lighthouse(p,url,'mobile'),'largest-contentful-paint')

    def test_lighthouse_strict_origin_and_metrics(self):
        p=self.root/'lighthouse.json';url='http://127.0.0.1:19400/'
        report={'lighthouseVersion':'13.0.0','requestedUrl':url,
                'finalDisplayedUrl':url,
                'audits':{'largest-contentful-paint':{'numericValue':2100},
                          'cumulative-layout-shift':{'numericValue':0.03},
                          'total-blocking-time':{'numericValue':150}},
                'categories':{'performance':{'score':0.89}}}
        p.write_text(json.dumps(report))
        score=measured_lighthouse(p,url,'mobile')
        self.assertTrue(score['good_lab_lcp'] and score['good_lab_cls'])
        report['finalDisplayedUrl']='https://finalvestige.com/'
        p.write_text(json.dumps(report))
        self.assert_closed(lambda:measured_lighthouse(p,url,'mobile'),'navigated away')
        report['finalDisplayedUrl']=url
        report['audits']['largest-contentful-paint']['numericValue']=float('nan')
        p.write_text(json.dumps(report))
        self.assert_closed(lambda:measured_lighthouse(p,url,'mobile'),'missing/invalid')

    def test_lighthouse_bad_lab_threshold_is_recorded_not_a_pass(self):
        p=self.root/'lighthouse.json';url='http://127.0.0.1:19400/'
        report={'lighthouseVersion':'13.0.0','requestedUrl':url,'finalDisplayedUrl':url,
                'audits':{'largest-contentful-paint':{'numericValue':5000},
                          'cumulative-layout-shift':{'numericValue':0.32},
                          'total-blocking-time':{'numericValue':900}},
                'categories':{'performance':{'score':0.36}}}
        p.write_text(json.dumps(report))
        score=measured_lighthouse(p,url,'desktop')
        self.assertFalse(score['good_lab_lcp'])
        self.assertFalse(score['good_lab_cls'])

    def test_append_only_receipts_dont_reuse_stale_success(self):
        old=self.root/'FV_STAGE_LAUNCH_RECEIPT.json'
        old.write_text('{"status":"PREVIOUS_RUN_PASSED"}\n')
        first={'status':'FAILED_CLOSED','reason':'first failure'}
        second={'status':'FAILED_CLOSED','reason':'second failure'}
        a=write_receipt(self.root,first)
        b=write_receipt(self.root,second)
        self.assertNotEqual(a,b)
        self.assertEqual(len(list(self.root.glob('FV_STAGE_LAUNCH_RECEIPT_*.json'))),2)
        self.assertEqual(old.read_text(),'{"status":"PREVIOUS_RUN_PASSED"}\n')
        self.assertEqual(json.loads(a.read_text())['reason'],'first failure')
        self.assertEqual(json.loads(b.read_text())['reason'],'second failure')
        if os.name=='posix':self.assertEqual(a.stat().st_mode&0o077,0)

if __name__=='__main__':unittest.main(verbosity=2)
