"""Editorial and accessibility regression checks for optional read-only custody concordance."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from source_concordance import build_concordance, ConcordanceHold, CASEFILE, GENERATED

class SourceConcordance(unittest.TestCase):
    def test_six_native_details_and_external_nasa_citations(self):
        html,css,receipt=build_concordance()
        self.assertEqual(receipt['record_count'],6)
        self.assertEqual(html.count('data-concordance-record='),6)
        self.assertEqual(html.count('<details><summary>'),6)
        self.assertEqual(html.count('<a href="#stage-'),6)
        self.assertEqual(html.count('<a href="https://www.nasa.gov/image-detail/'),6)
        self.assertNotIn('<img',html)
        self.assertNotIn('<iframe',html)
        self.assertNotIn('<script',html)
        self.assertIn('2017 tribute exhibits are not accident footage',html)
        self.assertIn(':focus-visible',css)
        self.assertEqual(receipt['rights'],'HOLD_PER_ITEM_REVIEW')

    def test_deterministic_bytes(self):
        self.assertEqual(build_concordance(),build_concordance())

    def mutate(self,change):
        with tempfile.TemporaryDirectory() as tmp:
            cp=Path(tmp)/'casefile'; gp=Path(tmp)/'generated'
            cp.mkdir();gp.mkdir()
            data=json.loads((CASEFILE/'records.json').read_text())
            change(data)
            (cp/'records.json').write_text(json.dumps(data))
            shutil.copyfile(GENERATED/'fragment.html',gp/'fragment.html')
            with self.assertRaises(ConcordanceHold):build_concordance(cp,gp)

    def test_rejects_2017_reclassified_as_1967(self):
        self.mutate(lambda d:d['records'][3].update(source_date='27 Jan 1967'))

    def test_rejects_1966_reclassified_as_1967(self):
        self.mutate(lambda d:d['records'][2].update(source_date='Jan 1967'))

    def test_rejects_photo_rights_escalation(self):
        self.mutate(lambda d:d['records'][0].update(rights='NASA_permission_granted'))

    def test_rejects_fake_nasa_domain(self):
        self.mutate(lambda d:d['records'][1].update(image_url='https://nasa.gov.evil.example/image-detail/amf-s67-15717/'))

    def test_rejects_missing_claim_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            gp=Path(tmp); frag=(GENERATED/'fragment.html').read_text().replace('id="stage-04"','id="stage-unlinked"')
            (gp/'fragment.html').write_text(frag)
            with self.assertRaisesRegex(ConcordanceHold,'Unresolved claim/source route'):
                build_concordance(CASEFILE,gp)

    def test_provenance_preserves_all_metadata(self):
        html,_,receipt=build_concordance()
        rows=json.loads((CASEFILE/'records.json').read_text())['records']
        for row in rows:
            self.assertIn(row['title'],html)
            self.assertIn(row['source_date'],html)
            self.assertIn(row['image_url'],html)
        self.assertEqual(receipt['photos_embedded'],0)
        self.assertEqual(receipt['geographic_pins'],0)

if __name__=='__main__':unittest.main()
