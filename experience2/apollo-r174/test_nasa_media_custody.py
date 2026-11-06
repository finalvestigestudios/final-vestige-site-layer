"""Release-guard and fixture tests for the *source-controlled* R174 provenance overlay.

Run from repository root: python -m unittest discover -s experience2/apollo-r174 -p 'test_*.py' -v
The test loads the R173 real HTML committed on the parent branch. No remote HTTP or CMS calls.
"""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DIR=Path(__file__).resolve().parent
sys.path.insert(0,str(DIR))
from nasa_media_custody import annotate,git_blob,EXPECTED_BLOB
SOURCE=ROOT/'experience2/apollo-r173/research-desk-source-custody.html'
LEDGER=DIR/'nasa_media_custody.json'

class MediaCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=SOURCE.read_text(encoding='utf-8')
        cls.data=json.loads(LEDGER.read_text(encoding='utf-8'))
    def test_exact_parent_blob_and_six_records(self):
        self.assertEqual(git_blob(self.src),EXPECTED_BLOB)
        text,r=annotate(self.src,self.data)
        self.assertTrue(r['strict_roundtrip'])
        self.assertEqual(text.count('data-fvx-r174-media-custody'),6)
        self.assertEqual(r['unmatched_catalog_ids'],1)
        self.assertFalse(r['paid_media_cleared'])
    def test_ambiguity_prominently_qualified(self):
        text,_=annotate(self.src,self.data)
        self.assertIn('Catalog ID not established on linked NASA page.',text)
        self.assertIn('POST-FIRE PHYSICAL AFTERMATH DOCUMENTATION',text)
    def test_nasa_photo_url_tampering_held(self):
        src=self.src.replace('https://www.nasa.gov/image-detail/apollo-1-crew-honored/','https://example.test/fake-photo/',1)
        with self.assertRaisesRegex(ValueError,'source Git blob'):
            annotate(src,self.data)
        with self.assertRaisesRegex(ValueError,'NASA link'):
            annotate(src,self.data,fixture=True)
    def test_duplicate_overlay_fails(self):
        text,_=annotate(self.src,self.data)
        with self.assertRaisesRegex(ValueError,'duplicate'):
            annotate(text,self.data,fixture=True)
    def test_six_records_and_order_required(self):
        changed=copy.deepcopy(self.data)
        changed['records'][0]['record']='07'
        with self.assertRaisesRegex(ValueError,'six ordered'):
            annotate(self.src,changed)
    def test_all_original_anchors_preserved(self):
        text,receipt=annotate(self.src,self.data)
        self.assertTrue(receipt['all_original_links_preserved'])
        self.assertEqual(receipt['new_links'],0)
        self.assertEqual(receipt['new_scripts'],0)
        self.assertIn('Read original investigation',text)
    def test_source_roles_not_replaced(self):
        changed=self.src.replace('data-fvx-r173-source-role=\"01\"','data-fvx-r173-deleted=\"01\"',1)
        with self.assertRaisesRegex(ValueError,'source role'):
            annotate(changed,self.data,fixture=True)

if __name__=='__main__': unittest.main()
