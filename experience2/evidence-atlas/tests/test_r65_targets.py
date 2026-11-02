"""R65: ensure six NASA evidence link fixes are present in distributed plugin."""
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_full_staging_r65 import build

class R65Tests(unittest.TestCase):
    def test_staging_contains_scoped_source_target_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);manifest=build(folder)
            self.assertEqual(manifest['schema'],'fv.apollo.r65.wp-triplet.v1')
            self.assertFalse(manifest['wordpress_installed'])
            self.assertFalse(manifest['browser_axe_verified'])
            self.assertEqual(manifest['media_rights_unreviewed'],6)
            self.assertEqual(manifest['geographic_pins'],0)
            text=(folder/'fv-ex2-apollo-suite/apollo-suite.css').read_text()
            self.assertIn('.fv-ex2-apollo-suite .fva-card__external',text)
            self.assertIn('min-height:44px',text)
            self.assertIn('outline:3px solid #e5c487',text)
            php=(folder/'fv-ex2-apollo-suite/fv-ex2-apollo-suite.php').read_text()
            self.assertIn('0.0.66-staging',php)
    def test_staging_does_not_mutate_source(self):
        css=Path(__file__).resolve().parents[1]/'integration/apollo-suite.css'
        original=css.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:build(Path(tmp))
        self.assertEqual(original,css.read_bytes())

if __name__=='__main__':unittest.main()
