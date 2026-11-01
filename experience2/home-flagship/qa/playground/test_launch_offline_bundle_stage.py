"""Adversarial, synthetic offline ZIP launcher regressions; NOT native WP QA."""
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile
import test_offline_bundle as fixtures
h = fixtures.h
import launch_offline_bundle_stage as mod


class OfflineStageTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.OfflineBundleTests()
        self.fixture.setUp()
        for key in ("tmp","p","media","original","manifest","blueprint","theme","out","blueprint_pin","theme_pin"):
            setattr(self,key,getattr(self.fixture,key))
        self.fixture.build()
        self.pin=h(self.out.read_bytes())
        self.manifest_pin=h(self.manifest.read_bytes())
        self.approved_blueprint_pin=self.blueprint_pin
        self.orig_gate=patch.object(mod,'check_blueprint',return_value={'blueprint_sha256':self.approved_blueprint_pin})
        self.manifest_gate=patch.object(mod,'check_manifest',return_value={'original_manifest_schema':'PASS'})
        self.orig_gate.start();self.manifest_gate.start()

    def tearDown(self):
        self.orig_gate.stop();self.manifest_gate.stop()
        self.fixture.tearDown()

    def verify(self):
        return mod.inspect_offline_bundle(self.out,self.pin,self.blueprint,self.approved_blueprint_pin,
                                          self.manifest,self.manifest_pin,self.theme_pin)

    def repack(self, modify):
        with zipfile.ZipFile(self.out) as z:
            contents={name:z.read(name) for name in z.namelist()}
        modify(contents)
        self.out.unlink()
        with zipfile.ZipFile(self.out,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,data in contents.items():z.writestr(name,data)
        os.chmod(self.out,0o600)
        self.pin=h(self.out.read_bytes())  # malicious attacker re-pins bundle

    def args(self, execute=False):
        return SimpleNamespace(
            bundle=self.out,bundle_sha256=self.pin,original_blueprint=self.blueprint,
            original_blueprint_sha256=self.approved_blueprint_pin,
            media_manifest=self.manifest,media_manifest_sha256=self.manifest_pin,
            assembler_sha256=self.theme_pin,private_dir=self.p,output_dir=self.p/'out',
            execute=execute,axe_js=self.p/'axe.js',axe_sha256='0'*64,
            browser_runner=self.p/'verify_playground_browser.py',browser_runner_sha256='1'*64,
            playground_cli=self.p/'playground',playground_cli_sha256='2'*64,
            lighthouse_cli=self.p/'lighthouse',lighthouse_cli_sha256='3'*64,
            port=19400,ready_timeout=2,browser_timeout=2,
        )

    def test_valid_synthetic_bundle_admitted_not_rendered(self):
        x=self.verify()
        self.assertEqual(x['permitted_source_substitutions'],4)
        self.assertFalse(x['actual_wp_rendered'])
        self.assertEqual(set(x['images']),{'apollo.webp','franklin.jpg','nypl.jpg'})

    def test_zero_actual_wp_claim_in_preflight(self):
        report={'status':'FAILED_CLOSED'}
        mod.stage(self.args(),report)
        self.assertEqual(report['status'],'SEALED_BUNDLE_PREFLIGHT_PASS_NOT_WORDPRESS_EXECUTED')
        self.assertFalse(report['actual_wp_rendered'])

    def test_bundle_hash_mismatch(self):
        self.pin='0'*64
        with self.assertRaises(Exception):self.verify()

    def test_source_blueprint_pin_mismatch(self):
        self.approved_blueprint_pin='0'*64
        with self.assertRaises(Exception):self.verify()

    def test_source_blueprint_content_mutation(self):
        d=json.loads(self.blueprint.read_text());d['steps'][1]['themeData']['url']='https://attacker.invalid/theme.zip'
        self.blueprint.write_text(json.dumps(d))
        with self.assertRaises(Exception):self.verify()

    def test_changed_story_js_even_if_bundle_rehashed(self):
        def change(content):
            d=json.loads(content['blueprint.json']);d['steps'][3]['attacker']='new script'
            content['blueprint.json']=json.dumps(d,sort_keys=True,separators=(',',':')).encode()
        self.repack(change)
        with self.assertRaisesRegex(Exception,'four approved resource substitutions'):
            self.verify()

    def test_extra_file_even_if_bundle_rehashed(self):
        self.repack(lambda content:content.update({'secret.sqlite':b'subscriber data'}))
        with self.assertRaisesRegex(Exception,'bundle entries'):
            self.verify()

    def test_image_content_corruption_even_if_bundle_rehashed(self):
        def change(content):
            data=bytearray(content['media/franklin.jpg']);data[-1]^=1
            content['media/franklin.jpg']=bytes(data)
        self.repack(change)
        with self.assertRaisesRegex(Exception,'original image bytes'):
            self.verify()

    def test_manifest_mutated_even_if_schema_valid(self):
        d=json.loads(self.manifest.read_text());d['images']['franklin.jpg']['sha256']='0'*64
        self.manifest.write_text(json.dumps(d))
        with self.assertRaisesRegex(Exception,'media manifest changed'):
            self.verify()

    def test_wrong_theme_hash_even_if_bundle_rehashed(self):
        self.theme_pin='0'*64
        with self.assertRaisesRegex(Exception,'Assembler theme ZIP SHA-256 mismatch'):
            self.verify()

    def test_duplicate_member_even_if_bundle_rehashed(self):
        with zipfile.ZipFile(self.out,'a') as z:
            z.writestr('media/franklin.jpg',b'evil')
        self.pin=h(self.out.read_bytes())
        with self.assertRaisesRegex(Exception,'bundle entries'):
            self.verify()

    def test_no_scope_escape_for_blueprint(self):
        # Path escapes parent even if all input fingerprints otherwise valid.
        a=self.args();a.original_blueprint=Path('/tmp')/'outside.json'
        with self.assertRaisesRegex(Exception,'Blueprint must remain'):
            mod.stage(a,{})

    def test_no_scope_escape_for_bundle(self):
        a=self.args();a.bundle=Path('/tmp')/'not-private.zip'
        with self.assertRaisesRegex(Exception,'bundle must remain'):
            mod.stage(a,{})

    def test_preflight_never_executes_existing_wordpress_launcher(self):
        with patch.object(mod,'run',side_effect=AssertionError('should never be called')):
            mod.stage(self.args(execute=False),{})

    def test_execute_delegates_bundle_to_existing_unchanged_launcher(self):
        with patch.object(mod,'check_axe',return_value={'axe_executed':False}),\
             patch.object(mod,'check_runner',return_value={'browser_runner':'pinned'}),\
             patch.object(mod,'run') as run:
            receipt={}
            mod.stage(self.args(execute=True),receipt)
            self.assertEqual(run.call_args.args[0].blueprint,self.out)
            self.assertEqual(receipt['status'] if 'status' in receipt else None,None)

    def test_no_zip_replacement_when_symlinked(self):
        self.out.rename(self.p/'real.zip')
        self.out.symlink_to(self.p/'real.zip')
        with self.assertRaisesRegex(Exception,'non-symlink'):
            self.verify()

    def test_wrong_protected_environment_not_accepted(self):
        def change(content):
            d=json.loads(content['blueprint.json']);d['steps'][0]['consts']['WP_ENVIRONMENT_TYPE']='production'
            content['blueprint.json']=json.dumps(d,sort_keys=True,separators=(',',':')).encode()
        self.repack(change)
        with self.assertRaises(Exception):self.verify()


if __name__=='__main__': unittest.main()
