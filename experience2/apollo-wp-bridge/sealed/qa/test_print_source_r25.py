"""Source custody failure, media nonreuse and print-only acceptance gates."""
from __future__ import annotations
import copy
from pathlib import Path
import json
import tempfile
import unittest
from print_source_transcript_r25 import build_print_transcript, PrintCustodyHold, CASEFILE

class PrintLedgerR25(unittest.TestCase):
    def test_six_source_provenance_and_hold(self):
        html,css,receipt=build_print_transcript()
        self.assertEqual(receipt['records'],6)
        self.assertEqual(receipt['catalog_label_holds'],1)
        self.assertEqual(receipt['atlas_pins'],0)
        self.assertEqual(receipt['images_embedded'],0)
        self.assertEqual(html.count('data-r25-print-record='),6)
        self.assertEqual(html.count('LINK ONLY — IMAGE REUSE NOT CLEARED'),6)
        self.assertEqual(html.count('href="https://www.nasa.gov/image-'),6)
        self.assertIn('S67-19766',html)
        self.assertIn('S66-30236',html)
        self.assertIn('@media print',css)
        self.assertIn('#fv-ex2-apollo-document > :not(#fv-ex2-print-transcript)',css)
        for dangerous in ('<img','<script','<iframe','_wpnonce','admin-ajax','data-lat=','data-lon='):
            self.assertNotIn(dangerous,html.lower())

    def _mutate(self,mutator):
        original=json.loads((CASEFILE/'records.json').read_text(encoding='utf-8'))
        mutated=copy.deepcopy(original)
        mutator(mutated)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'records.json').write_text(json.dumps(mutated),encoding='utf-8')
            with self.assertRaises((PrintCustodyHold,ValueError,AssertionError)):
                build_print_transcript(casefile=root)

    def test_wrong_nasa_source_url_refused(self):
        self._mutate(lambda r:r['records'][0].update(image_url='https://fake.test/portrait'))

    def test_original_casefile_date_drift_refused(self):
        self._mutate(lambda r:r['records'][3].update(source_date='27 Jan 1967'))

    def test_image_reuse_cleared_without_authority_refused(self):
        self._mutate(lambda r:r['records'][2].update(rights='cleared_for_commercial_reuse'))

    def test_unreviewed_catalog_substitution_refused(self):
        self._mutate(lambda r:r['records'][0].update(source_id='NASA S66-30236'))

    def test_missing_nasa_media_policy_refused(self):
        self._mutate(lambda r:r.update(rights_policy='https://example.org/license'))

if __name__=='__main__':unittest.main()
