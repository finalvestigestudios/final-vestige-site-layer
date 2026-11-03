"""R64 source-custody triplet and no-release tests."""
import hashlib
import json
import os
import subprocess
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_full_staging_r64 as stage
from test_desk_profiles_r52 import EXPECTED,blob

class StageR64Tests(unittest.TestCase):
    def test_exact_three_plugins(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)
            manifest=stage.build(output)
            self.assertEqual(manifest['release'],'STAGING_HOLD')
            self.assertFalse(manifest['wordpress_installed'])
            self.assertEqual(manifest['media_rights_unreviewed'],6)
            self.assertEqual(manifest['geographic_pins'],0)
            self.assertEqual(manifest['embedded_images'],0)
            self.assertEqual(len(manifest['plugin_directories']),3)
            self.assertEqual(manifest['active_desk_profile'],'r84-chronology-certainty')
            self.assertEqual(len(manifest['files']),4+len(EXPECTED['r84-chronology-certainty'])+2)
            for relative,sha in EXPECTED['r84-chronology-certainty'].items():
                self.assertEqual(blob((output/'fv-ex2-research-desk'/relative).read_bytes()),sha)
            for filename,hash_ in manifest['files'].items():
                self.assertEqual(hashlib.sha256((output/filename).read_bytes()).hexdigest(),hash_)
            self.assertIn('0.0.66-staging',(output/'fv-ex2-apollo-suite/fv-ex2-apollo-suite.php').read_text())
            style=(output/'fv-ex2-apollo-suite/apollo-suite.css').read_text()
            self.assertIn('.fva-guide a',style)
            self.assertIn('.fva-footer a',style)
            self.assertIn('min-height:44px',style)
            self.assertIn('attr(href)',style)
            # Exercise the actual triplet bytes with the original PHP WordPress
            # API simulator. This is deliberately NOT a WordPress core test.
            env=dict(os.environ,
                FV_R59_DESK_ROOT=str(output/'fv-ex2-research-desk'),
                FV_R59_ATLAS_ROOT=str(output/'fv-ex2-evidence-atlas'))
            for mode in ('nested','top-level','not-allowed','non-singular'):
                probe=stage.HERE/'tests/php_real_cohost_r59.php'
                process=subprocess.run(['php',str(probe),mode],env=env,
                    capture_output=True,text=True,check=True)
                info=json.loads(process.stdout)
                self.assertTrue(info['active_r84_pinned'])
                self.assertTrue(info['built_atlas_pinned'])
                self.assertTrue(info['suite_rendered'])
                self.assertEqual(info['desk_records'],6)
                self.assertEqual(info['atlas_records'],6)
                self.assertTrue(info['no_embedded_media'])
    def test_source_files_pinned_to_current_r84_profile(self):
        for path,sha in EXPECTED['r84-chronology-certainty'].items():
            self.assertEqual(blob((stage.DESK/path).read_bytes()),sha)

if __name__=='__main__': unittest.main()
