"""Release-gate tests: no actual WordPress or production access."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from run_local_playground import AdmissionError, PLUGIN_DIR, PLUGIN_FILE, prepare

HEAD='a'*40
class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out=Path(self.tmp.name)
        plugin=self.out/'plugin'/PLUGIN_DIR/PLUGIN_FILE
        plugin.parent.mkdir(parents=True)
        plugin.write_text('<?php /* local, synthetic */')
        (self.out/'sealed-review.zip').write_bytes(b'not a real ZIP; synthetic fixture only')
        bp={'login':True,'landingPage':'/wp-admin/','steps':[
            {'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_PREVIEW':True,'DISALLOW_FILE_EDIT':True}},
            {'step':'activatePlugin','pluginPath':f'{PLUGIN_DIR}/{PLUGIN_FILE}'},
            {'step':'runPHP','code':"'post_status'=>'private'"}]}
        (self.out/'blueprint.json').write_text(json.dumps(bp))
        receipt={'source_head':HEAD,'decision':'OFFLINE_PACKAGE_BUILT__NOT_WORDPRESS_ACCEPTED',
                 'production_writes':False,'hosted_equivalence':False}
        for filename,key in [('sealed-review.zip','sealed_zip_sha256'),
                             ('blueprint.json','blueprint_sha256'),
                             (f'plugin/{PLUGIN_DIR}/{PLUGIN_FILE}','php_sha256')]:
            receipt[key]=hashlib.sha256((self.out/filename).read_bytes()).hexdigest()
        (self.out/'receipt.json').write_text(json.dumps(receipt))
    def prep(self):
        return prepare(self.out,HEAD,['test-cli'])
    def test_explicit_mount_precedes_activation(self):
        cmd=self.prep()
        self.assertEqual(cmd[0:2],['test-cli','server'])
        self.assertTrue(any(x.startswith('--mount=') and x.endswith(':/wordpress/wp-content/plugins/'+PLUGIN_DIR) for x in cmd))
        self.assertIn('--site-url=http://127.0.0.1:9400',cmd)
        self.assertTrue(any(x.startswith('--blueprint=') for x in cmd))
    def test_wrong_sha_rejected(self):
        with self.assertRaisesRegex(AdmissionError,'mismatched'):prepare(self.out,'b'*40)
    def test_invalid_head_rejected(self):
        with self.assertRaisesRegex(AdmissionError,'40-character'):prepare(self.out,'main')
    def test_modified_plugin_rejected(self):
        p=self.out/'plugin'/PLUGIN_DIR/PLUGIN_FILE
        p.write_text('tampered')
        with self.assertRaisesRegex(AdmissionError,'integrity'):self.prep()
    def test_modified_blueprint_rejected(self):
        p=self.out/'blueprint.json';p.write_text('{}')
        with self.assertRaisesRegex(AdmissionError,'integrity'):self.prep()
    def test_missing_plugin_rejected(self):
        (self.out/'plugin'/PLUGIN_DIR/PLUGIN_FILE).unlink()
        with self.assertRaisesRegex(AdmissionError,'Missing'):self.prep()
    def test_symlink_plugin_rejected(self):
        p=self.out/'plugin'/PLUGIN_DIR/PLUGIN_FILE
        p.unlink();p.symlink_to(self.out/'blueprint.json')
        with self.assertRaisesRegex(AdmissionError,'symlinked'):self.prep()
    def test_wrong_environment_rejected_even_if_rehashed(self):
        p=self.out/'blueprint.json';bp=json.loads(p.read_text());bp['steps'][0]['consts']['WP_ENVIRONMENT_TYPE']='production';p.write_text(json.dumps(bp));self._rehash_blueprint()
        with self.assertRaisesRegex(AdmissionError,'local'):self.prep()
    def test_public_page_rejected_even_if_rehashed(self):
        p=self.out/'blueprint.json';bp=json.loads(p.read_text());bp['steps'][2]['code']='publish';p.write_text(json.dumps(bp));self._rehash_blueprint()
        with self.assertRaisesRegex(AdmissionError,'private'):self.prep()
    def test_missing_mount_target_rejected_even_if_rehashed(self):
        p=self.out/'blueprint.json';bp=json.loads(p.read_text());bp['steps'][1]['pluginPath']='other/evil.php';p.write_text(json.dumps(bp));self._rehash_blueprint()
        with self.assertRaisesRegex(AdmissionError,'exact mounted'):self.prep()
    def _rehash_blueprint(self):
        p=self.out/'receipt.json';r=json.loads(p.read_text());r['blueprint_sha256']=hashlib.sha256((self.out/'blueprint.json').read_bytes()).hexdigest();p.write_text(json.dumps(r))
if __name__=='__main__':unittest.main()
