"""Repository test: no fabricated source; all changes exact and reversible."""
import unittest
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import catalog_semantics as r176

class TestR176(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=HERE.parent
        cls.authentic = cls.root / 'apollo-r174' / 'research-desk-provenance-candidate-UNPUBLISHED.html'
        if cls.authentic.exists(): cls.source=cls.authentic.read_text(encoding='utf-8')
        else: cls.source=None

    def test_exact_repo_source_and_reversibility(self):
        if self.source is None: self.skipTest('Full repository checkout required; never accept fixture as authentic')
        result, audit=r176.integrate(self.source)
        old, _=r176.r175_rewrite(self.source)
        self.assertEqual(result.replace(r176.R176,r176.R175,1),old)
        self.assertEqual(audit['source_r174_git_blob'],r176.PINNED_BLOB)
        self.assertEqual(audit['original_links'],14)
        self.assertTrue('Catalog identification not verified.' in result)
        self.assertTrue('NASA crew-training photograph. <p' in result)
        self.assertTrue(audit['status']=='BUILT_NOT_INSTALLED')

    def test_source_drift_hold(self):
        self.assertRaisesRegex(ValueError, 'STAGING HOLD',r176.integrate,'a different HTML page')

    def test_no_change_to_links_or_script_in_template(self):
        self.assertNotIn('<a ',r176.R176)
        self.assertNotIn('<script',r176.R176)
        self.assertNotIn('onclick=',r176.R176)
        self.assertEqual(r176.R176.count('<p'),1)
        self.assertEqual(r176.R176.count('</p>'),1)
        self.assertEqual(r176.R176.count('data-fvx-r175-catalog-review'),1)

    def test_no_css_dependent_whitespace(self):
        self.assertIn('photograph. <p',r176.R176)
        self.assertIn('<strong>Catalog identification not verified.</strong> ',r176.R176)
        self.assertIn('does not confirm',r176.R176)

if __name__ == '__main__':
    unittest.main(verbosity=2)
