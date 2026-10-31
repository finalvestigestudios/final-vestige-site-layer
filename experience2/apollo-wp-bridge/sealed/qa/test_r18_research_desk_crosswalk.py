"""R18: independent PR158 Research Desk cross-lane source custody gate."""
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
import json
import unittest
from research_desk_crosswalk import CrosswalkHold, WITNESS, build_crosswalk, verify_witness
from source_concordance import CASEFILE, build_concordance, build_context_index

class ResearchDeskCrosswalk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=json.loads((CASEFILE/'records.json').read_text(encoding='utf-8'))['records']

    def test_six_urls_but_not_six_catalog_labels(self):
        rows=verify_witness(self.records)
        self.assertEqual(len(rows),6)
        self.assertTrue(all(row['same_nasa_catalog_url'] for row in rows))
        self.assertEqual(sum(not row['catalog_identifier_label_match'] for row in rows),1)
        self.assertEqual(rows[0]['catalog_identifier_review'], 'HOLD_IDENTIFIERS_DIFFER_REVIEW_ORIGINAL_NASA_RECORD')
        self.assertEqual(rows[0]['research_desk_catalog_label'],'NASA S67-19766')
        self.assertEqual(rows[0]['canonical_catalog_label'],'Apollo 1 crew training portrait')
        self.assertTrue(all(row['media_reuse_rights']=='NOT_CLEARED' for row in rows))
        self.assertTrue(all(row['editorial_findings_equivalence']=='NOT_ASSERTED' for row in rows))
        self.assertTrue(all(row['recorded_geolocation']=='NONE' for row in rows))

    def test_native_no_js_disclosure_and_qa_html(self):
        html,css,receipt=build_concordance()
        self.assertIn('<details class="fv-ex2-crosswalk"',html)
        self.assertIn('CATALOG IDENTIFIER REVIEW NEEDED',html)
        self.assertEqual(html.count('data-crosswalk-id='),6)
        self.assertEqual(html.count('data-crosswalk-review="hold"'),1)
        self.assertEqual(receipt['research_desk_crosswalk']['catalog_label_review_holds'],1)
        self.assertIn('@container(max-width:800px)',css)
        self.assertNotIn('<img',html)
        self.assertNotIn('<script',html)

    def test_context_export_retains_identifier_hold(self):
        obj=json.loads(build_context_index())
        self.assertEqual(len(obj['records']),6)
        self.assertEqual(obj['records'][0]['pr158_research_desk']['catalog_identifier_label_match'],False)
        self.assertTrue(obj['records'][1]['pr158_research_desk']['catalog_identifier_label_match'])
        self.assertEqual(obj['media_rights'],'HOLD_PER_ITEM_REVIEW')
        self.assertEqual(obj['geographic_coordinates_assigned'],0)

    def test_catalog_url_mutation_fails_closed(self):
        rows=deepcopy(self.records)
        rows[2]['image_url']='https://www.nasa.gov/image-detail/amf-s66-58038-incorrect/'
        with self.assertRaisesRegex(CrosswalkHold,'source URL differs'):
            verify_witness(rows)

    def test_record_ordinal_mutation_fails_closed(self):
        with TemporaryDirectory() as tmp:
            data=json.loads(WITNESS.read_text())
            data['rows'][0]['casefile_id']='02'
            fp=Path(tmp)/'witness.json'; fp.write_text(json.dumps(data))
            with self.assertRaisesRegex(CrosswalkHold,'ordinals'):
                verify_witness(self.records,fp)

    def test_staging_blob_pin_mutation_fails_closed(self):
        with TemporaryDirectory() as tmp:
            data=json.loads(WITNESS.read_text())
            data['ledger_git_blob_sha1']='0'*40
            fp=Path(tmp)/'witness.json';fp.write_text(json.dumps(data))
            with self.assertRaisesRegex(CrosswalkHold,'identity drifted'):
                verify_witness(self.records,fp)

    def test_ledger_label_mutation_fails_closed_pending_review(self):
        with TemporaryDirectory() as tmp:
            data=json.loads(WITNESS.read_text())
            data['rows'][0]['ledger_catalog_label']='NASA Apollo 1 crew training portrait'
            fp=Path(tmp)/'witness.json';fp.write_text(json.dumps(data))
            with self.assertRaisesRegex(CrosswalkHold,'identifier-label mismatch'):
                verify_witness(self.records,fp)

    def test_adversarial_label_html_escaped(self):
        with TemporaryDirectory() as tmp:
            data=json.loads(WITNESS.read_text())
            data['rows'][2]['ledger_title']='<img src=x onerror=alert(1)>'
            fp=Path(tmp)/'witness.json';fp.write_text(json.dumps(data))
            html,_=build_crosswalk(self.records,fp)
            self.assertNotIn('<img',html)
            self.assertIn('&lt;img',html)

if __name__=='__main__':unittest.main()
