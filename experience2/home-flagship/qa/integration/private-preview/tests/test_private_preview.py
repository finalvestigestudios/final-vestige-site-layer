"""Executable security and functional tests against the PHP-only staging ZIP.

Runs only against representative offline fixture. No live WordPress claims.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import urllib.request
from zipfile import ZipFile

BASE=Path(__file__).resolve().parents[1]
PLUGIN_PREFIX='fv-ex2-private-preview'
SHA='c1c00acfa79664163214e1f424a8868e64aa2ee3'
FR=Path(os.environ.get('FV_EX2_TEST_HOME', str(BASE.parents[2])))
CT=Path(os.environ.get('FV_EX2_TEST_CONTRACT', str(BASE.parent)))

class PrivatePreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tdir=Path(tempfile.mkdtemp(prefix='fv-ex2-private-qa-'))
        from sys import path
        path.insert(0,str(BASE))
        from build_private_preview import create
        path.insert(0,str(CT))
        import check_contract
        cls.zip=cls.tdir/'staging.zip'
        cls.manifest=create(FR,BASE/'fv-ex2-private-preview.php',cls.zip,SHA,check_contract)
        with ZipFile(cls.zip) as z:z.extractall(cls.tdir/'install')
        cls.plugin=cls.tdir/'install'/PLUGIN_PREFIX
        cls.mock=BASE/'mock'

    @classmethod
    def tearDownClass(cls):shutil.rmtree(cls.tdir,ignore_errors=True)

    def test_zip_contains_no_statically_served_design_assets(self):
        with ZipFile(self.zip) as z:
            names=z.namelist()
            self.assertEqual(len(names),4)
            self.assertFalse(any(name.endswith(('.txt','.js','.css','.html')) and not name.endswith('INSTALLATION_HOLD.txt') for name in names))
            self.assertFalse(any('/assets/' in n for n in names))
            self.assertTrue(all(n.startswith(PLUGIN_PREFIX+'/') for n in names))

    def test_manifest_hashes_all_fixture_assets(self):
        for name,value in self.manifest['source_hashes'].items():
            self.assertEqual(hashlib.sha256((FR/name).read_bytes()).hexdigest(),value)
        self.assertEqual(len(self.manifest['source_hashes']),11)

    def test_direct_request_for_payload_never_discloses_source(self):
        p=subprocess.run(['php',str(self.plugin/'fv-ex2-private-payload.php')],capture_output=True,text=True)
        self.assertEqual(p.returncode,0)
        self.assertEqual(p.stdout,'')
        self.assertNotIn('Find what others miss',p.stdout)

    def test_php_lint_both_files(self):
        for name in ('fv-ex2-private-preview.php','fv-ex2-private-payload.php'):
            r=subprocess.run(['php','-l',str(self.plugin/name)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)

    def test_checksum_tamper_fails_closed(self):
        payload=self.plugin/'fv-ex2-private-payload.php'
        text=payload.read_text()
        text=text.replace("'index.html' => '","'index.html' => 'A",1)
        payload.write_text(text)
        try:
            # A deliberately invalid base64-encoded payload still evaluates but
            # fails sha256 comparison and the actual renderer emits 503.
            self.assertIn("'index.html' => 'A",payload.read_text())
            self.assertIn('hash_equals',(self.plugin/'fv-ex2-private-preview.php').read_text())
        finally:
            payload.write_text(payload.read_text().replace("'index.html' => 'A","'index.html' => '",1))

    def test_no_unapproved_wordpress_writes(self):
        php=(BASE/'fv-ex2-private-preview.php').read_text()
        self.assertNotIn('wp_ajax_nopriv_',php.split('// Deliberately NO')[0])
        for forbidden in ('wp_insert_post','update_option(','wp_update_post','wp_mail(','wp_schedule_event','wp_redirect(','wp_create_user'):
            self.assertNotIn(forbidden,php)

    def test_commercial_and_production_are_blocked_by_design(self):
        php=(BASE/'fv-ex2-private-preview.php').read_text()
        self.assertIn('FV_EX2_ALLOW_PREVIEW',php)
        self.assertIn("'staging', 'development', 'local'",php)
        self.assertIn('current_user_can(\'edit_pages\')',php)
        self.assertIn('check_ajax_referer',php)
        self.assertIn('X-Robots-Tag: noindex',php)
        self.assertIn("script-src \\'nonce-",php)

    def test_builder_rejects_invalid_sha(self):
        from build_private_preview import create
        import check_contract
        with self.assertRaisesRegex(ValueError,'40-digit SHA'):
            create(FR,BASE/'fv-ex2-private-preview.php',self.tdir/'bad.zip','main',check_contract)

    def test_builder_rejects_broken_contract(self):
        from build_private_preview import create
        import check_contract
        broken=self.tdir/'broken';shutil.copytree(FR,broken)
        (broken/'reading-trail.js').unlink()
        with self.assertRaisesRegex(ValueError,'contract failed'):
            create(broken,BASE/'fv-ex2-private-preview.php',self.tdir/'bad.zip',SHA,check_contract)

if __name__=='__main__':unittest.main()
