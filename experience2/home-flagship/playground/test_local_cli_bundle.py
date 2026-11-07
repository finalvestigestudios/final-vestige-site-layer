import io
import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from local_cli_bundle import pack, sha, BP_HASH, LOCAL_PREFLIGHT

SOURCE = Path(os.environ.get('FV_EX2_REVIEW_ZIP', 'review-only-source.zip'))

class BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SOURCE.is_file():
            raise RuntimeError('Provide exact PR #1379 source ZIP via FV_EX2_REVIEW_ZIP (fail closed)')
        cls.src=SOURCE.read_bytes()
    def test_repeatable_compact(self):
        a, _ = pack(self.src); b, _ = pack(self.src)
        self.assertEqual(a,b)
        self.assertLess(len(a),len(self.src)//2)
    def test_bundle_extracted_import_steps_and_privacy(self):
        blob, receipt = pack(self.src)
        with ZipFile(io.BytesIO(blob)) as z:
            self.assertEqual(len(z.namelist()),5)
            bp=json.loads(z.read('blueprint.json'))
            self.assertEqual(bp['landingPage'],'/')
            self.assertEqual(receipt['exact_source_sha256'],BP_HASH)
            self.assertEqual(sum(s['step']=='runPHP' for s in bp['steps']),3)
            self.assertEqual(bp['steps'][0]['step'],'runPHP')
            self.assertEqual(bp['steps'][0]['code'],LOCAL_PREFLIGHT)
            self.assertEqual(bp['steps'][1]['step'],'installTheme')
            self.assertTrue(receipt['local_only_preflight_first'])
            for s in bp['steps']:
                if s['step']=='writeFile':
                    self.assertEqual(s['data']['resource'],'bundled')
                    self.assertTrue(z.read(s['data']['path'].lstrip('/')).startswith(b'<?php'))
            self.assertIn(b'Never install on production',z.read('REVIEW.txt'))
            self.assertFalse(any(p.endswith(('.sql','.env')) for p in z.namelist()))
    def _changed(self, which, before, after):
        with ZipFile(io.BytesIO(self.src)) as z:
            files={p:z.read(p) for p in z.namelist()}
        self.assertIn(before,files[which])
        files[which]=files[which].replace(before,after,1)
        buf=io.BytesIO()
        with ZipFile(buf,'w',compression=ZIP_DEFLATED) as z:
            for p,v in files.items(): z.writestr(p,v)
        return buf.getvalue()

    @unittest.skipUnless(shutil.which('php'), 'PHP CLI required for local preflight test')
    def test_local_preflight_live_php_safety_matrix(self):
        bundle, _ = pack(self.src)
        with ZipFile(io.BytesIO(bundle)) as z:
            bp=json.loads(z.read('blueprint.json'))
        code=bp['steps'][0]['code']
        self.assertIn("require_once '/wordpress/wp-load.php';", code)
        # WordPress stub supplies URL parsing ONLY. This does not run WordPress.
        code=code.replace("require_once '/wordpress/wp-load.php';",'')
        source='''<?php
function home_url($path) { return getenv('FV_TEST_HOME'); }
function wp_parse_url($url) { return parse_url($url); }
''' + code.removeprefix('<?php') + '\n' + 'echo "PREFLIGHT_PASS";'
        matrix=[('http://localhost:9400/',None,True),
                ('http://127.0.0.1:9400/',None,True),
                ('http://fv.localhost:9400/',None,True),
                ('http://[::1]:9400/',None,True),
                ('https://finalvestige.com/',None,False),
                ('https://www.finalvestige.com/',None,False),
                ('https://fv.localhost.evil.test/',None,False),
                ('https://playground.wordpress.net/',None,False),
                ('https://foo.wpcomstaging.com/',None,False),
                ('http://localhost:9400/','production',False)]
        for host, env, should_pass in matrix:
            with self.subTest(host=host, env=env):
                code_to_run = source.replace('<?php',
                    "<?php define('WP_ENVIRONMENT_TYPE','production');",1) if env == 'production' else source
                e={**os.environ, 'FV_TEST_HOME':host}
                p=subprocess.run(['php'],input=code_to_run,text=True,capture_output=True,env=e)
                if should_pass:
                    self.assertEqual(p.returncode,0,p.stdout+p.stderr)
                    self.assertIn('PREFLIGHT_PASS',p.stdout)
                else:
                    self.assertNotEqual(p.returncode,0,host)
                    self.assertIn('FV_EX2_REFUSE_',p.stderr)

    def test_does_not_mutate_exact_pinned_source_steps(self):
        with ZipFile(io.BytesIO(self.src)) as z: original=json.loads(z.read('blueprint_with_local_receipt.json'))
        bundle,_ = pack(self.src)
        with ZipFile(io.BytesIO(bundle)) as z:
            compiled=json.loads(z.read('blueprint.json'))
            for step in compiled['steps'][1:]:
                if step.get('step')=='writeFile':
                    step['data']=z.read(step['data']['path'].lstrip('/')).decode('utf-8')
        self.assertEqual(compiled['steps'][1:],original['steps'])

    def test_blueprint_mutation_rejected(self):
        bad=self._changed('blueprint_with_local_receipt.json', b'fv-ex2-review',b'fv-ex2-revieX')
        with self.assertRaisesRegex(ValueError,'SOURCE_DRIFT'):pack(bad)
    def test_manifest_mutation_rejected(self):
        bad=self._changed('source_manifest.json',b'75faa8a1',b'15faa8a1')
        with self.assertRaisesRegex(ValueError,'PIN_DRIFT'):pack(bad)

if __name__=='__main__': unittest.main(verbosity=2)
