"""R73: printable NASA rights custody is complete even with six CLOSED native details."""
from __future__ import annotations
from pathlib import Path
import html, re, sys, tempfile, unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_atlas as atlas


class PrintRightsCustody(unittest.TestCase):
    def test_six_complete_independent_print_proofs(self):
        ledger = atlas.validate_custody()
        audit = atlas.validate_rights_audit(ledger)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            one = atlas.build_rights_matrix_r71(out)
            raw = (out / 'apollo-r71-media-rights-STAGING-ONLY.html').read_bytes()
            two = atlas.build_rights_matrix_r71(out)
            self.assertEqual(one, two)
            self.assertEqual(raw, (out / 'apollo-r71-media-rights-STAGING-ONLY.html').read_bytes())
            document = raw.decode()
        proofs = re.findall(r'<div class="fva-r73-print-proof" data-r73-print-proof>(.*?)</div>', document, re.S)
        self.assertEqual(len(proofs), 6)
        self.assertEqual(document.count('data-r71-rights-row'), 6)
        self.assertEqual(document.count('Individual photo review outstanding'), 12)  # six screen + six print
        self.assertIn('.fva-r71-rights .fva-r73-print-proof{display:block!important}', document)
        self.assertIn('.fva-r71-rights details{display:none!important}', document)
        self.assertNotIn('<img ', document)
        self.assertNotIn('data-geo-edge=', document)
        for source, rights, proof in zip(ledger['records'], audit['records'], proofs):
            with self.subTest(record=source['id']):
                for field in ('date_label', 'catalog', 'photo_role', 'photo_url'):
                    self.assertIn(html.escape(str(source[field]), quote=True), proof)
                for field in ('page_last_updated',):
                    self.assertIn(html.escape(str(rights[field]), quote=True), proof)
                self.assertIn('no human', proof)
                self.assertIn('license granted', proof)
                self.assertIn('<strong>Credit:</strong>', proof)
                self.assertIn('<strong>Producing center:</strong>', proof)
                self.assertIn('<strong>Catalog verification:</strong>', proof)
                self.assertIn('data-r73-print-url', proof)

    def test_print_is_not_a_rights_clearance(self):
        with tempfile.TemporaryDirectory() as td:
            build = atlas.build_rights_matrix_r71(Path(td))
        self.assertEqual(build['photo_reuse_clearances'], 0)
        self.assertEqual(build['photograph_binaries'], 0)
        self.assertFalse(build['actual_wordpress_tested'])


if __name__ == '__main__':
    unittest.main()
