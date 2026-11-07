"""Self-contained controls; optional real bundle supplied through FV_EX2_BUNDLE_PATH.
Synthetic fixture results never count as WordPress runtime or approved source.
"""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch
from zipfile import ZipFile

SOURCE=Path(__file__).with_name('run_local_wordpress_acceptance.py')
spec=importlib.util.spec_from_file_location('entry',SOURCE)
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
REAL_BUNDLE=Path(os.environ['FV_EX2_BUNDLE_PATH']) if os.getenv('FV_EX2_BUNDLE_PATH') else None


def fixture(path):
    php={'mu-plugins/fv-ex2-playground-review.php':b'<?php echo "review";',
         'mu-plugins/fv-ex2-private-browser-receipt.php':b'<?php echo "receipt";'}
    steps=[{'step':'runPHP','code':'FV_EX2_REFUSE_NON_LOOPBACK_BEFORE_ANY_SITE_WRITE WP_ENVIRONMENT_TYPE'},
           {'step':'installTheme','themeData':{'resource':'git:directory','ref':e.ASSEMBLER_COMMIT,'path':'assembler'}},
           {'step':'mkdir','path':'/wordpress/wp-content/mu-plugins'},
           {'step':'writeFile','path':'/wordpress/wp-content/mu-plugins/fv-ex2-playground-review.php'},
           {'step':'writeFile','path':'/wordpress/wp-content/mu-plugins/fv-ex2-private-browser-receipt.php'},
           {'step':'runPHP','code':'<?php'}, {'step':'runPHP','code':'<?php'}]
    receipt={'exact_source_sha256':e.SOURCE_BLUEPRINT,'assembler_commit':e.ASSEMBLER_COMMIT,
             'files_sha256':{k:e.sha(v) for k,v in php.items()}}
    contents={'blueprint.json':json.dumps({'landingPage':'/','steps':steps}).encode(),
              'SOURCE_CUSTODY.json':json.dumps(receipt).encode(), 'REVIEW.txt':b'OFFLINE SYNTHETIC TEST ONLY',**php}
    with ZipFile(path,'w') as z:
        for k,v in contents.items():z.writestr(k,v)
    return e.sha(path.read_bytes())


class Contract(unittest.TestCase):
    def test_synthetic_attested_shape(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'synthetic.zip';hash_=fixture(p)
            with patch.object(e,'BUNDLE_SHA256',hash_):
                r=e.attest(p)
            self.assertEqual(r['php_payloads_verified'],2)
            self.assertEqual(r['scope'],'local-only source preflight; NOT a WordPress pass')
    @unittest.skipUnless(REAL_BUNDLE is not None,'Real ZIP optional: set FV_EX2_BUNDLE_PATH')
    def test_real_pinned_bundle(self):
        self.assertEqual(e.attest(REAL_BUNDLE)['zip_sha256'],e.BUNDLE_SHA256)
    def test_reject_nonlocal_url(self):
        for url in ['https://finalvestige.com/','http://evil.example/','http://localhost:9400/']:
            with self.assertRaises(ValueError):e.ready(url,1,Mock())
    def test_reject_port_before_launch(self):
        with tempfile.TemporaryDirectory() as d:
            audit=Path(d)/'audit.py';audit.write_text('# synthetic')
            with self.assertRaises(ValueError):e.execute(Path(d)/'unused.zip',Path(d)/'out',audit,None,80,1)
    def test_modified_zip_fails_source_pin(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'synthetic.zip';fixture(p)
            with self.assertRaisesRegex(ValueError,'ZIP_SHA_DRIFT'):e.attest(p)
    def test_missing_archive_members_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.zip'
            with ZipFile(p,'w') as z:z.writestr('blueprint.json','{}')
            with patch.object(e,'BUNDLE_SHA256',e.sha(p.read_bytes())):
                with self.assertRaisesRegex(ValueError,'BUNDLE_FILES_CHANGED'):e.attest(p)
    def test_modified_php_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'synthetic.zip';fixture(p)
            with ZipFile(p,'a') as z:z.writestr('mu-plugins/tampered.php','<?php')
            with patch.object(e,'BUNDLE_SHA256',e.sha(p.read_bytes())):
                with self.assertRaises(ValueError):e.attest(p)
    def test_preflight_only_not_wp(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'synthetic.zip';hash_=fixture(p)
            with patch.object(e,'BUNDLE_SHA256',hash_):
                rc=e.main(['--bundle',str(p),'--output',str(Path(d)/'qa'),'--preflight-only'])
            self.assertEqual(rc,0)
            self.assertFalse((Path(d)/'qa'/'local_acceptance.json').exists())
            report=json.loads((Path(d)/'qa'/'source_preflight.json').read_text())
            self.assertIn('NOT a WordPress pass',report['scope'])

if __name__=='__main__':unittest.main()
