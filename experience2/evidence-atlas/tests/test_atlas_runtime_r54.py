#!/usr/bin/env python3
"""R54 exact Atlas PHP/CSS/JS/template admission, failure/recovery, and staging scope."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / 'tests/php_atlas_runtime_r54_probe.php'
PINS = {
    'final-vestige-ex2-evidence-atlas.php': 'f7b41a7aafb92208afce661b9f6f1c7171f4e13b',
    'atlas.css': 'ad64e7967f84856672fd8a229a61370d7a865227',
    'atlas.js': '23212093d354917e403a5a9dbd9dca6b0eb8ca28',
}
TEMPLATE_SHA = '5d76b85ab62feb0c9a3a5733cd0718d8f0f4fe8f820edb1d61f57e499d0fdb73'

def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

class AtlasRuntimeIntegrity(unittest.TestCase):
    def test_reviewed_php_css_js_pins_are_exact(self):
        for name, sha in PINS.items():
            self.assertEqual(blob((ROOT/name).read_bytes()), sha, name)

    def test_fail_closed_enqueuing_and_shortcodes(self):
        src = (ROOT/'integration/fv-ex2-apollo-suite.php').read_text()
        self.assertIn('function fv_ex2_apollo_verified_atlas(): ?string', src)
        self.assertIn('fv_ex2_apollo_verified_atlas() === null', src)
        self.assertIn('hash_file(\'sha256\', $template)', src)
        self.assertIn('0.0.56-staging', src)
        for forbidden in ('wp_insert_post(', 'update_option(', 'wp_update_post(', 'wp_remote_get(', 'file_get_contents(\'http'):
            self.assertNotIn(forbidden, src)
        self.assertIn('function fv_ex2_apollo_suite_fallback()', src)

    def test_php_syntax(self):
        for file in (ROOT/'integration/fv-ex2-apollo-suite.php', PROBE):
            result = subprocess.run(['php','-l',str(file)], capture_output=True,text=True,check=True)
            self.assertIn('No syntax errors detected',result.stdout)

    def test_full_bundle_acceptance_and_adversarial_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)/'atlas-plugin'
            (src/'assets').mkdir(parents=True)
            (src/'templates').mkdir()
            shutil.copyfile(ROOT/'final-vestige-ex2-evidence-atlas.php', src/'final-vestige-ex2-evidence-atlas.php')
            for name in ('atlas.css','atlas.js'):
                shutil.copyfile(ROOT/name,src/'assets'/name)
            fixture = os.environ.get('FV_R54_ATLAS_TEMPLATE_FIXTURE')
            if fixture:
                template = Path(fixture).read_bytes()
            else:
                try:
                    import sys
                    sys.path.insert(0,str(ROOT))
                    import build_wordpress_stage
                    with tempfile.TemporaryDirectory() as built:
                        build_wordpress_stage.build(Path(built))
                        template = (Path(built)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_bytes()
                except FileNotFoundError:
                    self.skipTest('Reviewed R37 custody crosswalk absent in standalone archive; supply exact template explicitly')
            self.assertEqual(hashlib.sha256(template).hexdigest(),TEMPLATE_SHA,'Exact reviewed artifact only')
            (src/'templates/atlas-fragment.html').write_bytes(template)
            env = dict(os.environ,FV_R54_ATLAS_PLUGIN_ROOT=str(src))
            result = subprocess.run(['php',str(PROBE)],capture_output=True,text=True,env=env,check=True)
            data = json.loads(result.stdout)
            self.assertEqual(len(data),14)
            self.assertTrue(all(data.values()),data)

if __name__=='__main__': unittest.main()
