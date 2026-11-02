"""Synthetic-only ZIP/identity adversarial tests; not WordPress execution."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile
from package_offline_playground_bundle import (MEDIA, PREFIX, ASSET_DIR, STYLES_AND_SCRIPTS,
    PLUGIN_FILE, THEME_URL, Hold, package, seal, sha)


def fixture():
    steps = [
        {'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_LOCAL_REVIEW':True}},
        {'step':'installTheme','themeData':{'resource':'url','url':THEME_URL},'options':{'activate':True}},
        {'step':'writeFile','path':PLUGIN_FILE,'data':"<?php function fv_ex2_ready(){} function fv_ex2_integrity(){} add_filter('render_block');"},
    ]
    for n in STYLES_AND_SCRIPTS:
        steps.append({'step':'writeFile','path':ASSET_DIR+n,'data':'REAL FLAGSHIP SOURCE ONLY: ' + n + ' attested'})
    for n, (url, _) in MEDIA.items():
        steps.append({'step':'writeFile','path':PREFIX+n,'data':{'resource':'url','url':url}})
    steps.append({'step':'activatePlugin','pluginPath':'fv-ex2-playground/fv-ex2-playground.php'})
    steps.append({'step':'runPHP','code':"<?php if (get_stylesheet() !== 'assembler' || wp_get_environment_type() !== 'local' || !fv_ex2_ready()) die(); $raw=base64_decode('x'); if (substr_count($raw,'--i:') !== 72) die(); $id=wp_insert_post(array('post_content'=>wp_slash($raw))); $fv_stored=get_post_field('post_content',$id,'raw');"})
    assert len(steps)==19
    sources={}
    for n,(url,length) in MEDIA.items():
        sig=b'RIFF\x00\x00\x00\x00WEBP' if n=='apollo.webp' else b'\xff\xd8\xff\xe0'
        sources[n]=sig + b'Z'*(length-len(sig))
    manifest={'purpose':'isolated-staging-media-review','images':{n:{'source_url':MEDIA[n][0],'bytes':len(data),'sha256':sha(data)} for n,data in sources.items()}}
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        z.writestr('assembler/style.css','/*\nTheme Name: Assembler\n*/')
        z.writestr('assembler/templates/index.html','<!-- wp:post-content /-->')
    return {'steps':steps},b.getvalue(),sources,manifest

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.blueprint,self.theme,self.sources,self.manifest=fixture()
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.root.chmod(0o700)
        (self.root/'assets').mkdir(mode=0o700)
        self.out=self.root/'private-bundle.zip'
        self.save_all()

    def private(self,path,data):
        if isinstance(data,str):data=data.encode()
        path.write_bytes(data);path.chmod(0o600)

    def save_all(self):
        self.private(self.root/'blueprint.json',json.dumps(self.blueprint))
        self.private(self.root/'theme.zip',self.theme)
        self.private(self.root/'manifest.json',json.dumps(self.manifest))
        for n,data in self.sources.items():self.private(self.root/'assets'/n,data)

    def execute(self,path=None):
        return package(self.root/'blueprint.json',self.root/'theme.zip',self.root/'assets',
            self.root/'manifest.json',sha(self.theme),sha((self.root/'blueprint.json').read_bytes()),path or self.out)

    def test_complete_offline_zip_matches_official_bundled_resource_contract(self):
        r=self.execute()
        self.assertFalse(r['wordpress_runtime_executed']);self.assertFalse(r['rights_verified'])
        self.assertEqual(r['status'],'OFFLINE_BUNDLE_SEALED_NOT_WORDPRESS_EXECUTED_RELEASE_HOLD')
        with zipfile.ZipFile(self.out) as z:
            self.assertEqual(set(z.namelist()),{'blueprint.json','assets/assembler.zip'} | {'assets/'+n for n in MEDIA})
            self.assertEqual(z.read('assets/assembler.zip'),self.theme)
            bp=json.loads(z.read('blueprint.json'))
            self.assertEqual(bp['steps'][1]['themeData'],{'resource':'bundled','path':'/assets/assembler.zip'})
            for s in bp['steps'][2:17]:
                if s['path'].startswith(PREFIX):
                    n=s['path'].split('/')[-1]
                    self.assertEqual(s['data'],{'resource':'bundled','path':'/assets/'+n})
                    self.assertEqual(z.read('assets/'+n),self.sources[n])
        self.assertEqual(self.out.stat().st_mode & 0o077,0)
        self.assertEqual(json.loads((self.root/'blueprint.json').read_text()),self.blueprint,'source Blueprint must stay unchanged')

    def test_bundle_is_deterministic_and_never_overwritten(self):
        a=self.execute()
        b=self.execute(self.root/'second.zip')
        self.assertEqual(a['bundle_sha256'],b['bundle_sha256'])
        with self.assertRaisesRegex(Hold,'overwrite'):
            self.execute()

    def test_tampered_historical_image_fails_closed(self):
        self.private(self.root/'assets'/'nypl.jpg',self.sources['nypl.jpg'][:-1]+b'X')
        with self.assertRaisesRegex(Hold,'byte identity mismatch'):
            self.execute()
        self.assertFalse(self.out.exists())

    def test_manifest_substituted_origin_fails_closed(self):
        self.manifest['images']['franklin.jpg']['source_url']='https://attacker.test/f.jpg'
        self.save_all()
        with self.assertRaisesRegex(Hold,'byte identity mismatch'):
            self.execute()

    def test_wrong_theme_sha_fails_closed(self):
        with self.assertRaisesRegex(Hold,'Assembler ZIP'):
            package(self.root/'blueprint.json',self.root/'theme.zip',self.root/'assets',self.root/'manifest.json','0'*64,sha((self.root/'blueprint.json').read_bytes()),self.out)

    def test_wrong_blueprint_sha_fails_closed(self):
        with self.assertRaisesRegex(Hold,'Blueprint SHA-256'):
            package(self.root/'blueprint.json',self.root/'theme.zip',self.root/'assets',self.root/'manifest.json',sha(self.theme),'0'*64,self.out)

    def test_unsafe_extra_source_or_import_rejected(self):
        self.blueprint['steps'][5]['path']='/wordpress/wp-content/evil.php'
        self.save_all()
        with self.assertRaisesRegex(Hold,'source payload'):
            self.execute()

    def test_missing_wp_post_save_gate_rejected(self):
        self.blueprint['steps'][-1]['code']=self.blueprint['steps'][-1]['code'].replace('wp_slash($raw)','$raw')
        self.save_all()
        with self.assertRaisesRegex(Hold,'post-save integrity'):
            self.execute()

    def test_remote_theme_or_external_media_substitution_rejected(self):
        self.blueprint['steps'][1]['themeData']['url']='https://other.example/assembler.zip'
        self.save_all()
        with self.assertRaisesRegex(Hold,'theme URL'):
            self.execute()
        self.blueprint['steps'][1]['themeData']['url']=THEME_URL
        self.blueprint['steps'][14]['data']['url']='https://malicious.test/photo.jpg'
        self.save_all()
        with self.assertRaisesRegex(Hold,'source substitution'):
            self.execute()

    def test_path_traversal_theme_zip_rejected(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            z.writestr('assembler/style.css','Theme Name: Assembler')
            z.writestr('assembler/templates/index.html','index')
            z.writestr('../escaping.php','evil')
        self.theme=b.getvalue();self.save_all()
        with self.assertRaisesRegex(Hold,'unsafe ZIP member'):
            self.execute()

    def test_symlink_inputs_rejected(self):
        (self.root/'assets'/'apollo.webp').unlink()
        (self.root/'assets'/'apollo.webp').symlink_to(self.root/'assets'/'franklin.jpg')
        with self.assertRaisesRegex(Hold,'non-symlink'):
            self.execute()

    def test_bad_output_permissions_rejected(self):
        (self.root/'public').mkdir(mode=0o755)
        with self.assertRaisesRegex(Hold,'chmod 700'):
            self.execute(self.root/'public'/'bundle.zip')

if __name__=='__main__':unittest.main(verbosity=2)
