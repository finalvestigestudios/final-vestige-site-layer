"""Synthetic/offline adversarial unit tests. Does NOT certify actual WordPress."""
from __future__ import annotations
import copy
import hashlib
import importlib
import io
import json
from pathlib import Path
import re
import stat
import sys
import tempfile
import types
import unittest
import zipfile

from test_package_offline_playground_bundle import fixture
from package_offline_playground_bundle import MEDIA, package, sha

# These tests use a faithful lightweight launcher contract double, not a
# substitute for CI against launch_integrated_staging.py at the same Git SHA.
local = types.ModuleType('launch_integrated_staging')
local.DIGEST = re.compile(r'^[a-f0-9]{64}$')
class Hold(RuntimeError):pass
local.Hold = Hold
def require(ok,msg):
    if not ok:raise Hold(msg)
local.require = require
local.regular_private = lambda p,label: p.read_bytes() if p.is_file() and not p.is_symlink() and not p.stat().st_mode & 0o077 else (_ for _ in ()).throw(Hold(label+' not private'))
local.check_manifest = lambda p: {'media_manifest':json.loads(p.read_text())['purpose']}
local.check_axe = lambda *a: {'axe_executed':False}
local.check_runner = lambda *a: {'browser_runner_attested':True}
local.write_receipt = lambda *a: None
local.run = lambda *a: (_ for _ in ()).throw(Hold('real WordPress execution unavailable'))
sys.modules['launch_integrated_staging'] = local
import launch_pr543_offline_stage as admission

class TestAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name);self.root.chmod(0o700)
        self.bp,self.theme,self.images,self.manifest=fixture()
        (self.root/'media').mkdir(mode=0o700)
        def private(name,data):
            f=self.root/name
            f.write_bytes(data if isinstance(data,bytes) else data.encode());f.chmod(0o600)
            return f
        self.original=private('original.json',json.dumps(self.bp))
        self.theme_path=private('assembler.zip',self.theme)
        self.media_manifest=private('manifest.json',json.dumps(self.manifest))
        for name,data in self.images.items():private('media/'+name,data)
        self.bundle=self.root/'stage.zip'
        package(self.original,self.theme_path,self.root/'media',self.media_manifest,sha(self.theme),sha(self.original.read_bytes()),self.bundle)
        self.bundle_hash=sha(self.bundle.read_bytes())
        self.theme_hash=sha(self.theme)
        self.source_hash=sha(json.dumps(self.bp,sort_keys=True,separators=(',', ':'),ensure_ascii=False).encode())

    def admit(self, **options):
        return admission.admit_bundle(options.get('path',self.bundle),options.get('sha',self.bundle_hash),
                                     options.get('manifest',self.media_manifest),options.get('theme_sha',self.theme_hash),options.get('source_sha',self.source_hash))

    def rewrite(self, fn):
        with zipfile.ZipFile(self.bundle) as z:
            members={n:z.read(n) for n in z.namelist()}
        fn(members)
        with zipfile.ZipFile(self.bundle,'w') as z:
            for n,data in members.items():z.writestr(n,data)
        self.bundle.chmod(0o600)
        self.bundle_hash=sha(self.bundle.read_bytes())

    def test_valid_private_bundle_preflight_passes_without_wordpress(self):
        got=self.admit()
        self.assertEqual(got['status'],'PRIVATE_OFFLINE_BUNDLE_PREFLIGHT_PASSED_NOT_WORDPRESS_EXECUTED')
        self.assertFalse(got['wordpress_rendered']);self.assertFalse(got['image_rights_cleared'])
        self.assertEqual(got['media_sha256']['nypl.jpg'],sha(self.images['nypl.jpg']))

    def test_wrong_pinned_bundle_sha_fails(self):
        with self.assertRaisesRegex(Hold,'SHA-256'):
            self.admit(sha='0'*64)

    def test_invalid_theme_approval_sha_fails(self):
        with self.assertRaisesRegex(ValueError,'Assembler ZIP'):
            self.admit(theme_sha='0'*64)

    def test_tampered_original_image_rejected_even_with_new_zip_hash(self):
        self.rewrite(lambda m:m.__setitem__('assets/nypl.jpg',m['assets/nypl.jpg'][:-1]+b'!'))
        with self.assertRaisesRegex(ValueError,'byte identity mismatch'):
            self.admit()

    def test_malicious_extra_file_fails(self):
        self.rewrite(lambda m:m.__setitem__('secrets.txt',b'bad'))
        with self.assertRaisesRegex(Hold,'member'):
            self.admit()

    def test_missing_media_fails(self):
        self.rewrite(lambda m:m.pop('assets/apollo.webp'))
        with self.assertRaisesRegex(Hold,'member'):
            self.admit()

    def test_foreign_bundled_resource_fails(self):
        def altered(m):
            bp=json.loads(m['blueprint.json'])
            bp['steps'][1]['themeData']['path']='/assets/foreign.zip'
            m['blueprint.json']=json.dumps(bp).encode()
        self.rewrite(altered)
        with self.assertRaisesRegex(Hold,'Assembler bundled'):
            self.admit()

    def test_unauthorized_php_mutation_rejected(self):
        def altered(m):
            bp=json.loads(m['blueprint.json'])
            bp['steps'][-1]['code']=bp['steps'][-1]['code'].replace('wp_slash($raw)','$raw')
            m['blueprint.json']=json.dumps(bp,indent=2).encode()+b'\n'
        self.rewrite(altered)
        changed=copy.deepcopy(self.bp)
        changed['steps'][-1]['code']=changed['steps'][-1]['code'].replace('wp_slash($raw)','$raw')
        new_fingerprint=sha(json.dumps(changed,sort_keys=True,separators=(',', ':'),ensure_ascii=False).encode())
        with self.assertRaisesRegex(ValueError,'post-save integrity'):
            self.admit(source_sha=new_fingerprint)

    def test_gutenberg_source_cannot_be_changed_silently(self):
        def altered(m):
            bp=json.loads(m['blueprint.json'])
            bp['steps'][3]['data']+=' unauthorized'
            m['blueprint.json']=json.dumps(bp,indent=2).encode()+b'\n'
        self.rewrite(altered)
        with self.assertRaisesRegex(Hold,'original source differs'):
            self.admit()

    def test_missing_approved_original_source_sha_fails(self):
        with self.assertRaisesRegex(Hold,'original source semantic'):
            self.admit(source_sha='not-a-sha')

    def test_duplicate_member_fails_closed(self):
        with zipfile.ZipFile(self.bundle,'a') as z:z.writestr('blueprint.json',b'{}')
        self.bundle.chmod(0o600)
        self.bundle_hash=sha(self.bundle.read_bytes())
        with self.assertRaisesRegex(Hold,'member'):
            self.admit()

    def test_symlink_bundle_rejected(self):
        link=self.root/'linked.zip';link.symlink_to(self.bundle)
        with self.assertRaisesRegex(Hold,'private'):
            self.admit(path=link)

    def test_invalid_manifest_origin_fails(self):
        m=copy.deepcopy(self.manifest);m['images']['apollo.webp']['source_url']='https://evil.test/x'
        self.media_manifest.write_text(json.dumps(m));self.media_manifest.chmod(0o600)
        with self.assertRaisesRegex(ValueError,'byte identity mismatch'):
            self.admit()

if __name__ == '__main__': unittest.main(verbosity=2)
