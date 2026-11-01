"""Synthetic local ZIP boundary regressions; NEVER original image/source authentication."""
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch
import make_offline_private_bundle as mod


def h(raw): return hashlib.sha256(raw).hexdigest()

class OfflineBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name)
        os.chmod(self.p, 0o700)
        self.media = self.p/'media';self.media.mkdir()
        self.original = {'steps':[{'step':'noop'} for _ in range(19)]}
        self.original['steps'][1] = {'step':'installTheme','themeData':{'resource':'url','url':mod.THEME_URL}}
        self.original['steps'][0] = {'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_LOCAL_REVIEW':True}}
        images = {}
        for idx,(name,(url,length)) in enumerate(mod.MEDIA_SOURCES.items()):
            data = (b'RIFFxxxxWEBP' if name.endswith('webp') else b'\xff\xd8\xff') + bytes([idx + 1])*(length - (12 if name.endswith('webp') else 3))
            x = self.media/name;x.write_bytes(data);os.chmod(x,0o600)
            self.original['steps'][14+idx] = {'step':'writeFile', 'path':mod.SITE_PREFIX+'media/'+name,'data':{'resource':'url','url':url}}
            images[name] = {'source_url':url,'bytes':length,'sha256':h(data)}
        self.manifest=self.p/'manifest.json';self.manifest.write_text(json.dumps({'purpose':'isolated-staging-media-review','images':images}));os.chmod(self.manifest,0o600)
        self.blueprint=self.p/'blueprint.json';self.blueprint.write_text(json.dumps(self.original));os.chmod(self.blueprint,0o600)
        self.theme=self.p/'assembler.zip'
        with zipfile.ZipFile(self.theme,'w') as z:
            z.writestr('assembler/style.css','/*\nTheme Name: Assembler\n*/\n')
            z.writestr('assembler/theme.json','{}')
            z.writestr('assembler/templates/index.html','<!-- wp:post-content /-->')
        os.chmod(self.theme,0o600)
        self.out=self.p/'offline.zip'
        self.blueprint_pin=h(self.blueprint.read_bytes());self.theme_pin=h(self.theme.read_bytes())
        self.g1=patch.object(mod,'check_blueprint',return_value={'steps':19})
        self.g2=patch.object(mod,'check_manifest',return_value={'original_manifest_schema':'PASS'})
        self.g1.start();self.g2.start()
    def tearDown(self):
        self.g1.stop();self.g2.stop();self.tmp.cleanup()
    def build(self):
        return mod.package(self.blueprint,self.blueprint_pin,self.manifest,self.media,self.theme,self.theme_pin,self.out)
    def test_valid_synthetic_bundle_four_file_replacements(self):
        receipt=self.build()
        self.assertEqual(receipt['rewritten_steps'],[1,14,15,16])
        with zipfile.ZipFile(self.out) as z:
            self.assertEqual(z.namelist(),list(mod.ENTRIES))
            generated=json.loads(z.read('blueprint.json'))
            self.assertEqual(generated['steps'][1]['themeData']['resource'],'bundled')
            for idx,name in enumerate(mod.FILES):
                self.assertEqual(generated['steps'][14+idx]['data']['path'],'/media/'+name)
                self.assertEqual(h(z.read('media/'+name)),json.loads(self.manifest.read_text())['images'][name]['sha256'])
        self.assertFalse(receipt['wordpress_rendered'])
    def test_determinism(self):
        self.build();a=h(self.out.read_bytes());self.out.unlink();self.build()
        self.assertEqual(a,h(self.out.read_bytes()))
    def test_bad_media_hash_fails_closed(self):
        path=self.media/'franklin.jpg';b=bytearray(path.read_bytes());b[-1]^=1;path.write_bytes(b)
        with self.assertRaises(Exception):self.build()
        self.assertFalse(self.out.exists())
    def test_bad_image_signature_fails_closed(self):
        p=self.media/'nypl.jpg';b=bytearray(p.read_bytes());b[:3]=b'GIF';p.write_bytes(b)
        manifest=json.loads(self.manifest.read_text());manifest['images']['nypl.jpg']['sha256']=h(b)
        self.manifest.write_text(json.dumps(manifest))
        with self.assertRaises(Exception):self.build()
    def test_wrong_theme_sha_fails_closed(self):
        self.theme_pin='0'*64
        with self.assertRaises(Exception):self.build()
    def test_theme_zip_traversal_fails_closed(self):
        self.theme.unlink()
        with zipfile.ZipFile(self.theme,'w') as z:
            z.writestr('assembler/style.css','Theme Name: Assembler')
            z.writestr('assembler/theme.json','{}')
            z.writestr('assembler/templates/index.html','hi')
            z.writestr('../escape','bad')
        self.theme_pin=h(self.theme.read_bytes())
        with self.assertRaises(Exception):self.build()
    def test_manifest_wrong_url_fails_closed(self):
        data=json.loads(self.manifest.read_text());data['images']['apollo.webp']['source_url']='https://attacker.invalid/apollo.webp'
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(Exception):self.build()
    def test_refuse_replace_existing_bundle(self):
        self.out.write_bytes(b'original');os.chmod(self.out,0o600)
        with self.assertRaises(Exception):self.build()
        self.assertEqual(self.out.read_bytes(),b'original')
    def test_refuse_theme_symlink(self):
        self.theme.rename(self.p/'real.zip');self.theme.symlink_to(self.p/'real.zip')
        with self.assertRaises(Exception):self.build()
    def test_not_private_directory_fails(self):
        os.chmod(self.p,0o755)
        with self.assertRaises(Exception):self.build()
    def test_original_source_drift_fails(self):
        self.original['steps'][1]['themeData']={'resource':'url','url':'https://other.invalid/theme.zip'}
        self.blueprint.write_text(json.dumps(self.original))
        with self.assertRaises(Exception):self.build()

if __name__=='__main__':unittest.main()
