import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
from zipfile import ZipFile

SOURCE=Path(__file__).with_name('run_local_wordpress_acceptance.py')
spec=importlib.util.spec_from_file_location('entry',SOURCE)
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
BUNDLE=Path(__file__).parents[1]/'fv_sprint15'/'fv-ex2-local-cli-preflight-guarded.zip'

class Contract(unittest.TestCase):
    def test_real_attested_bundle(self):
        p=e.attest(BUNDLE)
        self.assertEqual(p['php_payloads_verified'],2)
        self.assertEqual(p['zip_sha256'],e.BUNDLE_SHA256)
    def test_no_production_host(self):
        with self.assertRaises(ValueError):e.ready('https://finalvestige.com/',1,Mock())
        with self.assertRaises(ValueError):e.ready('http://evil.example/',1,Mock())
    def test_bad_port_blocked_pre_launch(self):
        with tempfile.TemporaryDirectory() as t:
            audit=Path(t)/'stub.py';audit.write_text('pass')
            with self.assertRaises(ValueError):e.execute(BUNDLE,Path(t)/'output',audit,None,80,1)
    def test_tampered_archive_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            changed=Path(t)/'tampered.zip';changed.write_bytes(BUNDLE.read_bytes()+b' ') 
            with self.assertRaisesRegex(ValueError,'ZIP_SHA_DRIFT'):e.attest(changed)
    def test_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            changed=Path(t)/'missing.zip'
            with ZipFile(changed,'w') as z:z.writestr('blueprint.json','{}')
            with self.assertRaises(ValueError):e.attest(changed)
    def test_preflight_only_is_explicitly_not_wp(self):
        with tempfile.TemporaryDirectory() as t:
            rc=e.main(['--bundle',str(BUNDLE),'--output',t,'--preflight-only'])
            self.assertEqual(rc,0)
            self.assertFalse((Path(t)/'local_acceptance.json').exists())
            self.assertEqual(json.loads((Path(t)/'source_preflight.json').read_text())['scope'],'local-only source preflight; NOT a WordPress pass')
    def test_readiness_rejects_redirect(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertFalse('release_authorized' in e.attest(BUNDLE))

if __name__=='__main__': unittest.main()
