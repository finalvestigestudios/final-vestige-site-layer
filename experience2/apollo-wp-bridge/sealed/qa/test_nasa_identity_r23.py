"""R23: adversarial catalog-identity witness and live component source accountability.

Cannot resolve the PR158 S67-19766 label from a NASA URL match alone.
"""
from __future__ import annotations
import hashlib, json, tempfile, unittest
from pathlib import Path
from qa.research_desk_crosswalk import (WITNESS, IDENTITY_WITNESS, IDENTITY_WITNESS_SHA256,
    CrosswalkHold, build_crosswalk, verify_nasa_identity, verify_witness)
from qa.source_concordance import CASEFILE, build_concordance

class NASAIdentityR23(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=json.loads((CASEFILE/'records.json').read_text())['records']
        cls.pr158=verify_witness(cls.rows)
        cls.html,cls.receipt=build_crosswalk(cls.rows)

    def test_01_pinned_witness_and_original_url(self):
        self.assertEqual(hashlib.sha256(IDENTITY_WITNESS.read_bytes()).hexdigest(), IDENTITY_WITNESS_SHA256)
        d=verify_nasa_identity(self.pr158)
        self.assertEqual(d['source_page']['url'], self.rows[0]['image_url'])
        self.assertEqual(d['decision'],'HOLD_UNTIL_FIRST_PARTY_IDENTIFIER_EQUIVALENCE_CONFIRMED')
        self.assertFalse(d['source_page']['id_equivalence_verified'])

    def test_02_one_unresolved_identifier_is_preserved_not_renamed(self):
        self.assertEqual(sum(not r['catalog_identifier_label_match'] for r in self.pr158),1)
        self.assertEqual(self.pr158[0]['research_desk_catalog_label'],'NASA S67-19766')
        self.assertEqual(self.pr158[0]['canonical_catalog_label'],'Apollo 1 crew training portrait')
        self.assertEqual(self.receipt['source_identifier_verified'],False)
        self.assertEqual(self.receipt['identity_adjudication'],'HOLD_UNRESOLVED_PR158_S67_19766')

    def test_03_separate_nasa_portrait_never_promoted_to_same_photo(self):
        d=verify_nasa_identity(self.pr158)
        self.assertEqual(d['comparison_page']['nasa_identifier'],'S66-30236')
        self.assertFalse(d['comparison_page']['is_same_photo_as_casefile_claim_01'])
        self.assertTrue(d['comparison_page']['not_a_substitute_identifier'])
        self.assertNotIn('S66-30236', self.rows[0]['source_id'])

    def test_04_no_images_js_geo_or_new_external_site(self):
        self.assertEqual(self.html.count('data-catalog-review="hold"'),1)
        self.assertEqual(self.html.count('id="fv-ex2-catalog-identity"'),1)
        self.assertEqual(self.html.count('<details><summary>Compare NASA references'),1)
        for url in (self.rows[0]['image_url'], 'https://www.nasa.gov/image-article/apollo-1-prime-crew-portrait/'):
            self.assertIn(url,self.html)
        for token in ('<img','<script','<iframe','data-lat=','data-lon=','onclick='):
            self.assertNotIn(token,self.html)
        self.assertIn('first-party NASA',self.html)
        self.assertIn('not a live NASA change monitor',self.html)
        self.assertIn('not the original linked image',self.html)

    def test_05_reject_witness_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'witness.json'
            p.write_bytes(IDENTITY_WITNESS.read_bytes().replace(b'NOT_CLEARED',b'CLEARED'))
            with self.assertRaisesRegex(CrosswalkHold,'witness mutated'):
                verify_nasa_identity(self.pr158,p)

    def test_06_reject_label_promotion(self):
        rows=[dict(r) for r in self.pr158];rows[0]['catalog_identifier_label_match']=True
        with self.assertRaises(CrosswalkHold):verify_nasa_identity(rows)
        rows=[dict(r) for r in self.pr158];rows[0]['canonical_catalog_label']='NASA S67-19766'
        with self.assertRaises(CrosswalkHold):verify_nasa_identity(rows)

    def test_07_reject_alternate_photo_substitution(self):
        rows=[dict(r) for r in self.pr158];rows[0]['nasa_catalog_url']='https://www.nasa.gov/image-article/apollo-1-prime-crew-portrait/'
        with self.assertRaises(CrosswalkHold):verify_nasa_identity(rows)

    def test_08_no_js_and_named_nested_disclosures(self):
        self.assertIn('aria-labelledby="fv-ex2-catalog-identity-title"',self.html)
        self.assertIn('<summary>Compare NASA references',self.html)
        self.assertIn('href="#source-01"',self.html)
        self.assertIn('href="#stage-01"',self.html)
        main,css,receipt=build_concordance()
        self.assertIn('fv-ex2-catalog-identity',main)
        self.assertIn('@container(max-width:700px)',css)
        self.assertEqual(receipt['research_desk_crosswalk']['nasa_identity_witness_sha256'],IDENTITY_WITNESS_SHA256)
        self.assertEqual(receipt['photos_embedded'],0)

    def test_09_deterministic_html_and_receipt(self):
        self.assertEqual(build_crosswalk(self.rows),build_crosswalk(self.rows))

if __name__=='__main__':unittest.main()
