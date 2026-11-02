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
    'final-vestige-ex2-evidence-atlas.php': '8f5a21b42cbd00acf0e390aaeb22e55f3bb216f8',
    'atlas.css': '079f2ef9785184a098ec7686f5018a474181031b',
    'atlas.js': '1bfde47e00abc522f5af0b125c5668f8c7617256',
}
TEMPLATE_SHA = '33c72ea1b64d5b3b93dd949da9143debea6bda1cc1143402a20e9e1abcaef82a'

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
        self.assertIn('0.0.66-staging', src)
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
