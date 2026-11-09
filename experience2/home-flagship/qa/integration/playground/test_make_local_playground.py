import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_local_playground as m

class StageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.base=Path(self.tmp.name)
        self.repo=self.base/'fixture'
        self.repo.mkdir()
        for f in m.ASSETS:
            p=self.repo/'experience2/home-flagship'/f
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('<!-- TEST SYNTHETIC SOURCE -->' if f.endswith('.html') else '/* TEST */')
        builder=self.repo/m.BUILDER
        builder.parent.mkdir(parents=True,exist_ok=True)
        builder.write_text('''import argparse,json,zipfile,hashlib\nfrom pathlib import Path\np=argparse.ArgumentParser()\np.add_argument('--root');p.add_argument('--out');p.add_argument('--expected-head');a=p.parse_args()\nphp=b'<?php /* SYNTHETIC TEST PLUGIN */'\nmanifest={'expected_commit':a.expected_head,'browser_visible_asset_paths':[],'plugin_sha256':hashlib.sha256(php).hexdigest()}\nwith zipfile.ZipFile(a.out,'w') as z:\n z.writestr('fv-ex2-sealed-staging-preview/fv-ex2-sealed-preview.php',php)\n z.writestr('fv-ex2-sealed-staging-preview/STAGING_MANIFEST.json',json.dumps(manifest))\n z.writestr('fv-ex2-sealed-staging-preview/INSTALLATION_HOLD.txt','LOCAL ONLY')\n''')
        stub=self.repo/'experience2/home-flagship/qa/integration/sealed/fv-ex2-sealed-preview.php'
        stub.write_text('<?php /* DRAFT TEST TEMPLATE */')
        self._cmd('init'); self._cmd('config','user.email','test@invalid.example'); self._cmd('config','user.name','Test');
        self._cmd('add','.'); self._cmd('commit','-m','test fixture')
        self.head=self._cmd('rev-parse','HEAD').strip()
    def tearDown(self): self.tmp.cleanup()
    def _cmd(self,*a):
        return subprocess.check_output(['git','-C',str(self.repo),*a],text=True,stderr=subprocess.DEVNULL)
    def test_build_creates_three_private_files_and_blueprint(self):
        out=self.base/'out'
        r=m.build(self.repo,out,self.head)
        self.assertEqual(r['decision'],'OFFLINE_PACKAGE_BUILT__NOT_WORDPRESS_ACCEPTED')
        self.assertEqual(r['source_head'],self.head)
        self.assertFalse(r['hosted_equivalence'])
        self.assertTrue((out/'plugin'/m.ZIPROOT/m.PLUGIN).exists())
        b=json.loads((out/'blueprint.json').read_text())
        self.assertTrue(b['login'])
        self.assertEqual(b['steps'][0]['consts']['WP_ENVIRONMENT_TYPE'],'local')
        self.assertTrue(b['steps'][0]['consts']['FV_EX2_ALLOW_PREVIEW'])
        self.assertEqual(b['steps'][1]['step'],'activatePlugin')
        self.assertEqual(b['steps'][1]['pluginPath'], f"{m.ZIPROOT}/{m.PLUGIN}")
        self.assertIn("'post_status'=>'private'",b['steps'][2]['code'])
        self.assertNotIn('finalvestige.com',json.dumps(b))
        self.assertIn('NOT_RUN',(out/'receipt.json').read_text())
        with zipfile.ZipFile(out/'sealed-review.zip') as z:
            self.assertEqual(len(z.namelist()),3)
    def test_blueprint_uses_documented_plugin_file_path(self):
        # Playground accepts an absolute plugin DIRECTORY or plugin entry FILE
        # relative to wp-content/plugins. An absolute PHP file is not allowed.
        step = m.blueprint()['steps'][1]
        self.assertEqual(step['step'], 'activatePlugin')
        self.assertEqual(step['pluginPath'], f'{m.ZIPROOT}/{m.PLUGIN}')
        self.assertFalse(step['pluginPath'].startswith('/'))
        self.assertTrue(step['pluginPath'].endswith('.php'))

    def test_wrong_head_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'HEAD mismatch'):m.build(self.repo,self.base/'out','0'*40)
    def test_dirty_source_fails_closed(self):
        (self.repo/'experience2/home-flagship/index.html').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Dirty'):m.build(self.repo,self.base/'out',self.head)
    def test_out_inside_repo_rejected(self):
        with self.assertRaisesRegex(ValueError,'outside'):m.build(self.repo,self.repo/'out',self.head)
    def test_output_webroot_rejected(self):
        with self.assertRaisesRegex(ValueError,'webroot'):m.build(self.repo,self.base/'wp-content'/'out',self.head)
    def test_invalid_sha_rejected(self):
        with self.assertRaisesRegex(ValueError,'40-character'):m.verify_checkout(self.repo,'main')
    def test_symlinked_source_rejected(self):
        p=self.repo/'experience2/home-flagship/index.html'
        p.unlink();p.symlink_to(self.repo/'experience2/home-flagship/flagship.css')
        with self.assertRaisesRegex(ValueError,'symlinked'):m.verify_checkout(self.repo,self.head)
    def test_blueprint_no_public_publish_or_production_host(self):
        b=m.blueprint();s=json.dumps(b)
        self.assertNotIn("'post_status'=>'publish'",s)
        self.assertNotIn('finalvestige.com',s)
        self.assertNotIn('subscriber',s.lower())
        self.assertEqual([x['step'] for x in b['steps']],['defineWpConfigConsts','activatePlugin','runPHP'])
if __name__=='__main__':unittest.main()
